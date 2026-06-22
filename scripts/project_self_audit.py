"""Generate a self-audit and critique report for the Ocean Park pilot."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _exists(path: str) -> bool:
    return Path(path).exists()


def count_completed_spot_checks(path: Path) -> tuple[int, int]:
    if not path.exists():
        return 0, 0
    df = pd.read_csv(path)
    if "spot_check_status" not in df.columns:
        return len(df), 0
    complete = int((df["spot_check_status"].fillna("unchecked") != "unchecked").sum())
    return len(df), complete


def motorcycle_status(path: Path) -> dict:
    if not path.exists():
        return {"rows": 0, "android_completed": 0, "has_android_column": False}
    df = pd.read_csv(path)
    android_cols = [c for c in df.columns if c in {"google_maps_android_minutes", "android_motorcycle_minutes"}]
    if not android_cols:
        return {"rows": len(df), "android_completed": 0, "has_android_column": False}
    completed = int(df[android_cols[0]].notna().sum())
    return {"rows": len(df), "android_completed": completed, "has_android_column": True}

def android_emulator_status(path: Path) -> dict:
    if not path.exists():
        return {"status_file": False, "installed": False, "motorcycle_mode_available": None}
    text = path.read_text(encoding="utf-8")
    return {
        "status_file": True,
        "installed": "Emulator boots" in text,
        "motorcycle_mode_available": False if "not currently provide a motorcycle-mode measurement" in text else None,
    }


def build_audit() -> dict:
    gtfs = _read_json(Path("data/interim/hanoi_gtfs_status.json"))
    pop = _read_json(Path("data/interim/population_proxy_resolution.json"))
    manifest = _read_json(Path("data/interim/pilot_data_manifest.json"))
    poi_total, poi_done = count_completed_spot_checks(Path("data/interim/poi_spot_check.csv"))
    moto = motorcycle_status(Path("outputs/validation/manual_motorcycle_validation_template.csv"))
    emulator = android_emulator_status(Path("outputs/validation/android_emulator_status.md"))

    summary = pd.read_csv("outputs/pilot_summary.csv", index_col=0)["value"].to_dict() if _exists("outputs/pilot_summary.csv") else {}
    vif = pd.read_csv("outputs/validation/vif_flags.csv") if _exists("outputs/validation/vif_flags.csv") else pd.DataFrame()
    high_vif = bool(vif["flag_high_vif"].any()) if not vif.empty and "flag_high_vif" in vif else None

    blockers = []
    warnings = []
    strengths = []

    if manifest.get("counts") and _exists("data/processed/pilot_metrics.csv"):
        strengths.append("End-to-end pilot pipeline has real OSM graph/POI/grid inputs and processed metrics.")
    if pop.get("resolution_source") == "raster_metadata" and pop.get("adequate_for_250m_pilot"):
        strengths.append("WorldPop raster is downloaded and resolution-verified against the 250m grid.")
    if high_vif is False:
        strengths.append("Current NAI/MAI/RAC VIF diagnostics are below threshold 5.")

    if gtfs.get("network_b_baseline_limited", True):
        blockers.append("Network B remains baseline-limited because current GTFS is missing or stale.")
    if poi_done < 20:
        blockers.append(f"POI manual spot-check incomplete: {poi_done}/{max(poi_total, 20)} records checked.")
    if moto.get("android_completed", 0) < 10:
        blockers.append(f"Android motorcycle validation incomplete: {moto.get('android_completed', 0)}/10 OD pairs measured.")
    if emulator.get("installed") and emulator.get("motorcycle_mode_available") is False:
        blockers.append("Android emulator is installed, but Google Maps on the AVD does not expose Motorcycle/Two-wheeler mode.")
    if pop.get("resolution_source") == "raster_metadata":
        warnings.append("Population raster is verified but not yet integrated into MAI magnitude weighting.")
    if summary.get("mean_SMCI_A", 0.0) == 0.0 or gtfs.get("network_b_baseline_limited", True):
        warnings.append("Scenario A interpretation is weak until Network B is current or explicitly reframed as no-baseline-transit.")

    return {
        "snapshot": {
            "grid_cells": int(summary.get("n_cells", manifest.get("counts", {}).get("grid_cells", 0)) or 0),
            "mean_SMCI_A": float(summary.get("mean_SMCI_A", 0.0) or 0.0),
            "mean_SMCI_B": float(summary.get("mean_SMCI_B", 0.0) or 0.0),
            "share_improved": float(summary.get("share_improved", 0.0) or 0.0),
            "gtfs_status": gtfs.get("status", "missing"),
            "poi_spot_checks": {"total": poi_total, "completed": poi_done},
            "motorcycle_android_checks": moto,
            "android_emulator": emulator,
            "population_resolution": pop,
            "high_vif": high_vif,
        },
        "strengths": strengths,
        "blockers": blockers,
        "warnings": warnings,
        "next_actions": [
            "Fill 20 POI spot-check rows using OSM/Google Maps links.",
            "Measure 10 Android motorcycle OD times and add google_maps_android_minutes.",
            "Either obtain current GTFS or reframe Scenario A as baseline-limited/no-current-GTFS.",
            "Integrate WorldPop raster into MAI magnitude weighting only if the paper needs population-weighted opportunity magnitudes.",
        ],
    }


def write_markdown(audit: dict, output: Path) -> None:
    lines = ["# Project Self-Audit", "", "## Snapshot", ""]
    for key, value in audit["snapshot"].items():
        lines.append(f"- {key}: {value}")
    for section in ("strengths", "blockers", "warnings", "next_actions"):
        title = section.replace("_", " ").title()
        lines += ["", f"## {title}", ""]
        lines += [f"- {item}" for item in audit[section]] or ["- None"]
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, default=Path("outputs/project_self_audit.json"))
    parser.add_argument("--md", type=Path, default=Path("outputs/project_self_audit.md"))
    args = parser.parse_args()

    audit = build_audit()
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    write_markdown(audit, args.md)
    print(json.dumps(audit, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
