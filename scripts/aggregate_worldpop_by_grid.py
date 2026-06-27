"""
Aggregate WorldPop raster population counts by analysis grid cell.

Produces data/interim/grid_worldpop.csv with per-cell population statistics
for use as a population-weighted SMCI cross-check and MAI proxy validation.
Does NOT modify the MAI formula — see docs/decisions.md before changing that.

Run:
  python scripts/aggregate_worldpop_by_grid.py
  python scripts/aggregate_worldpop_by_grid.py --raster data/raw/worldpop/vnm_ppp_2020.tif
                                                --grid data/interim/pilot_grid.gpkg
                                                --output data/interim/grid_worldpop.csv
"""
from __future__ import annotations

import argparse
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.mask import mask as rasterio_mask
from shapely.geometry import mapping


def aggregate_worldpop_by_grid(
    raster_path: Path,
    grid_path: Path,
    cell_id_col: str = "cell_id",
) -> pd.DataFrame:
    """
    Extract and aggregate WorldPop raster pixels per grid cell.

    Returns a DataFrame with columns:
        cell_id, pop_sum, pop_mean, pop_density_per_km2, n_valid_pixels
    """
    grid = gpd.read_file(grid_path)
    if cell_id_col not in grid.columns:
        raise ValueError(f"Grid missing column '{cell_id_col}'. Available: {list(grid.columns)}")

    rows = []
    with rasterio.open(raster_path) as src:
        raster_crs = src.crs
        nodata = src.nodata if src.nodata is not None else -99999.0

        grid_reproj = grid.to_crs(raster_crs)

        # Cell area in km² (reproject to metric CRS for accurate area)
        grid_metric = grid.to_crs(grid.estimate_utm_crs())
        cell_areas_km2 = grid_metric.geometry.area / 1e6

        for idx, (row, area_km2) in enumerate(zip(grid_reproj.itertuples(), cell_areas_km2)):
            cell_id = getattr(row, cell_id_col)
            geom = [mapping(row.geometry)]
            try:
                out_image, _ = rasterio_mask(src, geom, crop=True, nodata=nodata)
                data = out_image[0].astype(float)
                valid_mask = (data != nodata) & np.isfinite(data) & (data >= 0)
                valid_pixels = data[valid_mask]
                if len(valid_pixels) == 0:
                    pop_sum = 0.0
                    pop_mean = 0.0
                    n_valid = 0
                else:
                    pop_sum = float(valid_pixels.sum())
                    pop_mean = float(valid_pixels.mean())
                    n_valid = int(len(valid_pixels))
            except Exception:
                pop_sum = 0.0
                pop_mean = 0.0
                n_valid = 0

            pop_density = pop_sum / area_km2 if area_km2 > 0 else 0.0
            rows.append({
                "cell_id":               cell_id,
                "pop_sum":               round(pop_sum, 4),
                "pop_mean":              round(pop_mean, 4),
                "pop_density_per_km2":   round(pop_density, 4),
                "n_valid_pixels":        n_valid,
                "cell_area_km2":         round(float(area_km2), 6),
            })

    return pd.DataFrame(rows)


def summary_stats(df: pd.DataFrame) -> dict:
    return {
        "n_cells":          int(len(df)),
        "cells_with_pop":   int((df["pop_sum"] > 0).sum()),
        "zero_pop_cells":   int((df["pop_sum"] == 0).sum()),
        "total_pop":        round(float(df["pop_sum"].sum()), 1),
        "mean_pop_per_cell": round(float(df["pop_sum"].mean()), 2),
        "max_pop_cell":     round(float(df["pop_sum"].max()), 2),
        "mean_density_per_km2": round(float(df["pop_density_per_km2"].mean()), 2),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raster", type=Path,
                        default=Path("data/raw/worldpop/vnm_ppp_2020.tif"))
    parser.add_argument("--grid",   type=Path,
                        default=Path("data/interim/pilot_grid.gpkg"))
    parser.add_argument("--output", type=Path,
                        default=Path("data/interim/grid_worldpop.csv"))
    parser.add_argument("--cell-id-col", default="cell_id")
    args = parser.parse_args()

    if not args.raster.exists():
        raise FileNotFoundError(f"WorldPop raster not found: {args.raster}")
    if not args.grid.exists():
        raise FileNotFoundError(f"Grid not found: {args.grid}")

    print(f"Aggregating {args.raster} by {args.grid} ...")
    df = aggregate_worldpop_by_grid(args.raster, args.grid, args.cell_id_col)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)
    print(f"Wrote {len(df)} rows to {args.output}")

    stats = summary_stats(df)
    for k, v in stats.items():
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
