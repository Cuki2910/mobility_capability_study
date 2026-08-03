import sys
from pathlib import Path

import geopandas as gpd
import networkx as nx
import pytest
from shapely.geometry import box

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from boundary_permeability import boundary_crossings, boundary_detours, run_permeability


def _graph() -> nx.MultiDiGraph:
    graph = nx.MultiDiGraph(crs="EPSG:3857")
    graph.add_node(1, x=-10, y=0)
    graph.add_node(2, x=10, y=0)
    graph.add_node(3, x=30, y=0)
    graph.add_edge(1, 2, key=0, length=20, highway="footway")
    graph.add_edge(2, 1, key=0, length=20, highway="footway")
    graph.add_edge(2, 3, key=0, length=20, highway="footway")
    graph.add_edge(3, 2, key=0, length=20, highway="footway")
    return graph


def _boundary() -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame({"name": ["site"]}, geometry=[box(0, -20, 20, 20)], crs="EPSG:3857")


def _grid() -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame({"cell_id": [1, 2]}, geometry=[box(2, -2, 8, 2), box(22, -2, 28, 2)], crs="EPSG:3857")


def test_crossings_detect_opposite_boundary_sides():
    crossings = boundary_crossings(_graph(), _boundary(), mode="walking")
    assert len(crossings) == 4
    assert set(crossings["physical_edge_id"]) == {"1|2", "2|3"}
    assert crossings["access_status"].eq("no_restriction_tag").all()


def test_restricted_access_tag_is_reported():
    graph = _graph()
    graph[2][3][0]["access"] = "private"
    crossings = boundary_crossings(graph, _boundary(), mode="walking")
    assert "restricted_edge_tag" in set(crossings["access_status"])


def test_detours_and_permeability_are_reproducible():
    detours = boundary_detours(_graph(), _grid(), _boundary(), mode="walking", distance_m=250)
    assert len(detours) == 1
    assert detours.loc[0, "status"] == "reachable"
    assert detours.loc[0, "detour_ratio"] > 1
    result = run_permeability(_graph(), _grid(), _boundary(), mode="walking", sample_nodes=2)
    assert result.summary.loc[0, "physical_crossings"] == 2
    assert not result.crossing_flow.empty
