"""Build data/interim/pilot_accessibility_inputs.csv from real pilot layers."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.accessibility_inputs import build_network_accessibility_inputs, build_spatial_accessibility_inputs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["proxy", "network"], default="proxy")
    parser.add_argument("--grid", type=Path, default=Path("data/interim/pilot_grid.gpkg"))
    parser.add_argument("--pois", type=Path, default=Path("data/interim/merged_pois.gpkg"))
    parser.add_argument("--walk-graph", type=Path, default=Path("data/raw/pilot_walk_network.graphml"))
    parser.add_argument("--drive-graph", type=Path, default=Path("data/raw/pilot_drive_network.graphml"))
    parser.add_argument("--vinbus-geometry", type=Path, default=Path("data/raw/vinbus_overpass_relations_geom.json"))
    parser.add_argument(
        "--vinbus-gtfs-dir",
        type=Path,
        default=Path("data/raw/vinbus_pseudo_gtfs_fixed"),
        help="Pseudo-GTFS dir (API-scraped: 176 routes / 5,631 stops / per-route headway). "
        "Primary Network C source when present; OSM overpass is the fallback.",
    )
    parser.add_argument("--speed-factor-csv", type=Path, default=Path("data/raw/motorcycle_speed_calibration.csv"))
    parser.add_argument("--gtfs", type=Path, default=Path("data/raw/hanoi_gtfs.zip"))
    parser.add_argument("--gtfs-status", default="stale", choices=["current", "stale", "missing", "unverified", "limited", "baseline_limited"])
    parser.add_argument("--walking-threshold-m", type=float, default=800.0)
    parser.add_argument("--motorcycle-threshold-m", type=float, default=3000.0)
    parser.add_argument("--headway-min", type=float, default=15.0)
    parser.add_argument("--vinbus-mode", choices=["stops", "corridor"], default="stops")
    parser.add_argument("--bus-speed-kph", type=float, default=20.0)
    parser.add_argument("--buildings", type=Path, default=Path("data/raw/building_footprints.gpkg"))
    parser.add_argument(
        "--no-pop-weighting",
        action="store_true",
        help="Disable supply-side population weighting of MAI (Decision #19). "
        "Use for the no-pop sensitivity run.",
    )
    parser.add_argument(
        "--worldpop-csv",
        type=Path,
        default=Path("data/interim/grid_worldpop.csv"),
        help="Per-cell WorldPop density used for supply-side MAI weighting (Decision #19).",
    )
    parser.add_argument(
        "--opportunity-basis",
        choices=["proxy", "observed", "observed_strict"],
        default="proxy",
        help="MAI opportunity weights: proxy reproduces current baseline; observed uses "
        "Decision #21 hybrid hierarchy; observed_strict requires source-backed magnitudes "
        "or explicit exclusion for every included POI.",
    )
    parser.add_argument("--output", type=Path, default=Path("data/interim/pilot_accessibility_inputs.csv"))
    args = parser.parse_args()

    if not args.grid.exists():
        raise FileNotFoundError(f"Missing {args.grid}. Run scripts/fetch_osm_data.py first.")
    if not args.pois.exists():
        raise FileNotFoundError(f"Missing {args.pois}. Run scripts/fetch_osm_data.py first.")

    vinbus_geometry = args.vinbus_geometry if args.vinbus_geometry.exists() else None
    vinbus_gtfs_dir = (
        args.vinbus_gtfs_dir
        if args.vinbus_gtfs_dir is not None and (args.vinbus_gtfs_dir / "stops.txt").exists()
        else None
    )
    if args.mode == "network":
        if not args.walk_graph.exists() or not args.drive_graph.exists():
            raise FileNotFoundError("Missing graphml files. Run scripts/fetch_osm_data.py first.")
        speed_csv = args.speed_factor_csv if args.speed_factor_csv.exists() else None
        inputs = build_network_accessibility_inputs(
            args.grid,
            args.pois,
            args.walk_graph,
            args.drive_graph,
            vinbus_geometry_json=vinbus_geometry,
            gtfs_zip=args.gtfs if args.gtfs.exists() else None,
            gtfs_status=args.gtfs_status,
            walk_cutoff_min=args.walking_threshold_m / 80.0,
            motorcycle_cutoff_min=args.motorcycle_threshold_m / 250.0,
            speed_factor_csv=speed_csv,
            headway_min=args.headway_min,
            vinbus_mode=args.vinbus_mode,
            bus_speed_kph=args.bus_speed_kph,
            vinbus_gtfs_dir=vinbus_gtfs_dir,
            buildings_path=args.buildings,
            pop_weighting=not args.no_pop_weighting,
            worldpop_csv=args.worldpop_csv if args.worldpop_csv.exists() else None,
            opportunity_basis=args.opportunity_basis,
        )
    else:
        inputs = build_spatial_accessibility_inputs(
            args.grid,
            args.pois,
            vinbus_geometry_json=vinbus_geometry,
            gtfs_status=args.gtfs_status,
            walking_threshold_m=args.walking_threshold_m,
            motorcycle_threshold_m=args.motorcycle_threshold_m,
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    inputs.to_csv(args.output, index=False)
    print(f"Wrote {args.output} ({len(inputs)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
