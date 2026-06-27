"""Fetch real OSM walk/drive networks, POIs, and pilot grid for Ocean Park."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


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
            "walk_graphml": "data/raw/pilot_walk_network.graphml",
            "drive_graphml": "data/raw/pilot_drive_network.graphml",
            "pois_gpkg": "data/interim/pilot_pois.gpkg",
            "grid_gpkg": "data/interim/pilot_grid.gpkg",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--center-lat", type=float, default=20.9930)
    parser.add_argument("--center-lon", type=float, default=105.9450)
    parser.add_argument("--half-box-km", type=float, default=2.5)
    parser.add_argument("--cell-size-m", type=int, default=250)
    parser.add_argument("--request-timeout", type=int, default=180)
    args = parser.parse_args()

    import geopandas as gpd
    import osmnx as ox
    from shapely.geometry import box

    ox.settings.requests_timeout = args.request_timeout
    ox.settings.use_cache = True

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    bbox = pilot_bbox(args.center_lat, args.center_lon, args.half_box_km)
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
    ox.save_graphml(G_walk, RAW_DIR / "pilot_walk_network.graphml")
    ox.save_graphml(G_drive, RAW_DIR / "pilot_drive_network.graphml")
    pois.to_file(INTERIM_DIR / "pilot_pois.gpkg", driver="GPKG")
    grid.to_file(INTERIM_DIR / "pilot_grid.gpkg", driver="GPKG")
    manifest = build_manifest(
        bbox, args.center_lat, args.center_lon, args.half_box_km, args.cell_size_m,
        len(G_walk.nodes), len(G_walk.edges), len(G_drive.nodes), len(G_drive.edges), len(pois), len(grid),
    )
    (INTERIM_DIR / "pilot_data_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("Done. Wrote data/raw/*, data/interim/*, and data/interim/pilot_data_manifest.json", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
