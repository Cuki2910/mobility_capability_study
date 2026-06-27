"""
Merge OSM POIs and Overture Places into a unified POI layer with source labels.

Logic:
  - OSM + Overture within 30m → source = "both"       (high confidence)
  - OSM-only                  → source = "osm_only"    (spot-check priority: low)
  - Overture-only             → source = "overture_only" (spot-check priority: high)

Run (after fetch_overture_pois.py):
  python scripts/merge_poi_sources.py

Outputs:
  data/interim/merged_pois.gpkg
  outputs/poi_merge_summary.md
"""
from __future__ import annotations

import argparse
from pathlib import Path

import geopandas as gpd
import pandas as pd


MATCH_DISTANCE_M = 30.0


def merge_poi_sources(
    osm_path: Path,
    overture_path: Path,
    match_distance_m: float = MATCH_DISTANCE_M,
) -> gpd.GeoDataFrame:
    osm = gpd.read_file(osm_path)
    overture = gpd.read_file(overture_path)

    # Work in metric CRS for distance matching
    utm = osm.estimate_utm_crs()
    osm_m = osm.to_crs(utm).copy()
    overture_m = overture.to_crs(utm).copy()

    osm_m["_osm_idx"] = range(len(osm_m))
    overture_m["_ov_idx"] = range(len(overture_m))

    # Spatial join: Overture points within match_distance_m of any OSM point
    osm_buffered = osm_m.copy()
    osm_buffered["geometry"] = osm_m.geometry.buffer(match_distance_m)

    joined = gpd.sjoin(overture_m, osm_buffered[["_osm_idx", "geometry"]], how="left", predicate="within")
    matched_ov_idx = set(joined[joined["_osm_idx"].notna()]["_ov_idx"].unique())
    matched_osm_idx = set(joined[joined["_osm_idx"].notna()]["_osm_idx"].astype(int).unique())

    # Build merged output
    rows = []

    # OSM POIs matched with Overture — use OSM geometry as primary
    for _, row in osm_m.iterrows():
        idx = int(row["_osm_idx"])
        if idx in matched_osm_idx:
            rows.append({**row.drop("_osm_idx").to_dict(), "source": "both", "spot_check_priority": "low"})
        else:
            rows.append({**row.drop("_osm_idx").to_dict(), "source": "osm_only", "spot_check_priority": "low"})

    # Overture-only POIs (not matched to any OSM point)
    for _, row in overture_m.iterrows():
        if int(row["_ov_idx"]) not in matched_ov_idx:
            rows.append({**row.drop("_ov_idx").to_dict(), "source": "overture_only", "spot_check_priority": "high"})

    merged = gpd.GeoDataFrame(rows, crs=utm).to_crs("EPSG:4326")
    return merged


def write_summary(merged: gpd.GeoDataFrame, osm_count: int, overture_count: int, output: Path) -> None:
    counts = merged["source"].value_counts()
    both        = int(counts.get("both", 0))
    osm_only    = int(counts.get("osm_only", 0))
    ov_only     = int(counts.get("overture_only", 0))
    total       = len(merged)

    lines = [
        "# POI Source Merge Summary",
        "",
        f"OSM input POIs:      {osm_count}",
        f"Overture input POIs: {overture_count}",
        f"Match distance:      {MATCH_DISTANCE_M} m",
        "",
        "## Source Agreement",
        "",
        "| Source label     | Count | % of merged |",
        "|---|---:|---:|",
        f"| both (matched)   | {both}    | {both/total:.1%} |",
        f"| osm_only         | {osm_only} | {osm_only/total:.1%} |",
        f"| overture_only    | {ov_only}  | {ov_only/total:.1%} |",
        f"| **Total**        | **{total}** | — |",
        "",
        "## Interpretation",
        "",
        "- `both` POIs have two-source confirmation — highest confidence.",
        "- `osm_only` POIs are in OSM but not Overture — may be very local or recently added.",
        "- `overture_only` POIs are new candidates not in current OSM data — spot-check these first.",
        "",
        "## Recommended Next Step",
        "",
        f"Spot-check the {ov_only} `overture_only` POIs to determine how many are real, relevant,",
        "and missing from the current OSM NAI calculation. If a meaningful share are confirmed,",
        "re-run build_accessibility_inputs.py with merged_pois.gpkg as the POI source.",
    ]
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--osm",      type=Path, default=Path("data/interim/pilot_pois.gpkg"))
    parser.add_argument("--overture", type=Path, default=Path("data/raw/overture_pois.gpkg"))
    parser.add_argument("--output",   type=Path, default=Path("data/interim/merged_pois.gpkg"))
    parser.add_argument("--summary",  type=Path, default=Path("outputs/poi_merge_summary.md"))
    args = parser.parse_args()

    if not args.osm.exists():
        raise FileNotFoundError(f"OSM POIs not found: {args.osm}")
    if not args.overture.exists():
        raise FileNotFoundError(
            f"Overture POIs not found: {args.overture}\n"
            "Run scripts/fetch_overture_pois.py first (requires internet)."
        )

    osm      = gpd.read_file(args.osm)
    overture = gpd.read_file(args.overture)

    merged = merge_poi_sources(args.osm, args.overture)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    merged.to_file(args.output, driver="GPKG")
    write_summary(merged, len(osm), len(overture), args.summary)

    counts = merged["source"].value_counts()
    print(f"Wrote {len(merged)} merged POIs to {args.output}")
    print(f"  both:           {counts.get('both', 0)}")
    print(f"  osm_only:       {counts.get('osm_only', 0)}")
    print(f"  overture_only:  {counts.get('overture_only', 0)}")
    print(f"  Summary:        {args.summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
