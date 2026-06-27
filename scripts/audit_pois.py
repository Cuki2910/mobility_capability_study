"""Audit OSM POIs used for NAI and create a spot-check template."""
from __future__ import annotations

import argparse
from urllib.parse import quote_plus
from pathlib import Path

import pandas as pd

NAI_CATEGORIES = {
    "school": ("amenity", "school"),
    "healthcare": ("amenity", ["hospital", "clinic", "pharmacy"]),
    "retail": ("shop", None),
    "park": ("leisure", "park"),
}


def repair_mojibake(value):
    """Repair common UTF-8-as-Latin-1 text when possible."""
    if not isinstance(value, str):
        return value
    try:
        repaired = value.encode("latin1").decode("utf-8")
    except UnicodeError:
        return value
    return repaired if any(marker in value for marker in ("Ãƒ", "Ã¡Âº", "Ã¡Â»", "Ã„")) else value


def poi_category(row) -> str:
    for category, (column, values) in NAI_CATEGORIES.items():
        value = row.get(column)
        if values is None and pd.notna(value):
            return category
        if isinstance(values, list) and value in values:
            return category
        if value == values:
            return category
    return "other"


def audit_pois(pois_path: Path, sample_per_category: int = 5):
    import geopandas as gpd

    pois = gpd.read_file(pois_path).to_crs(epsg=4326)
    for column in [c for c in pois.columns if pd.api.types.is_object_dtype(pois[c])]:
        pois[column] = pois[column].map(repair_mojibake)
    pois["nai_category"] = pois.apply(poi_category, axis=1)
    centroids = pois.to_crs(epsg=3857).geometry.centroid.to_crs(epsg=4326)
    pois["lat"] = centroids.y
    pois["lon"] = centroids.x
    pois["osm_url"] = pois.apply(lambda row: f"https://www.openstreetmap.org/{row.get('element', 'node')}/{row.get('id')}", axis=1)
    pois["google_maps_search_url"] = pois.apply(
        lambda row: "https://www.google.com/maps/search/?api=1&query="
        + quote_plus(f"{row.get('name') or row.get('name:vi') or row.get('nai_category')} {row['lat']},{row['lon']}"),
        axis=1,
    )
    name_col = "name" if "name" in pois.columns else None
    geom_key = pois.geometry.to_wkb().map(bytes.hex)
    name_key = pois[name_col].fillna("") if name_col else pd.Series([""] * len(pois))
    pois["duplicate_name_geometry"] = (name_key + "|" + geom_key).duplicated(keep=False)

    counts = pois.groupby("nai_category").size().rename("count").reset_index()
    for category in NAI_CATEGORIES:
        if category not in set(counts["nai_category"]):
            counts = pd.concat([counts, pd.DataFrame([{"nai_category": category, "count": 0}])], ignore_index=True)
    counts["empty_category_flag"] = counts["count"] == 0

    duplicates = pois.loc[pois["duplicate_name_geometry"], [c for c in [name_col, "nai_category"] if c] + ["geometry"]]
    samples = []
    for category, group in pois.groupby("nai_category"):
        sample = group.head(sample_per_category).copy()
        sample["spot_check_status"] = "unchecked"
        sample["spot_check_options"] = "confirmed|missing_in_osm|misclassified|duplicate"
        sample["spot_check_notes"] = ""
        samples.append(sample)
    spot_check = pd.concat(samples, ignore_index=True) if samples else pois.head(0)
    return counts.sort_values("nai_category"), duplicates, spot_check


def merge_existing_spot_checks(spot_check: pd.DataFrame, existing_path: Path) -> pd.DataFrame:
    """Preserve manual/web spot-check statuses when regenerating the sample."""
    if not existing_path.exists():
        return spot_check
    existing = pd.read_csv(existing_path)
    if "osm_url" not in existing.columns or "osm_url" not in spot_check.columns:
        return spot_check
    keep = ["osm_url", "spot_check_status", "spot_check_notes"]
    existing = existing[[c for c in keep if c in existing.columns]].drop_duplicates("osm_url")
    merged = spot_check.drop(columns=["spot_check_status", "spot_check_notes"], errors="ignore").merge(existing, on="osm_url", how="left")
    merged["spot_check_status"] = merged["spot_check_status"].fillna("unchecked")
    merged["spot_check_notes"] = merged["spot_check_notes"].fillna("")
    if "spot_check_options" not in merged.columns:
        merged["spot_check_options"] = "confirmed|missing_in_osm|misclassified|duplicate"
    return merged


def write_markdown(counts: pd.DataFrame, duplicates: pd.DataFrame, spot_check: pd.DataFrame, output: Path) -> None:
    completed = 0
    breakdown = {}
    if "spot_check_status" in spot_check.columns:
        status = spot_check["spot_check_status"].fillna("unchecked")
        completed = int((status != "unchecked").sum())
        breakdown = status.value_counts().to_dict()
    lines = ["# POI Audit", "", "## Category Counts", ""]
    lines += [f"- {row.nai_category}: {row.count} (empty={row.empty_category_flag})" for row in counts.itertuples(index=False)]
    lines += ["", "## Duplicate Name/Geometry", "", f"Duplicate rows: {len(duplicates)}"]
    lines += ["", "## Spot-Check Status", "", f"Completed rows: {completed}/{len(spot_check)}", f"Breakdown: {breakdown}"]
    if completed < 20:
        lines += ["", "## Caveat", "", "Manual/web spot-check remains required until at least 20 records are reviewed."]
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pois", type=Path, default=Path("data/interim/pilot_pois.gpkg"))
    parser.add_argument("--output-csv", type=Path, default=Path("outputs/poi_audit.csv"))
    parser.add_argument("--output-md", type=Path, default=Path("outputs/poi_audit.md"))
    parser.add_argument("--spot-check", type=Path, default=Path("data/interim/poi_spot_check.csv"))
    parser.add_argument("--sample-per-category", type=int, default=5)
    args = parser.parse_args()

    if not args.pois.exists():
        raise FileNotFoundError(f"Missing {args.pois}; run scripts/fetch_osm_data.py first")
    counts, duplicates, spot_check = audit_pois(args.pois, args.sample_per_category)
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    args.spot_check.parent.mkdir(parents=True, exist_ok=True)
    spot_check = merge_existing_spot_checks(spot_check, args.spot_check)
    counts.to_csv(args.output_csv, index=False)
    write_markdown(counts, duplicates, spot_check, args.output_md)
    spot_check.drop(columns="geometry", errors="ignore").to_csv(args.spot_check, index=False)
    print(f"Wrote {args.output_csv}, {args.output_md}, {args.spot_check}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
