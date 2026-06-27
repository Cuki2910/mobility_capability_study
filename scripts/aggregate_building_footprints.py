"""Aggregate building footprint count and area by analysis grid cell."""
from __future__ import annotations

import argparse
from pathlib import Path

import geopandas as gpd
import pandas as pd


def aggregate_buildings(grid_path: Path, buildings_path: Path, output: Path, cell_id_col: str = "cell_id") -> gpd.GeoDataFrame:
    if not grid_path.exists():
        raise FileNotFoundError(f"Missing grid file: {grid_path}")
    if not buildings_path.exists():
        raise FileNotFoundError(f"Missing building footprint file: {buildings_path}")

    grid = gpd.read_file(grid_path)
    buildings = gpd.read_file(buildings_path)
    if cell_id_col not in grid.columns:
        grid[cell_id_col] = range(len(grid))
    if buildings.crs != grid.crs:
        buildings = buildings.to_crs(grid.crs)

    metric_crs = grid.estimate_utm_crs()
    grid_m = grid.to_crs(metric_crs)
    buildings_m = buildings.to_crs(metric_crs)
    clipped = gpd.overlay(
        buildings_m[[col for col in buildings_m.columns if col != "geometry"] + ["geometry"]],
        grid_m[[cell_id_col, "geometry"]],
        how="intersection",
        keep_geom_type=False,
    )
    clipped["footprint_area_m2"] = clipped.geometry.area

    agg = clipped.groupby(cell_id_col).agg(
        building_count=("geometry", "count"),
        building_footprint_area_m2=("footprint_area_m2", "sum"),
    )
    confidence_cols = [c for c in clipped.columns if c.lower() in {"confidence", "confidence_score"}]
    if confidence_cols:
        agg["mean_building_confidence"] = clipped.groupby(cell_id_col)[confidence_cols[0]].mean()

    out = grid.merge(agg, on=cell_id_col, how="left")
    out["building_count"] = out["building_count"].fillna(0).astype(int)
    out["building_footprint_area_m2"] = out["building_footprint_area_m2"].fillna(0.0)
    out["has_building"] = out["building_count"] > 0
    output.parent.mkdir(parents=True, exist_ok=True)
    out.to_file(output, driver="GPKG")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--grid", type=Path, required=True, help="Analysis grid vector file with a cell_id column.")
    parser.add_argument("--buildings", type=Path, required=True, help="Building footprints vector file clipped to/near the study area.")
    parser.add_argument("--output", type=Path, default=Path("data/interim/grid_building_footprints.gpkg"))
    parser.add_argument("--cell-id-col", default="cell_id")
    args = parser.parse_args()

    out = aggregate_buildings(args.grid, args.buildings, args.output, args.cell_id_col)
    summary = pd.Series(
        {
            "grid_cells": len(out),
            "built_cells": int(out["has_building"].sum()),
            "built_cell_share": float(out["has_building"].mean()),
            "total_buildings": int(out["building_count"].sum()),
            "total_footprint_area_m2": float(out["building_footprint_area_m2"].sum()),
        }
    )
    summary_path = args.output.with_suffix(".summary.csv")
    summary.to_frame("value").to_csv(summary_path)
    print(f"Wrote {args.output} and {summary_path}")
    print(summary.to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
