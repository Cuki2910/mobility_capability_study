import networkx as nx
import pytest

from scripts.measure_cbd_matching import corridor_bbox, route_distance_m


def test_corridor_bbox_covers_all_points_with_buffer():
    assert corridor_bbox([(21.0, 105.7), (21.1, 105.9)], 0.01) == pytest.approx((105.69, 20.99, 105.91, 21.11))


def test_route_distance_uses_directed_edge_lengths():
    graph = nx.MultiDiGraph()
    graph.graph["crs"] = "EPSG:4326"
    graph.add_node(1, x=105.7, y=21.0)
    graph.add_node(2, x=105.8, y=21.0)
    graph.add_edge(1, 2, length=1250.0)
    assert route_distance_m(graph, (21.0, 105.7), (21.0, 105.8)) == 1250.0
