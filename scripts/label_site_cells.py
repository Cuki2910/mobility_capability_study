"""Label grid cells by planned/organic/transition core overlap."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import geopandas as gpd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.site_config import add_site_config_argument, apply_site_config, print_resolved_paths


def _union_geometries(geoms):
    if hasattr(geoms, "union_all"):
        return geoms.union_all()
    return geoms.unary_union


def label_cells(
    grid_path: Path,
    planned_boundary: Path,
    organic_boundary: Path,
    primary_overlap: float = 0.75,
) -> gpd.GeoDataFrame:
    grid = gpd.read_file(grid_path)
    if "cell_id" not in grid.columns:
        raise ValueError(f"Grid missing cell_id column: {grid_path}")
    utm = grid.estimate_utm_crs()
    grid_m = grid.to_crs(utm).copy()
    planned = _union_geometries(gpd.read_file(planned_boundary).to_crs(utm).geometry)
    organic = _union_geometries(gpd.read_file(organic_boundary).to_crs(utm).geometry)

    areas = grid_m.geometry.area.replace(0, float("nan"))
    planned_frac = grid_m.geometry.intersection(planned).area / areas
    organic_frac = grid_m.geometry.intersection(organic).area / areas

    labels = []
    for p_frac, o_frac in zip(planned_frac.fillna(0), organic_frac.fillna(0)):
        if p_frac >= primary_overlap and o_frac == 0:
            labels.append("planned_west")
        elif o_frac >= primary_overlap and p_frac == 0:
            labels.append("organic_west")
        elif p_frac > 0 or o_frac > 0:
            labels.append("transition")
        else:
            labels.append("outside_core")

    out = grid.copy()
    out["west_core_label"] = labels
    out["planned_overlap_frac"] = planned_frac.fillna(0).round(4).to_numpy()
    out["organic_overlap_frac"] = organic_frac.fillna(0).round(4).to_numpy()
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    add_site_config_argument(parser)
    parser.add_argument("--grid", type=Path, default=Path("data/interim/pilot_grid.gpkg"))
    parser.add_argument("--planned-boundary", type=Path, required=False)
    parser.add_argument("--organic-boundary", type=Path, required=False)
    parser.add_argument("--output", type=Path, default=Path("data/interim/labeled_grid.gpkg"))
    parser.add_argument("--primary-overlap", type=float, default=0.75)
    args = parser.parse_args()
    config = apply_site_config(args, parser, {
        "grid": "paths.grid",
        "planned_boundary": "paths.smart_city_core_boundary",
        "organic_boundary": "paths.tay_mo_core_boundary",
        "output": "paths.labeled_grid",
    })

    if args.dry_run:
        print_resolved_paths("Cell label dry-run", {
            "site_id": config.site_id if config else "pilot",
            "grid": args.grid,
            "planned_boundary": args.planned_boundary,
            "organic_boundary": args.organic_boundary,
            "output": args.output,
            "primary_overlap": args.primary_overlap,
        })
        return 0

    if args.planned_boundary is None or args.organic_boundary is None:
        raise ValueError("Both --planned-boundary and --organic-boundary are required.")
    if not args.grid.exists():
        raise FileNotFoundError(f"Grid not found: {args.grid}")
    if not args.planned_boundary.exists():
        raise FileNotFoundError(f"Planned boundary not found: {args.planned_boundary}")
    if not args.organic_boundary.exists():
        raise FileNotFoundError(f"Organic boundary not found: {args.organic_boundary}")

    labeled = label_cells(
        args.grid,
        args.planned_boundary,
        args.organic_boundary,
        primary_overlap=args.primary_overlap,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    labeled.to_file(args.output, driver="GPKG")
    print(f"Wrote {args.output} ({len(labeled)} cells)")
    print(f"  labels: {labeled['west_core_label'].value_counts().to_dict()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
