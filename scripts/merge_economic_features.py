"""Merge OSM economic features (landuse/office/bank) into the active POI layer.

Reads:
  data/interim/merged_pois.gpkg         — current primary POI layer (161 POIs)
  data/interim/landuse_poi_synthetic.gpkg — output of fetch_osm_landuse.py

Produces:
  data/interim/merged_pois_economic.gpkg — augmented POI layer (replaces merged_pois.gpkg
      when confirmed; kept separate until spot-checked)
  outputs/validation/economic_merge_summary.md

Deduplication: synthetic POIs within 30 m of an existing POI in the same domain
are dropped. This prevents double-counting office buildings already in merged_pois.

Run after fetch_osm_landuse.py:
  python scripts/merge_economic_features.py [--promote]

Use --promote to overwrite data/interim/merged_pois.gpkg with the augmented layer.
Without --promote, only writes merged_pois_economic.gpkg (safe default).
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


DEDUP_DISTANCE_M = 30.0
SUMMARY_PATH = Path("outputs/validation/economic_merge_summary.md")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-pois", type=Path, default=Path("data/interim/merged_pois.gpkg"))
    parser.add_argument("--econ-pois", type=Path, default=Path("data/interim/landuse_poi_synthetic.gpkg"))
    parser.add_argument("--output", type=Path, default=Path("data/interim/merged_pois_economic.gpkg"))
    parser.add_argument("--promote", action="store_true",
                        help="Also overwrite data/interim/merged_pois.gpkg with the augmented layer.")
    parser.add_argument("--dedup-distance-m", type=float, default=DEDUP_DISTANCE_M)
    args = parser.parse_args()

    import geopandas as gpd
    import pandas as pd
    from src.accessibility_inputs import classify_poi_opportunity_domain

    if not args.base_pois.exists():
        print(f"Error: {args.base_pois} not found. Run merge_poi_sources.py first.")
        return 1
    if not args.econ_pois.exists():
        print(f"Error: {args.econ_pois} not found. Run fetch_osm_landuse.py first.")
        return 1

    base = gpd.read_file(args.base_pois)
    econ = gpd.read_file(args.econ_pois)

    print(f"Base POIs: {len(base)}")
    print(f"Economic candidates: {len(econ)}")

    utm = base.estimate_utm_crs()
    base_m = base.to_crs(utm)
    econ_m = econ.to_crs(utm)

    # Deduplicate: drop synthetic POIs within dedup_distance_m of any existing POI
    econ_m["_eidx"] = range(len(econ_m))
    base_buf = base_m.copy()
    base_buf["geometry"] = base_m.geometry.buffer(args.dedup_distance_m)
    joined = gpd.sjoin(econ_m[["_eidx", "geometry"]], base_buf[["geometry"]], how="left", predicate="within")
    dup_idx = set(joined[joined["index_right"].notna()]["_eidx"].astype(int).unique())
    fresh = econ_m[~econ_m["_eidx"].isin(dup_idx)].copy()
    n_dropped = len(econ_m) - len(fresh)
    print(f"Dropped {n_dropped} duplicates (within {args.dedup_distance_m}m of existing POI)")
    print(f"Fresh economic POIs to add: {len(fresh)}")

    # Union of columns: keep base columns AND tag columns from synthetic POIs
    # (e.g. office, landuse) that the classifier relies on. Dropping them would
    # silently send office=* lecture halls to the generic commercial fallback.
    fresh_4326 = fresh.to_crs("EPSG:4326")
    helper_cols = {"_eidx", "_econ_domain", "_econ_weight", "index_right"}
    base_cols = [c for c in base.columns if c != "geometry"]
    fresh_cols = [c for c in fresh_4326.columns if c != "geometry" and c not in helper_cols]
    all_cols = list(dict.fromkeys(base_cols + fresh_cols))  # ordered union
    for col in all_cols:
        if col not in base.columns:
            base[col] = None
        if col not in fresh_4326.columns:
            fresh_4326[col] = None

    merged = pd.concat(
        [base[all_cols + ["geometry"]], fresh_4326[all_cols + ["geometry"]]],
        ignore_index=True,
    )
    merged_gdf = gpd.GeoDataFrame(merged, geometry="geometry", crs="EPSG:4326")

    # Synthetic economic POIs have no OSM id; assign unique synthetic ids so the
    # downstream building-footprint join (which dedups on `id`) does not collapse
    # all NaN-id rows into one and drop the building_area_m2 column.
    if "id" in merged_gdf.columns:
        missing_id = merged_gdf["id"].isna()
        n_missing = int(missing_id.sum())
        if n_missing:
            merged_gdf.loc[missing_id, "id"] = [
                f"econ_synth_{i}" for i in range(n_missing)
            ]
            print(f"Assigned synthetic ids to {n_missing} economic POIs")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    merged_gdf.to_file(args.output, driver="GPKG")
    print(f"Wrote {args.output} ({len(merged_gdf)} total POIs)")

    if args.promote:
        merged_gdf.to_file(args.base_pois, driver="GPKG")
        print(f"Promoted: overwrote {args.base_pois}")

    # Domain distribution check
    results = [classify_poi_opportunity_domain(row) for _, row in merged_gdf.iterrows()]
    from collections import Counter
    domain_counts = Counter(r[0] for r in results)

    # Summary report
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Economic Feature Merge Summary",
        "",
        f"Base POIs (merged_pois.gpkg): {len(base)}",
        f"Economic candidates from OSM landuse/office: {len(econ)}",
        f"Dropped as duplicates ({args.dedup_distance_m}m threshold): {n_dropped}",
        f"Fresh economic POIs added: {len(fresh)}",
        f"**Total POIs after merge: {len(merged_gdf)}**",
        "",
        "## Domain distribution after merge",
        "",
        "| Domain | Count |",
        "|---|---|",
    ]
    for domain, count in sorted(domain_counts.items(), key=lambda x: -x[1]):
        lines.append(f"| {domain} | {count} |")
    lines += [
        "",
        "## Source breakdown of added economic POIs",
        "",
        "| Source | Count |",
        "|---|---|",
    ]
    src_counts = fresh_4326["source"].value_counts() if "source" in fresh_4326.columns else {}
    for src, cnt in (src_counts.items() if hasattr(src_counts, "items") else []):
        lines.append(f"| {src} | {cnt} |")
    lines += [
        "",
        "## Next steps",
        "",
        "- Spot-check `spot_check_priority=medium` rows (landuse/office synthetic POIs)",
        "- Run `python scripts/build_accessibility_inputs.py --mode network --gtfs-status baseline_limited "
        "--pois data/interim/merged_pois_economic.gpkg` to regenerate accessibility inputs",
        "- Compare domain distribution and MAI_B before/after",
        "- If satisfied, rerun with `--promote` to make this the default layer",
    ]
    SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {SUMMARY_PATH}")
    print(f"\nDomain distribution: {dict(domain_counts)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
