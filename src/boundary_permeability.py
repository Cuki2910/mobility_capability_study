"""Boundary-crossing and detour diagnostics for walking and motorcycle networks."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import geopandas as gpd
import networkx as nx
import numpy as np
import pandas as pd
from shapely.geometry import LineString, Point

RESTRICTED_ACCESS = {"no", "private", "customers"}


@dataclass(frozen=True)
class PermeabilityResult:
    summary: pd.DataFrame
    crossings: gpd.GeoDataFrame
    detours: pd.DataFrame
    crossing_flow: pd.DataFrame


def _value_is_restricted(value: Any) -> bool:
    return str(value).strip().lower() in RESTRICTED_ACCESS


def _edge_access_status(data: dict[str, Any], origin: dict[str, Any], destination: dict[str, Any], mode: str) -> str:
    mode_keys = ("foot", "access") if mode == "walking" else ("motor_vehicle", "vehicle", "access")
    if any(_value_is_restricted(data.get(key)) for key in mode_keys):
        return "restricted_edge_tag"
    if any(_value_is_restricted(node.get("access")) or str(node.get("barrier", "")).lower() in {"gate", "bollard", "block"}
           for node in (origin, destination)):
        return "restricted_node_tag"
    return "no_restriction_tag"


def _node_frame(graph: nx.MultiDiGraph) -> gpd.GeoDataFrame:
    crs = graph.graph.get("crs", "EPSG:4326")
    rows = [
        {"node": node, "geometry": Point(float(data["x"]), float(data["y"])), **data}
        for node, data in graph.nodes(data=True)
    ]
    return gpd.GeoDataFrame(rows, geometry="geometry", crs=crs)


def boundary_crossings(graph: nx.MultiDiGraph, boundary: gpd.GeoDataFrame, *, mode: str) -> gpd.GeoDataFrame:
    """Identify graph edges whose endpoints lie on opposite sides of a boundary."""
    if boundary.empty or boundary.crs is None:
        raise ValueError("boundary must be non-empty and have a CRS")
    nodes = _node_frame(graph)
    boundary_geom = boundary.to_crs(nodes.crs).geometry.union_all()
    rows = []
    for u, v, key, data in graph.edges(keys=True, data=True):
        origin = graph.nodes[u]
        destination = graph.nodes[v]
        start = Point(float(origin["x"]), float(origin["y"]))
        end = Point(float(destination["x"]), float(destination["y"]))
        inside_u, inside_v = boundary_geom.covers(start), boundary_geom.covers(end)
        if inside_u == inside_v:
            continue
        rows.append({
            "u": u,
            "v": v,
            "key": key,
            "physical_edge_id": "|".join(sorted((str(u), str(v)))),
            "mode": mode,
            "from_inside": bool(inside_u),
            "length_m": float(data.get("length", start.distance(end))),
            "highway": str(data.get("highway", "")),
            "access_status": _edge_access_status(data, origin, destination, mode),
            "geometry": LineString([start, end]),
        })
    return gpd.GeoDataFrame(rows, geometry="geometry", crs=nodes.crs)


def _boundary_length_km(boundary: gpd.GeoDataFrame) -> float:
    metric_crs = boundary.estimate_utm_crs()
    if metric_crs is None:
        raise ValueError("unable to estimate a metric CRS for boundary")
    return float(boundary.to_crs(metric_crs).geometry.union_all().boundary.length / 1000)


def _component_summary(graph: nx.MultiDiGraph, boundary: gpd.GeoDataFrame) -> tuple[int, int]:
    nodes = _node_frame(graph)
    site = boundary.to_crs(nodes.crs).geometry.union_all()
    inside = {node: site.covers(geometry) for node, geometry in zip(nodes["node"], nodes.geometry)}
    undirected = graph.to_undirected()
    components = list(nx.connected_components(undirected))
    traversing = sum(bool({inside[node] for node in component} == {True, False}) for component in components)
    return len(components), traversing


def summarize_crossings(graph: nx.MultiDiGraph, boundary: gpd.GeoDataFrame, *, mode: str) -> tuple[pd.DataFrame, gpd.GeoDataFrame]:
    crossings = boundary_crossings(graph, boundary, mode=mode)
    boundary_km = _boundary_length_km(boundary)
    physical = crossings.drop_duplicates("physical_edge_id")
    components, traversing_components = _component_summary(graph, boundary)
    restricted = int((physical["access_status"] != "no_restriction_tag").sum()) if not physical.empty else 0
    summary = pd.DataFrame([{
        "mode": mode,
        "boundary_length_km": boundary_km,
        "directed_crossing_edges": int(len(crossings)),
        "physical_crossings": int(len(physical)),
        "physical_crossings_per_km": float(len(physical) / boundary_km) if boundary_km else np.nan,
        "restricted_crossings": restricted,
        "components": components,
        "components_spanning_boundary": traversing_components,
        "restriction_tag_coverage": float((physical["access_status"] != "no_restriction_tag").mean()) if not physical.empty else np.nan,
    }])
    return summary, crossings


def _near_boundary_pairs(grid: gpd.GeoDataFrame, boundary: gpd.GeoDataFrame, *, distance_m: float) -> gpd.GeoDataFrame:
    if "cell_id" not in grid or grid["cell_id"].duplicated().any():
        raise ValueError("grid requires unique cell_id values")
    metric_crs = grid.estimate_utm_crs()
    if metric_crs is None:
        raise ValueError("unable to estimate a metric CRS for grid")
    cells = grid.to_crs(metric_crs).copy()
    site = boundary.to_crs(metric_crs).geometry.union_all()
    centroids = cells.geometry.centroid
    cells["inside"] = centroids.apply(site.covers)
    cells["boundary_distance_m"] = centroids.distance(site.boundary)
    near_inside = cells[(cells["inside"]) & (cells["boundary_distance_m"] <= distance_m)].copy()
    near_outside = cells[(~cells["inside"]) & (cells["boundary_distance_m"] <= distance_m)].copy()
    if near_inside.empty or near_outside.empty:
        raise ValueError("near-boundary pairing requires cells on both sides")
    rows = []
    outside_centroids = near_outside.geometry.centroid
    for row in near_inside.itertuples():
        origin = row.geometry.centroid
        distances = outside_centroids.distance(origin)
        destination_index = distances.idxmin()
        destination = near_outside.loc[destination_index]
        rows.append({
            "origin_cell_id": row.cell_id,
            "destination_cell_id": destination.cell_id,
            "euclidean_m": float(distances.loc[destination_index]),
            "origin_geometry": origin,
            "destination_geometry": destination.geometry.centroid,
        })
    return gpd.GeoDataFrame(rows, geometry="origin_geometry", crs=metric_crs)


def _nearest_graph_nodes(graph: nx.MultiDiGraph, points: gpd.GeoSeries) -> list[tuple[Any, float]]:
    nodes = _node_frame(graph).to_crs(points.crs)
    coordinates = np.column_stack((nodes.geometry.x.to_numpy(), nodes.geometry.y.to_numpy()))
    matches = []
    for point in points:
        location = np.array([point.x, point.y])
        index = int(np.argmin(np.sum((coordinates - location) ** 2, axis=1)))
        matches.append((nodes.iloc[index]["node"], float(points.iloc[len(matches)].distance(nodes.iloc[index].geometry))))
    return matches


def boundary_detours(graph: nx.MultiDiGraph, grid: gpd.GeoDataFrame, boundary: gpd.GeoDataFrame, *, mode: str, distance_m: float = 250.0) -> pd.DataFrame:
    """Compare network and straight-line distance for paired cells across the boundary."""
    pairs = _near_boundary_pairs(grid, boundary, distance_m=distance_m)
    origins = _nearest_graph_nodes(graph, gpd.GeoSeries(pairs["origin_geometry"], crs=pairs.crs))
    destinations = _nearest_graph_nodes(graph, gpd.GeoSeries(pairs["destination_geometry"], crs=pairs.crs))
    rows = []
    for pair, (origin, origin_snap_m), (destination, destination_snap_m) in zip(pairs.itertuples(), origins, destinations):
        try:
            distance = nx.shortest_path_length(graph, origin, destination, weight="length") + origin_snap_m + destination_snap_m
            status = "reachable"
        except nx.NetworkXNoPath:
            distance = np.nan
            status = "unreachable"
        rows.append({
            "mode": mode,
            "origin_cell_id": pair.origin_cell_id,
            "destination_cell_id": pair.destination_cell_id,
            "origin_node": origin,
            "destination_node": destination,
            "origin_snap_m": origin_snap_m,
            "destination_snap_m": destination_snap_m,
            "euclidean_m": pair.euclidean_m,
            "network_m": distance,
            "detour_ratio": float(distance / pair.euclidean_m) if np.isfinite(distance) and pair.euclidean_m else np.nan,
            "status": status,
        })
    return pd.DataFrame(rows)


def approximate_crossing_betweenness(graph: nx.MultiDiGraph, crossings: gpd.GeoDataFrame, *, seed: int = 2026, sample_nodes: int = 200) -> pd.DataFrame:
    """Return fixed-seed approximate edge betweenness for the boundary crossings."""
    if crossings.empty:
        return pd.DataFrame(columns=["u", "v", "key", "approx_edge_betweenness"])
    k = min(sample_nodes, graph.number_of_nodes())
    values = nx.edge_betweenness_centrality(graph, k=k, normalized=True, weight="length", seed=seed)
    records = []
    for row in crossings[["u", "v", "key"]].drop_duplicates().itertuples(index=False):
        records.append({"u": row.u, "v": row.v, "key": row.key,
                        "approx_edge_betweenness": float(values.get((row.u, row.v, row.key), 0.0))})
    return pd.DataFrame(records)


def run_permeability(
    graph: nx.MultiDiGraph,
    grid: gpd.GeoDataFrame,
    boundary: gpd.GeoDataFrame,
    *,
    mode: str,
    distance_m: float = 250.0,
    seed: int = 2026,
    sample_nodes: int = 200,
) -> PermeabilityResult:
    summary, crossings = summarize_crossings(graph, boundary, mode=mode)
    detours = boundary_detours(graph, grid, boundary, mode=mode, distance_m=distance_m)
    flow = approximate_crossing_betweenness(graph, crossings, seed=seed, sample_nodes=sample_nodes)
    if not flow.empty:
        crossings = crossings.merge(flow, on=["u", "v", "key"], validate="one_to_one")
    return PermeabilityResult(summary, crossings, detours, flow)
