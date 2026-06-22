"""Build accessibility-ready pilot inputs from real spatial layers."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

try:
    from .routing import (
        corridor_accessibility,
        gtfs_stops_from_zip,
        load_timed_graph,
        nearest_graph_nodes,
        reachable_counts_and_mean_time,
        stop_accessibility,
        vinbus_corridor_from_overpass,
    )
except ImportError:  # pragma: no cover
    from routing import (
        corridor_accessibility,
        gtfs_stops_from_zip,
        load_timed_graph,
        nearest_graph_nodes,
        reachable_counts_and_mean_time,
        stop_accessibility,
        vinbus_corridor_from_overpass,
    )


REQUIRED_INPUT_COLUMNS = {
    "cell_id",
    "NAI",
    "MAI_A",
    "MAI_B",
    "RAC_time_A_raw",
    "RAC_time_B_raw",
    "RAC_opp_A_raw",
    "RAC_opp_B_raw",
}


def validate_accessibility_inputs(df: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED_INPUT_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Accessibility inputs missing columns: {sorted(missing)}")
    return df


def baseline_transit_limited(gtfs_status: str | None) -> bool:
    if not gtfs_status:
        return True
    return gtfs_status.lower() in {"missing", "stale", "unverified", "limited", "baseline_limited"}


def _safe_ratio(num: np.ndarray, den: np.ndarray) -> np.ndarray:
    return np.divide(num, den, out=np.zeros_like(num, dtype=float), where=den > 0)


def _relations_with_geometry(overpass_json: Path | None) -> int:
    if overpass_json is None or not overpass_json.exists():
        return 0
    data = json.loads(overpass_json.read_text(encoding="utf-8"))
    count = 0
    for element in data.get("elements", []):
        members = element.get("members", []) or []
        if element.get("geometry") or any(member.get("geometry") for member in members):
            count += 1
    return count


def build_proxy_accessibility_inputs(
    cell_ids: Iterable,
    nai: Iterable[float],
    motorcycle_opportunities: Iterable[float] | None = None,
    vinbus_route_bonus: float = 0.0,
    gtfs_status: str | None = "stale",
) -> pd.DataFrame:
    """Small pure builder used by tests and as a fallback for spatial assembly."""
    nai_arr = np.asarray(list(nai), dtype=float)
    moto = np.asarray(list(motorcycle_opportunities), dtype=float) if motorcycle_opportunities is not None else np.maximum(nai_arr, 1)
    limited = baseline_transit_limited(gtfs_status)
    mai_a = np.zeros_like(nai_arr) if limited else nai_arr.copy()
    mai_b = np.maximum(mai_a, nai_arr + vinbus_route_bonus)

    # Conservative proxy: motorcycles are faster than walk+transit baseline;
    # VinBus reduces the walk+transit penalty when geometry is available.
    motorcycle_time = 10 + moto
    wt_a_time = motorcycle_time * (3.0 if limited else 2.0)
    wt_b_time = np.maximum(motorcycle_time * 1.5, wt_a_time - max(vinbus_route_bonus, 0.0))

    out = pd.DataFrame({
        "cell_id": list(cell_ids),
        "NAI": nai_arr,
        "MAI_A": mai_a,
        "MAI_B": mai_b,
        "RAC_time_A_raw": _safe_ratio(motorcycle_time, wt_a_time),
        "RAC_time_B_raw": _safe_ratio(motorcycle_time, wt_b_time),
        "RAC_opp_A_raw": _safe_ratio(mai_a, moto),
        "RAC_opp_B_raw": _safe_ratio(mai_b, moto),
        "MAI_A_baseline_limited": limited,
        "accessibility_input_notes": "proxy-v1; replace with network travel-time metrics when route/stop timetable data is complete",
    })
    return validate_accessibility_inputs(out)


def build_spatial_accessibility_inputs(
    grid_path: str | Path,
    pois_path: str | Path,
    vinbus_geometry_json: str | Path | None = None,
    gtfs_status: str | None = "stale",
    walking_threshold_m: float = 800.0,
    motorcycle_threshold_m: float = 3000.0,
) -> pd.DataFrame:
    """Build conservative v1 inputs from grid, POIs, and optional VinBus geometry."""
    import geopandas as gpd

    grid = gpd.read_file(grid_path).to_crs(epsg=3857)
    pois = gpd.read_file(pois_path).to_crs(epsg=3857)
    centroids = grid.geometry.centroid
    poi_points = pois.geometry.centroid

    nai = []
    moto_opp = []
    for centroid in centroids:
        distances = poi_points.distance(centroid)
        nai.append(int((distances <= walking_threshold_m).sum()))
        moto_opp.append(int((distances <= motorcycle_threshold_m).sum()))

    route_bonus = float(_relations_with_geometry(Path(vinbus_geometry_json)) if vinbus_geometry_json else 0)
    return build_proxy_accessibility_inputs(
        grid["cell_id"].tolist(),
        nai,
        motorcycle_opportunities=moto_opp,
        vinbus_route_bonus=route_bonus,
        gtfs_status=gtfs_status,
    )


def build_network_accessibility_inputs(
    grid_path: str | Path,
    pois_path: str | Path,
    walk_graphml: str | Path,
    drive_graphml: str | Path,
    vinbus_geometry_json: str | Path | None = None,
    gtfs_zip: str | Path | None = None,
    gtfs_status: str | None = "baseline_limited",
    walk_cutoff_min: float = 15.0,
    motorcycle_cutoff_min: float = 20.0,
    transit_access_m: float = 800.0,
    transit_opportunity_m: float = 800.0,
    speed_factor_csv: str | Path | None = None,
) -> pd.DataFrame:
    """Build pilot inputs from graph travel times plus transit corridor/stop access."""
    import geopandas as gpd

    grid = gpd.read_file(grid_path)
    pois = gpd.read_file(pois_path)
    grid_points = gpd.GeoSeries(grid.to_crs(epsg=3857).geometry.centroid, crs="EPSG:3857").to_crs(epsg=4326)
    poi_points = gpd.GeoSeries(pois.to_crs(epsg=3857).geometry.centroid, crs="EPSG:3857").to_crs(epsg=4326)
    grid_nodes_gdf = gpd.GeoDataFrame(grid[["cell_id"]].copy(), geometry=grid_points, crs="EPSG:4326")
    poi_nodes_gdf = gpd.GeoDataFrame(pois.drop(columns="geometry", errors="ignore"), geometry=poi_points, crs="EPSG:4326")

    walk_graph, walk_weight = load_timed_graph(walk_graphml, "walk")
    drive_graph, drive_weight = load_timed_graph(drive_graphml, "motorcycle", speed_factor_csv=speed_factor_csv)
    grid_walk_nodes = nearest_graph_nodes(walk_graph, grid_nodes_gdf)
    poi_walk_nodes = nearest_graph_nodes(walk_graph, poi_nodes_gdf)
    grid_drive_nodes = nearest_graph_nodes(drive_graph, grid_nodes_gdf)
    poi_drive_nodes = nearest_graph_nodes(drive_graph, poi_nodes_gdf)

    nai, walk_mean_time = reachable_counts_and_mean_time(walk_graph, grid_walk_nodes, poi_walk_nodes, walk_cutoff_min * 60, walk_weight)
    moto_opp, moto_mean_time = reachable_counts_and_mean_time(drive_graph, grid_drive_nodes, poi_drive_nodes, motorcycle_cutoff_min * 60, drive_weight)

    gtfs_missing = gtfs_zip is None or not Path(gtfs_zip).exists()
    baseline_limited = baseline_transit_limited(gtfs_status) or gtfs_missing

    # Use stop geometry even when timetable is stale/baseline_limited —
    # stop locations are stable even when service dates have expired.
    # Only skip stops entirely when the GTFS file is absent.
    stops = None if gtfs_missing else gtfs_stops_from_zip(gtfs_zip)
    mai_a, wt_a_time = stop_accessibility(grid, pois, stops, transit_access_m, transit_opportunity_m)
    if stops is None:
        mai_a = np.zeros(len(grid), dtype=float)
        wt_a_time = np.maximum(moto_mean_time * 3.0, 1.0)

    corridor = vinbus_corridor_from_overpass(vinbus_geometry_json)
    vinbus_opp, wt_b_time = corridor_accessibility(grid, pois, corridor, transit_access_m, transit_opportunity_m)
    mai_b = np.maximum(mai_a, vinbus_opp)
    wt_b_time = np.minimum(np.where(wt_b_time > 0, wt_b_time, np.inf), np.maximum(wt_a_time * 0.85, moto_mean_time * 1.5))
    wt_b_time = np.where(np.isfinite(wt_b_time), wt_b_time, np.maximum(moto_mean_time * 2.0, 1.0))

    out = pd.DataFrame({
        "cell_id": grid["cell_id"].tolist(),
        "NAI": nai,
        "MAI_A": mai_a,
        "MAI_B": mai_b,
        "RAC_time_A_raw": _safe_ratio(moto_mean_time, wt_a_time),
        "RAC_time_B_raw": _safe_ratio(moto_mean_time, wt_b_time),
        "RAC_opp_A_raw": _safe_ratio(mai_a, np.maximum(moto_opp, 1.0)),
        "RAC_opp_B_raw": _safe_ratio(mai_b, np.maximum(moto_opp, 1.0)),
        "MAI_A_baseline_limited": baseline_limited,
        "accessibility_input_notes": "network-v1; graph shortest paths for NAI/motorcycle plus GTFS-stop/VinBus-corridor transit proxy",
    })
    return validate_accessibility_inputs(out)
