"""
fix_vinbus_gtfs.py — Fix VinBus pseudo-GTFS data quality issues.

Issues addressed
----------------
1. 🔴 16 routes missing frequencies (incl. OCP1/OCP2 critical for Ocean Park)
2. 🟡 Blank start_time for route 11008
3. 🟡 Mixed time format — 132 rows seconds-int, 27 rows HH:MM → normalize to HH:MM:SS
4. 🟢 2 duplicate route_short_name (43, E11)
5. 🟢 Dirty fare/headway_offpeak columns — free-text mix → extract numeric

Output: data/raw/vinbus_pseudo_gtfs_fixed/ (drop-in replacement, safe to merge)
"""
from __future__ import annotations

import io
import re
import shutil
import sys
from pathlib import Path

import pandas as pd

# Force UTF-8 output on Windows so box/emoji chars don't crash cp1252
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ── Paths ──────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "data" / "raw" / "vinbus_pseudo_gtfs"
DST_DIR = REPO_ROOT / "data" / "raw" / "vinbus_pseudo_gtfs_fixed"

# Files we rewrite; others are copied verbatim
REWRITE_FILES = {"frequencies.txt", "routes.txt"}

# ── Internal shuttle headway defaults (seconds) ────────────────────────────────
# Applied when routes.txt has no headway_peak_min either.
INTERNAL_SHUTTLE_HEADWAY = {
    # Ocean Park internal — compact estate, ~10-min circuit
    "101014": 600,  # OCP1
    "101023": 600,  # OCP2
    # Ocean City express — slightly longer corridor
    "101011": 900,  # OCT1
    "101012": 900,  # OCT2
    # Smart City internal
    "101015": 600,  # SMC1
    # Hạ Long Xanh — long-distance scheduled service; conservative
    "101024": 1800,  # HLX1
    "101025": 1800,  # HLX2
}

# TC/exhibition routes — seasonal/special; we skip imputation and emit a warning
TC_ROUTE_IDS = {"13010", "13023", "13008", "13005", "13019", "13020", "13009"}

# Conservative urban default for any remaining missing routes
DEFAULT_HEADWAY_SECS = 900  # 15 min

# ── Time conversion helpers ────────────────────────────────────────────────────

def _secs_to_hms(secs: int | float) -> str:
    """Convert total seconds since midnight to HH:MM:SS (may be >24h for GTFS)."""
    secs = int(round(secs))
    h, rem = divmod(secs, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def _normalize_time(val) -> str | None:
    """
    Accept any of the three formats found in the feed and return HH:MM:SS.

    Formats:
      - int/float  → seconds since midnight  (18000 → '05:00:00')
      - 'HH:MM'   → append ':00'             ('05:00' → '05:00:00')
      - 'HH:MM:SS' → pass through             ('05:00:00' → '05:00:00')
      - blank / NaN → None
    """
    if pd.isna(val):
        return None
    s = str(val).strip()
    if not s:
        return None

    # Purely numeric → treat as seconds
    try:
        return _secs_to_hms(float(s))
    except ValueError:
        pass

    # HH:MM or HH:MM:SS
    parts = s.split(":")
    if len(parts) == 2:
        try:
            h, m = int(parts[0]), int(parts[1])
            return f"{h:02d}:{m:02d}:00"
        except ValueError:
            pass
    if len(parts) == 3:
        try:
            h, m, sec = int(parts[0]), int(parts[1]), int(parts[2])
            return f"{h:02d}:{m:02d}:{sec:02d}"
        except ValueError:
            pass

    return None  # unparseable


def _extract_numeric(val) -> float | None:
    """Extract the first integer/decimal number from a free-text string."""
    if pd.isna(val):
        return None
    s = str(val).replace(",", ".")  # handle Vietnamese decimal comma e.g. "0,000"
    m = re.search(r"\d+(?:\.\d+)?", s)
    if m:
        return float(m.group())
    return None


# ── Fix #3 + #2: normalize time columns & patch blank start_time ───────────────

def fix_frequencies(freq: pd.DataFrame) -> pd.DataFrame:
    freq = freq.copy()

    # Normalize start_time and end_time to HH:MM:SS
    for col in ("start_time", "end_time"):
        freq[col] = freq[col].apply(_normalize_time)

    # Fix #2: route 11008 had blank start_time → default to 05:00:00
    mask_11008 = freq["route_id"].astype(str) == "11008"
    if freq.loc[mask_11008, "start_time"].isna().any():
        freq.loc[mask_11008 & freq["start_time"].isna(), "start_time"] = "05:00:00"
        print("  [FIX #2] route 11008: blank start_time → '05:00:00'")

    # Ensure headway_secs is numeric
    freq["headway_secs"] = pd.to_numeric(freq["headway_secs"], errors="coerce")

    return freq


# ── Fix #1: impute missing frequencies ────────────────────────────────────────

def impute_missing_frequencies(
    freq: pd.DataFrame,
    routes: pd.DataFrame,
) -> tuple[pd.DataFrame, list[str]]:
    """
    For every route in routes.txt that has no row in frequencies.txt,
    generate a frequency row using headway_peak_min from routes.txt
    (or INTERNAL_SHUTTLE_HEADWAY / DEFAULT_HEADWAY_SECS as fallback).

    TC/exhibition routes (13xxx special service) are logged and skipped.

    Returns (updated_freq_df, list_of_warning_strings).
    """
    warnings: list[str] = []
    freq = freq.copy()

    existing_ids = set(freq["route_id"].astype(str))
    routes_ids = set(routes["route_id"].astype(str))
    missing_ids = routes_ids - existing_ids

    if not missing_ids:
        print("  [INFO] No missing frequencies — nothing to impute.")
        return freq, warnings

    new_rows: list[dict] = []
    skipped: list[str] = []

    for rid in sorted(missing_ids):
        if rid in TC_ROUTE_IDS:
            skipped.append(rid)
            continue

        row = routes[routes["route_id"].astype(str) == rid].iloc[0]
        short_name = str(row.get("route_short_name", rid)).strip()

        # Determine headway (seconds)
        headway_secs = None
        peak_min = _extract_numeric(row.get("headway_peak_min"))
        if peak_min and peak_min > 0:
            headway_secs = int(round(peak_min * 60))
        elif rid in INTERNAL_SHUTTLE_HEADWAY:
            headway_secs = INTERNAL_SHUTTLE_HEADWAY[rid]
        else:
            headway_secs = DEFAULT_HEADWAY_SECS

        # Determine time window
        first_trip = _normalize_time(row.get("first_trip")) or "05:00:00"
        last_trip  = _normalize_time(row.get("last_trip"))  or "23:00:00"

        new_rows.append({
            "route_id":     rid,
            "start_time":   first_trip,
            "end_time":     last_trip,
            "headway_secs": headway_secs,
            "exact_times":  0,
        })
        headway_min = headway_secs // 60
        source = (
            "INTERNAL_SHUTTLE_DEFAULT"
            if rid in INTERNAL_SHUTTLE_HEADWAY and not peak_min
            else ("routes.headway_peak_min" if peak_min else "DEFAULT_15min")
        )
        msg = (
            f"  [FIX #1] Imputed  route_id={rid:>7} ({short_name:>8}): "
            f"headway={headway_min}min  window={first_trip}–{last_trip}  src={source}"
        )
        print(msg)

    if skipped:
        w = f"  [SKIP]  TC/special routes skipped (no headway data): {', '.join(sorted(skipped))}"
        print(w)
        warnings.append(w)

    if new_rows:
        new_df = pd.DataFrame(new_rows)
        freq = pd.concat([freq, new_df], ignore_index=True)
        print(f"  [FIX #1] Total rows imputed: {len(new_rows)}")

    return freq, warnings


# ── Fix #4: deduplicate route_short_name ──────────────────────────────────────

def fix_duplicate_short_names(routes: pd.DataFrame) -> pd.DataFrame:
    routes = routes.copy()

    # Identify duplicates
    dup_mask = routes.duplicated(subset=["route_short_name"], keep=False)
    dup_names = routes.loc[dup_mask, "route_short_name"].unique()

    for name in dup_names:
        group = routes[routes["route_short_name"] == name].copy()
        # Sort by route_id — keep the "primary" (lower/older ID) untouched,
        # rename the secondary with suffix 'B'
        group_sorted = group.sort_values("route_id")
        secondary_ids = group_sorted.iloc[1:]["route_id"].tolist()
        for rid in secondary_ids:
            new_name = str(name).strip() + "B"
            routes.loc[routes["route_id"] == rid, "route_short_name"] = new_name
            print(
                f"  [FIX #4] Duplicate route_short_name '{name}' → "
                f"route_id {rid} renamed to '{new_name}'"
            )

    return routes


# ── Fix #6: clean dirty numeric columns ───────────────────────────────────────

def fix_dirty_columns(routes: pd.DataFrame) -> pd.DataFrame:
    routes = routes.copy()

    numeric_cols = ["headway_peak_min", "headway_offpeak_min", "fare_vnd"]
    for col in numeric_cols:
        if col not in routes.columns:
            continue
        original = routes[col].copy()
        routes[col] = routes[col].apply(_extract_numeric)
        changed = (routes[col] != original).sum()
        if changed:
            print(f"  [FIX #6] Cleaned column '{col}': {changed} cells normalized")

    return routes


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> int:
    print("=" * 70)
    print("fix_vinbus_gtfs.py — VinBus GTFS Data Quality Fix")
    print("=" * 70)

    # Load
    freq_path   = SRC_DIR / "frequencies.txt"
    routes_path = SRC_DIR / "routes.txt"

    print(f"\n[LOAD] {freq_path}")
    freq = pd.read_csv(freq_path, dtype=str, keep_default_na=False)
    # Replace literal whitespace-only strings with NaN for numeric detection
    freq.replace(r"^\s*$", pd.NA, regex=True, inplace=True)

    print(f"[LOAD] {routes_path}")
    routes = pd.read_csv(routes_path, dtype=str, keep_default_na=False)
    routes.replace(r"^\s*$", pd.NA, regex=True, inplace=True)

    print(f"       Loaded {len(freq)} frequency rows, {len(routes)} route rows\n")

    # ── Apply fixes ────────────────────────────────────────────────────────────
    print("── Fix #3 + #2: Normalize time formats ──")
    freq = fix_frequencies(freq)

    print("\n── Fix #1: Impute missing frequencies ──")
    freq, _warnings = impute_missing_frequencies(freq, routes)

    print("\n── Fix #6: Clean dirty numeric columns (routes.txt) ──")
    routes = fix_dirty_columns(routes)

    print("\n── Fix #4: Deduplicate route_short_name ──")
    routes = fix_duplicate_short_names(routes)

    # ── Write output ───────────────────────────────────────────────────────────
    DST_DIR.mkdir(parents=True, exist_ok=True)

    # Copy files we don't rewrite
    for fname in SRC_DIR.iterdir():
        if fname.name not in REWRITE_FILES:
            shutil.copy2(fname, DST_DIR / fname.name)
            print(f"\n[COPY]  {fname.name}")

    # Write fixed frequencies
    freq_out = DST_DIR / "frequencies.txt"
    freq.to_csv(freq_out, index=False)
    print(f"[WRITE] frequencies.txt  ({len(freq)} rows)")

    # Write fixed routes
    routes_out = DST_DIR / "routes.txt"
    routes.to_csv(routes_out, index=False)
    print(f"[WRITE] routes.txt       ({len(routes)} rows)")

    # ── Validation summary ─────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)

    # Time format check
    bad_time = freq[~freq["start_time"].str.match(r"^\d{2}:\d{2}:\d{2}$", na=False)]
    if bad_time.empty:
        print("✅ All start_time values are HH:MM:SS")
    else:
        print(f"❌ {len(bad_time)} rows still have non-standard start_time:")
        print(bad_time[["route_id", "start_time"]].to_string(index=False))

    bad_end = freq[~freq["end_time"].str.match(r"^\d{2}:\d{2}:\d{2}$", na=False)]
    if bad_end.empty:
        print("✅ All end_time values are HH:MM:SS")
    else:
        print(f"❌ {len(bad_end)} rows still have non-standard end_time:")
        print(bad_end[["route_id", "end_time"]].to_string(index=False))

    # Route 11008
    row_11008 = freq[freq["route_id"].astype(str) == "11008"]
    if not row_11008.empty and row_11008.iloc[0]["start_time"] == "05:00:00":
        print("✅ Route 11008 start_time = 05:00:00")
    else:
        print(f"❌ Route 11008 start_time unexpected: {row_11008[['route_id','start_time']].to_string(index=False)}")

    # OCP1/OCP2 present
    for rid, name in [("101014", "OCP1"), ("101023", "OCP2")]:
        if not freq[freq["route_id"].astype(str) == rid].empty:
            hw = freq[freq["route_id"].astype(str) == rid].iloc[0]["headway_secs"]
            print(f"✅ {name} ({rid}) in frequencies — headway={hw}s")
        else:
            print(f"❌ {name} ({rid}) STILL missing from frequencies")

    # Duplicate short names
    dup = routes[routes.duplicated(subset=["route_short_name"], keep=False)]
    if dup.empty:
        print("✅ No duplicate route_short_name")
    else:
        print(f"❌ {len(dup)} rows still have duplicate route_short_name:")
        print(dup[["route_id", "route_short_name"]].to_string(index=False))

    # Frequency coverage
    freq_ids = set(freq["route_id"].astype(str))
    route_ids = set(routes["route_id"].astype(str))
    tc_missing = TC_ROUTE_IDS & route_ids
    non_tc_missing = (route_ids - freq_ids) - TC_ROUTE_IDS
    if non_tc_missing:
        print(f"❌ {len(non_tc_missing)} non-TC routes still missing frequencies: {non_tc_missing}")
    else:
        print(f"✅ All non-TC routes have frequencies ({len(tc_missing)} TC routes intentionally skipped)")

    print(f"\n📁 Output written to: {DST_DIR}")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
