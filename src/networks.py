"""
Network construction helpers for the four proposal networks.

Network A: walking.
Network B: walking + existing Hanoi public transport.
Network C: walking + existing Hanoi public transport + VinBus.
Network D: motorcycle, calibrated by `src.calibration`.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import networkx as nx
import pandas as pd

try:  # supports both `python -m` and direct test imports from src/
    from .calibration import apply_motorcycle_calibration, load_motorcycle_calibration
except ImportError:  # pragma: no cover
    from calibration import apply_motorcycle_calibration, load_motorcycle_calibration


WALK_SPEED_KPH = 4.8


@dataclass(frozen=True)
class TransitRouteCatalog:
    """Loaded route geometry/metadata for Network B or C."""

    routes: Any
    include_vinbus: bool
    route_count: int
    vinbus_route_count: int


def _load_graphml(graphml_path: str | Path) -> nx.MultiDiGraph:
    import osmnx as ox

    path = Path(graphml_path)
    if not path.exists():
        raise FileNotFoundError(path)
    return ox.load_graphml(path)


def _edge_time_seconds(length_m: float, speed_kph: float) -> float:
    return float(length_m) / (speed_kph * 1000 / 3600) if speed_kph > 0 else float("inf")


def add_walking_travel_times(graph: nx.MultiDiGraph, walk_speed_kph: float = WALK_SPEED_KPH) -> nx.MultiDiGraph:
    """Copy a walk graph and attach `walk_travel_time_s` to each edge."""
    walked = graph.copy()
    for _, _, _, data in walked.edges(keys=True, data=True):
        data["walk_speed_kph"] = walk_speed_kph
        data["walk_travel_time_s"] = _edge_time_seconds(float(data.get("length", 0.0)), walk_speed_kph)
    return walked


def build_walk_network(graphml_path: str | Path, walk_speed_kph: float = WALK_SPEED_KPH) -> nx.MultiDiGraph:
    """Load the pedestrian Network A GraphML and attach walking travel time."""
    return add_walking_travel_times(_load_graphml(graphml_path), walk_speed_kph)


def build_motorcycle_network(
    graphml_path: str | Path,
    speed_factor_csv: str | Path | None = None,
) -> nx.MultiDiGraph:
    """Load Network D and apply explicit motorcycle speed calibration."""
    graph = _load_graphml(graphml_path)
    calibration = load_motorcycle_calibration(speed_factor_csv)
    return apply_motorcycle_calibration(graph, calibration)


def load_transit_routes(routes_path: str | Path, include_vinbus: bool) -> TransitRouteCatalog:
    """
    Load digitized/OSM transit routes for Network B or C.

    Expected columns when available: `route_id`, `route_ref`, `operator`,
    `source`. Network B excludes VinBus. Network C includes VinBus.
    """
    path = Path(routes_path)
    if not path.exists():
        raise FileNotFoundError(path)

    import geopandas as gpd

    routes = gpd.read_file(path)
    if "operator" not in routes.columns:
        routes["operator"] = "unknown"
    if "route_ref" not in routes.columns:
        routes["route_ref"] = routes.get("ref", pd.Series([None] * len(routes)))

    is_vinbus = routes["operator"].fillna("").str.contains("vinbus", case=False, regex=False)
    filtered = routes if include_vinbus else routes.loc[~is_vinbus].copy()
    return TransitRouteCatalog(
        routes=filtered,
        include_vinbus=include_vinbus,
        route_count=int(len(filtered)),
        vinbus_route_count=int(is_vinbus.sum()),
    )


def build_transit_network(routes_path: str | Path, include_vinbus: bool) -> TransitRouteCatalog:
    """
    Build the route catalog for Network B/C.

    Full multimodal edge construction requires confirmed route geometries and
    stop access rules. Until Phase 1 data is resolved, this returns a validated
    route catalog rather than inventing topology.
    """
    return load_transit_routes(routes_path, include_vinbus)
