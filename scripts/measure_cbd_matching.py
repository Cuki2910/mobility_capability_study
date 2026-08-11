"""Measure comparable drive-network distances from candidate cores to Hoan Kiem."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import geopandas as gpd
import networkx as nx


def boundary_centroid(path: Path) -> tuple[float, float]:
    """Return a boundary centroid as latitude, longitude in WGS84."""
    boundary = gpd.read_file(path).to_crs(epsg=4326)
    if boundary.empty:
        raise ValueError(f"Boundary is empty: {path}")
    centroid = boundary.geometry.union_all().centroid
    return float(centroid.y), float(centroid.x)


def corridor_bbox(points: list[tuple[float, float]], buffer_degrees: float = 0.01) -> tuple[float, float, float, float]:
    """Return west, south, east, north bounds covering all points plus a route buffer."""
    latitudes, longitudes = zip(*points)
    return (
        min(longitudes) - buffer_degrees,
        min(latitudes) - buffer_degrees,
        max(longitudes) + buffer_degrees,
        max(latitudes) + buffer_degrees,
    )


def route_distance_m(graph: nx.MultiDiGraph, origin: tuple[float, float], destination: tuple[float, float]) -> float:
    """Find directed road-network distance using each edge's OSM length in metres."""
    import osmnx as ox

    origin_node = ox.distance.nearest_nodes(graph, X=origin[1], Y=origin[0])
    destination_node = ox.distance.nearest_nodes(graph, X=destination[1], Y=destination[0])
    return float(nx.shortest_path_length(graph, origin_node, destination_node, weight="length"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smart-city-boundary", type=Path, default=Path("data/raw/west_taymo_smart_city_core_boundary.gpkg"))
    parser.add_argument("--tay-mo-boundary", type=Path, default=Path("data/raw/west_taymo_tay_mo_core_boundary.gpkg"))
    parser.add_argument("--ocean-park-boundary", type=Path, default=Path("data/interim/ocean_park_1_boundary.geojson"))
    parser.add_argument("--graph", type=Path, default=Path("data/raw/cbd_matching_drive_network.graphml"))
    parser.add_argument("--output", type=Path, default=Path("outputs/west_taymo/cbd_network_distance_preflight.csv"))
    parser.add_argument("--manifest", type=Path, default=Path("outputs/west_taymo/cbd_network_distance_manifest.json"))
    parser.add_argument("--cbd-lat", type=float, default=21.0287)
    parser.add_argument("--cbd-lon", type=float, default=105.8524)
    parser.add_argument("--request-timeout", type=int, default=300)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    origins = {
        "smart_city_core": boundary_centroid(args.smart_city_boundary),
        "tay_mo_core": boundary_centroid(args.tay_mo_boundary),
        "ocean_park": boundary_centroid(args.ocean_park_boundary),
    }
    cbd = (args.cbd_lat, args.cbd_lon)
    bbox = corridor_bbox([*origins.values(), cbd])
    if args.dry_run:
        print(f"Corridor bbox W/S/E/N: {bbox}")
        for name, point in origins.items():
            print(f"{name}: {point[0]:.6f}, {point[1]:.6f}")
        print(f"CBD: {cbd[0]:.6f}, {cbd[1]:.6f}")
        print(f"Graph: {args.graph}")
        return 0

    import osmnx as ox
    ox.settings.requests_timeout = args.request_timeout
    ox.settings.use_cache = True
    if args.graph.exists():
        graph = ox.load_graphml(args.graph)
        source = "existing_graphml"
    else:
        west, south, east, north = bbox
        graph = ox.graph_from_bbox((west, south, east, north), network_type="drive")
        args.graph.parent.mkdir(parents=True, exist_ok=True)
        ox.save_graphml(graph, args.graph)
        source = "osm_download"

    rows = []
    ocean_distance = route_distance_m(graph, origins["ocean_park"], cbd)
    for name, origin in origins.items():
        distance = route_distance_m(graph, origin, cbd)
        rows.append({
            "origin": name,
            "origin_lat": origin[0],
            "origin_lon": origin[1],
            "cbd_lat": cbd[0],
            "cbd_lon": cbd[1],
            "drive_distance_km": distance / 1000,
            "ratio_to_ocean_park": distance / ocean_distance,
            "within_15pct_of_ocean_park": abs(distance / ocean_distance - 1) <= 0.15,
        })
    import pandas as pd
    frame = pd.DataFrame(rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.output, index=False)
    args.manifest.write_text(json.dumps({
        "source": source,
        "graph": str(args.graph),
        "bbox_west_south_east_north": bbox,
        "nodes": len(graph.nodes),
        "edges": len(graph.edges),
        "cbd": {"lat": cbd[0], "lon": cbd[1]},
    }, indent=2) + "\n", encoding="utf-8")
    print(frame.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
