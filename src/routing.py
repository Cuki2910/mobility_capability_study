"""Small routing helpers for pilot accessibility inputs."""
from __future__ import annotations

from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd

try:
    from .networks import build_motorcycle_network, build_walk_network
except ImportError:  # pragma: no cover
    from networks import build_motorcycle_network, build_walk_network


def load_timed_graph(
    graphml_path: str | Path,
    mode: str,
    speed_factor_csv: str | Path | None = None,
) -> tuple[nx.MultiDiGraph, str]:
    if mode == "walk":
        return build_walk_network(graphml_path), "walk_travel_time_s"
    if mode == "motorcycle":
        return build_motorcycle_network(graphml_path, speed_factor_csv=speed_factor_csv), "motorcycle_travel_time_s"
    raise ValueError(f"unknown mode: {mode}")


def nearest_graph_nodes(graph: nx.MultiDiGraph, geometries) -> list[int]:
    import osmnx as ox

    points = geometries.to_crs(epsg=4326)
    return list(ox.distance.nearest_nodes(graph, points.geometry.x.to_numpy(), points.geometry.y.to_numpy()))


def reachable_counts_and_mean_time(
    graph: nx.MultiDiGraph,
    origin_nodes: list[int],
    destination_nodes: list[int],
    cutoff_s: float,
    weight: str,
) -> tuple[np.ndarray, np.ndarray]:
    destination_set = set(destination_nodes)
    counts: list[int] = []
    means: list[float] = []
    for origin in origin_nodes:
        lengths = nx.single_source_dijkstra_path_length(graph, origin, cutoff=cutoff_s, weight=weight)
        times = [float(lengths[node]) for node in destination_set if node in lengths]
        counts.append(len(times))
        means.append(float(np.mean(times)) if times else float(cutoff_s))
    return np.asarray(counts, dtype=float), np.asarray(means, dtype=float)


def gtfs_stops_from_zip(gtfs_zip: str | Path | None):
    if gtfs_zip is None or not Path(gtfs_zip).exists():
        return None
    import geopandas as gpd
    import zipfile

    with zipfile.ZipFile(gtfs_zip) as zf:
        if "stops.txt" not in zf.namelist():
            return None
        with zf.open("stops.txt") as handle:
            stops = pd.read_csv(handle)
    if not {"stop_lat", "stop_lon"} <= set(stops.columns):
        return None
    return gpd.GeoDataFrame(stops, geometry=gpd.points_from_xy(stops["stop_lon"], stops["stop_lat"]), crs="EPSG:4326")


def vinbus_corridor_from_overpass(overpass_json: str | Path | None):
    if overpass_json is None or not Path(overpass_json).exists():
        return None
    import geopandas as gpd
    import json
    from shapely.geometry import LineString

    data = json.loads(Path(overpass_json).read_text(encoding="utf-8"))
    rows = []
    for element in data.get("elements", []):
        tags = element.get("tags", {})
        for member in element.get("members", []) or []:
            geom = member.get("geometry") or []
            if len(geom) >= 2:
                rows.append({
                    "relation_id": element.get("id"),
                    "ref": tags.get("ref"),
                    "operator": tags.get("operator"),
                    "geometry": LineString([(p["lon"], p["lat"]) for p in geom]),
                })
    if not rows:
        return None
    return gpd.GeoDataFrame(rows, crs="EPSG:4326")


def corridor_accessibility(grid, pois, corridor, access_m: float, opportunity_m: float) -> tuple[np.ndarray, np.ndarray]:
    if corridor is None or len(corridor) == 0:
        zeros = np.zeros(len(grid), dtype=float)
        return zeros, zeros
    corridor_3857 = corridor.to_crs(epsg=3857)
    union = corridor_3857.geometry.union_all()
    centroids = grid.to_crs(epsg=3857).geometry.centroid
    poi_points = pois.to_crs(epsg=3857).geometry.centroid
    poi_near_corridor = poi_points.distance(union) <= opportunity_m
    corridor_poi_count = float(poi_near_corridor.sum())
    distances = centroids.distance(union)
    accessible = distances <= access_m
    opps = np.where(accessible, corridor_poi_count, 0.0)
    # access + line-haul proxy; used only until stop/timetable data exists.
    times = np.where(accessible, (distances / 1.333) + 15 * 60, 60 * 60)
    return opps.astype(float), times.astype(float)


def stop_accessibility(grid, pois, stops, access_m: float, opportunity_m: float) -> tuple[np.ndarray, np.ndarray]:
    if stops is None or len(stops) == 0:
        zeros = np.zeros(len(grid), dtype=float)
        return zeros, zeros
    stops_3857 = stops.to_crs(epsg=3857)
    stop_union = stops_3857.geometry.union_all()
    centroids = grid.to_crs(epsg=3857).geometry.centroid
    poi_points = pois.to_crs(epsg=3857).geometry.centroid
    poi_near_stop = poi_points.apply(lambda geom: stops_3857.distance(geom).min() <= opportunity_m)
    stop_poi_count = float(poi_near_stop.sum())
    distances = centroids.distance(stop_union)
    accessible = distances <= access_m
    opps = np.where(accessible, stop_poi_count, 0.0)
    times = np.where(accessible, (distances / 1.333) + 20 * 60, 75 * 60)
    return opps.astype(float), times.astype(float)
