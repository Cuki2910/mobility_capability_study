"""Generate shifted 250 m grids and an equal-area hexagon grid for robustness."""
from __future__ import annotations

import argparse
from pathlib import Path

import geopandas as gpd
import numpy as np
from shapely.geometry import Polygon, box


def square_grid(extent, cell_size: float, dx: float, dy: float):
    minx, miny, maxx, maxy = extent.bounds
    # Start one cell before the extent so a shifted lattice still covers every edge.
    xs = np.arange(minx - cell_size + dx, maxx, cell_size)
    ys = np.arange(miny - cell_size + dy, maxy, cell_size)
    return [box(x, y, x + cell_size, y + cell_size) for x in xs for y in ys]


def hex_grid(extent, side: float):
    minx, miny, maxx, maxy = extent.bounds
    dx, dy = np.sqrt(3) * side, 1.5 * side
    cells = []
    for row, y in enumerate(np.arange(miny - side, maxy + side, dy)):
        offset = (row % 2) * dx / 2
        for x in np.arange(minx - side + offset, maxx + side, dx):
            cells.append(Polygon([(x + side * np.cos(np.pi / 6 + k * np.pi / 3), y + side * np.sin(np.pi / 6 + k * np.pi / 3)) for k in range(6)]))
    return cells


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--grid", type=Path, default=Path("data/interim/pilot_grid.gpkg"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/interim/grid_sensitivity"))
    args = parser.parse_args()
    base = gpd.read_file(args.grid)
    crs = base.estimate_utm_crs()
    base_m = base.to_crs(crs)
    extent = base_m.geometry.union_all()
    specs = {"shift_x": (125, 0), "shift_y": (0, 125), "shift_xy": (125, 125)}
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, (dx, dy) in specs.items():
        geoms = [geom.intersection(extent) for geom in square_grid(extent, 250, dx, dy)]
        geoms = [geom for geom in geoms if not geom.is_empty]
        frame = gpd.GeoDataFrame({"cell_id": [f"{name}_{i}" for i in range(len(geoms))]}, geometry=geoms, crs=crs).to_crs(base.crs)
        frame.to_file(args.output_dir / f"{name}.gpkg", driver="GPKG")
    side = np.sqrt((2 * 62_500) / (3 * np.sqrt(3)))
    geoms = [geom.intersection(extent) for geom in hex_grid(extent, side)]
    geoms = [geom for geom in geoms if not geom.is_empty]
    frame = gpd.GeoDataFrame({"cell_id": [f"hex_{i}" for i in range(len(geoms))]}, geometry=geoms, crs=crs).to_crs(base.crs)
    frame.to_file(args.output_dir / "hex_equal_area.gpkg", driver="GPKG")
    print(f"Wrote grids to {args.output_dir}; hex side={side:.3f} m")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
