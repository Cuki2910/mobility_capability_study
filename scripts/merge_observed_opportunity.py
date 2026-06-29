"""Merge observed opportunity magnitudes onto the active POI layer.

Input CSV columns:
name, lat, lon, obs_jobs, obs_enrollment, obs_beds, obs_retail_gla_m2,
obs_source, obs_source_url
"""
from __future__ import annotations

import argparse
from pathlib import Path

import geopandas as gpd
import pandas as pd


OBS_COLUMNS = [
    "obs_jobs",
    "obs_enrollment",
    "obs_beds",
    "obs_retail_gla_m2",
    "obs_source",
    "obs_source_url",
]


def _read_observed(csv_path: Path) -> gpd.GeoDataFrame:
    df = pd.read_csv(csv_path)
    required = {"name", "lat", "lon"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Observed CSV missing columns: {sorted(missing)}")
    for col in OBS_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA
    return gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["lon"], df["lat"]),
        crs="EPSG:4326",
    )


def merge_observed_opportunity(
    pois_path: Path,
    observed_csv: Path,
    output: Path,
    match_distance_m: float = 30.0,
) -> gpd.GeoDataFrame:
    pois = gpd.read_file(pois_path)
    observed = _read_observed(observed_csv)
    metric_crs = pois.estimate_utm_crs()
    pois_m = pois.to_crs(metric_crs).copy()
    pois_m["_poi_idx"] = range(len(pois_m))
    obs_m = observed.to_crs(metric_crs).copy()
    obs_m["_obs_idx"] = range(len(obs_m))

    for col in OBS_COLUMNS:
        if col not in pois_m.columns:
            pois_m[col] = pd.NA

    joined = gpd.sjoin_nearest(
        pois_m,
        obs_m[["_obs_idx", *OBS_COLUMNS, "geometry"]],
        how="left",
        max_distance=match_distance_m,
        distance_col="_obs_distance_m",
    )
    joined = joined.sort_values("_obs_distance_m").drop_duplicates(subset="_poi_idx")
    joined = joined.set_index("_poi_idx").reindex(range(len(pois_m)))

    out = pois.copy()
    for col in OBS_COLUMNS:
        right = f"{col}_right"
        values = joined[right] if right in joined.columns else joined.get(col)
        if values is not None:
            out[col] = values.combine_first(out[col]) if col in out.columns else values

    output.parent.mkdir(parents=True, exist_ok=True)
    out.to_file(output, driver="GPKG")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pois", type=Path, default=Path("data/interim/merged_pois.gpkg"))
    parser.add_argument("--observed", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("data/interim/merged_pois_observed.gpkg"))
    parser.add_argument("--match-distance-m", type=float, default=30.0)
    args = parser.parse_args()
    out = merge_observed_opportunity(args.pois, args.observed, args.output, args.match_distance_m)
    print(f"Wrote {args.output} ({len(out)} POIs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
