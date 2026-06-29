"""Derive observed commercial GLA from POI-nearest building footprints.

obs_retail_gla_m2 = footprint_area_m2 * levels * usable_fraction
"""
from __future__ import annotations

import argparse
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd


COMMERCIAL_SHOPS = {
    "mall",
    "department_store",
    "supermarket",
    "convenience",
    "electronics",
    "computer",
    "mobile_phone",
    "houseware",
    "beauty",
}


def _to_num(value, default: float) -> float:
    val = pd.to_numeric(value, errors="coerce")
    if val is None or pd.isna(val) or float(val) <= 0:
        return default
    return float(val)


def derive_commercial_floorspace(
    pois_path: Path,
    buildings_path: Path,
    output: Path,
    usable_fraction: float = 0.7,
    match_distance_m: float = 25.0,
) -> gpd.GeoDataFrame:
    pois = gpd.read_file(pois_path)
    buildings = gpd.read_file(buildings_path)
    metric_crs = buildings.estimate_utm_crs()
    pois_m = pois.to_crs(metric_crs).copy()
    if "building_area_m2" in pois_m.columns:
        pois_m = pois_m.drop(columns=["building_area_m2"])
    bld_m = buildings.to_crs(metric_crs).copy()

    bld_m["building_area_m2"] = bld_m.geometry.area
    if "building:levels" not in bld_m.columns:
        bld_m["building:levels"] = np.nan
    if "levels" not in bld_m.columns:
        bld_m["levels"] = np.nan

    nearest = gpd.sjoin_nearest(
        pois_m,
        bld_m[["building_area_m2", "building:levels", "levels", "geometry"]],
        how="left",
        max_distance=match_distance_m,
        distance_col="_distance_m",
    )
    nearest = nearest[~nearest.index.duplicated(keep="first")].reindex(pois_m.index)

    out = pois.copy()
    shop = out.get("shop", pd.Series("", index=out.index)).fillna("").astype(str).str.lower()
    category = out.get("category", pd.Series("", index=out.index)).fillna("").astype(str).str.lower()
    commercial = shop.isin(COMMERCIAL_SHOPS) | (category == "retail")

    levels = []
    source = []
    for idx, row in nearest.iterrows():
        lvl = _to_num(row.get("building:levels"), np.nan)
        if pd.isna(lvl):
            lvl = _to_num(row.get("levels"), np.nan)
        if pd.isna(lvl):
            poi_shop = str(out.iloc[idx].get("shop", "") or "").lower()
            lvl = 3.0 if poi_shop == "mall" else 2.0
            source.append("observed_derived_OSM_levels_default")
        else:
            source.append("observed_derived_OSM_levels")
        levels.append(lvl)

    area = pd.to_numeric(nearest["building_area_m2"], errors="coerce").fillna(0.0)
    gla = area.to_numpy(dtype=float) * np.asarray(levels, dtype=float) * usable_fraction
    out["obs_retail_gla_m2"] = np.where(commercial & (gla > 0), gla, out.get("obs_retail_gla_m2", pd.NA))
    out["obs_source"] = np.where(commercial & (gla > 0), source, out.get("obs_source", pd.NA))
    out["obs_source_url"] = np.where(
        commercial & (gla > 0),
        "OSM building footprint/levels + 0.7 usable_fraction",
        out.get("obs_source_url", pd.NA),
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    out.to_file(output, driver="GPKG")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pois", type=Path, default=Path("data/interim/merged_pois.gpkg"))
    parser.add_argument("--buildings", type=Path, default=Path("data/raw/building_footprints.gpkg"))
    parser.add_argument("--output", type=Path, default=Path("data/interim/merged_pois_floorspace.gpkg"))
    parser.add_argument("--usable-fraction", type=float, default=0.7)
    parser.add_argument("--match-distance-m", type=float, default=25.0)
    args = parser.parse_args()
    out = derive_commercial_floorspace(
        args.pois, args.buildings, args.output, args.usable_fraction, args.match_distance_m
    )
    print(f"Wrote {args.output} ({len(out)} POIs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
