"""Fetch real OSM walk/drive networks, POIs, and pilot grid for Ocean Park."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.site_config import add_site_config_argument, apply_site_config, print_resolved_paths

RAW_DIR = Path("data/raw")
INTERIM_DIR = Path("data/interim")


def pilot_bbox(center_lat: float, center_lon: float, half_box_km: float) -> tuple[float, float, float, float]:
    deg_per_km = 1 / 111
    return (
        center_lon - half_box_km * deg_per_km,
        center_lat - half_box_km * deg_per_km,
        center_lon + half_box_km * deg_per_km,
        center_lat + half_box_km * deg_per_km,
    )  # west south east north


def build_manifest(
    bbox: tuple[float, float, float, float],
    center_lat: float,
    center_lon: float,
    half_box_km: float,
    cell_size_m: int,
    walk_nodes: int,
    walk_edges: int,
    drive_nodes: int,
    drive_edges: int,
    poi_count: int,
    grid_count: int,
    walk_graphml: Path = RAW_DIR / "pilot_walk_network.graphml",
    drive_graphml: Path = RAW_DIR / "pilot_drive_network.graphml",
    pois_gpkg: Path = INTERIM_DIR / "pilot_pois.gpkg",
    grid_gpkg: Path = INTERIM_DIR / "pilot_grid.gpkg",
) -> dict:
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "center_lat": center_lat,
        "center_lon": center_lon,
        "half_box_km": half_box_km,
        "cell_size_m": cell_size_m,
        "bbox_west_south_east_north": list(bbox),
        "counts": {
            "walk_nodes": walk_nodes,
            "walk_edges": walk_edges,
            "drive_nodes": drive_nodes,
            "drive_edges": drive_edges,
            "pois": poi_count,
            "grid_cells": grid_count,
        },
        "outputs": {
            "walk_graphml": str(walk_graphml),
            "drive_graphml": str(drive_graphml),
            "pois_gpkg": str(pois_gpkg),
            "grid_gpkg": str(grid_gpkg),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    add_site_config_argument(parser)
    parser.add_argument("--center-lat", type=float, default=20.9930)
    parser.add_argument("--center-lon", type=float, default=105.9450)
    parser.add_argument("--half-box-km", type=float, default=2.5)
    parser.add_argument("--cell-size-m", type=int, default=250)
    parser.add_argument("--request-timeout", type=int, default=180)
    parser.add_argument("--walk-output", type=Path, default=RAW_DIR / "pilot_walk_network.graphml")
    parser.add_argument("--drive-output", type=Path, default=RAW_DIR / "pilot_drive_network.graphml")
    parser.add_argument("--pois-output", type=Path, default=INTERIM_DIR / "pilot_pois.gpkg")
    parser.add_argument("--grid-output", type=Path, default=INTERIM_DIR / "pilot_grid.gpkg")
    parser.add_argument("--manifest-output", type=Path, default=INTERIM_DIR / "pilot_data_manifest.json")
    args = parser.parse_args()
    config = apply_site_config(args, parser, {
        "center_lat": "center.lat",
        "center_lon": "center.lon",
        "half_box_km": "center.half_box_km",
        "cell_size_m": "center.cell_size_m",
        "walk_output": "paths.walk_graph",
        "drive_output": "paths.drive_graph",
        "pois_output": "paths.osm_pois",
        "grid_output": "paths.grid",
        "manifest_output": "paths.data_manifest",
    })
    bbox = pilot_bbox(args.center_lat, args.center_lon, args.half_box_km)
    if args.dry_run:
        print_resolved_paths("OSM fetch dry-run", {
            "site_id": config.site_id if config else "pilot",
            "bbox_west_south_east_north": bbox,
            "walk_output": args.walk_output,
            "drive_output": args.drive_output,
            "pois_output": args.pois_output,
            "grid_output": args.grid_output,
            "manifest_output": args.manifest_output,
        })
        return 0

    import geopandas as gpd
    import osmnx as ox
    from shapely.geometry import box

    ox.settings.requests_timeout = args.request_timeout
    ox.settings.use_cache = True

    args.walk_output.parent.mkdir(parents=True, exist_ok=True)
    args.drive_output.parent.mkdir(parents=True, exist_ok=True)
    args.pois_output.parent.mkdir(parents=True, exist_ok=True)
    args.grid_output.parent.mkdir(parents=True, exist_ok=True)
    args.manifest_output.parent.mkdir(parents=True, exist_ok=True)
    west, south, east, north = bbox

    print("Step 1: downloading walking network...", flush=True)
    graph_kwargs = {"bbox": (west, south, east, north)}
    G_walk = ox.graph_from_bbox(**graph_kwargs, network_type="walk")
    print(f"  walk network: {len(G_walk.nodes)} nodes, {len(G_walk.edges)} edges", flush=True)

    print("Step 2: downloading driving network...", flush=True)
    G_drive = ox.graph_from_bbox(**graph_kwargs, network_type="drive")
    print(f"  drive network: {len(G_drive.nodes)} nodes, {len(G_drive.edges)} edges", flush=True)

    print("Step 3: downloading POIs for NAI...", flush=True)
    tags = {
        "amenity": [
            "school", "hospital", "clinic", "pharmacy",
            # Economic domain (hướng C): formal employment and financial services
            "bank", "atm", "marketplace", "post_office",
        ],
        "shop": True,
        "leisure": ["park"],
        # Economic domain (hướng C): office buildings and business parks
        "office": True,
        # Landuse polygons for economic area proxy (hướng B)
        "landuse": ["commercial", "retail", "industrial", "office"],
    }
    pois = ox.features_from_bbox(bbox=(west, south, east, north), tags=tags)
    print(f"  POIs found: {len(pois)}", flush=True)

    print("Step 4: building pilot grid...", flush=True)
    gdf_bbox = gpd.GeoDataFrame(geometry=[box(*bbox)], crs="EPSG:4326").to_crs(epsg=3857)
    minx, miny, maxx, maxy = gdf_bbox.total_bounds
    xs = np.arange(minx, maxx, args.cell_size_m)
    ys = np.arange(miny, maxy, args.cell_size_m)
    grid_cells = [box(x, y, x + args.cell_size_m, y + args.cell_size_m) for x in xs for y in ys]
    grid = gpd.GeoDataFrame(geometry=grid_cells, crs="EPSG:3857").to_crs(epsg=4326)
    grid["cell_id"] = range(len(grid))
    print(f"  grid cells created: {len(grid)}", flush=True)

    print("Step 5: saving outputs...", flush=True)
    ox.save_graphml(G_walk, args.walk_output)
    ox.save_graphml(G_drive, args.drive_output)
    pois.to_file(args.pois_output, driver="GPKG")
    grid.to_file(args.grid_output, driver="GPKG")
    manifest = build_manifest(
        bbox, args.center_lat, args.center_lon, args.half_box_km, args.cell_size_m,
        len(G_walk.nodes), len(G_walk.edges), len(G_drive.nodes), len(G_drive.edges), len(pois), len(grid),
        args.walk_output, args.drive_output, args.pois_output, args.grid_output,
    )
    args.manifest_output.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Done. Wrote {args.walk_output}, {args.drive_output}, {args.pois_output}, {args.grid_output}, and {args.manifest_output}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
