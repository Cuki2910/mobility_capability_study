import json
import sys
from pathlib import Path

import geopandas as gpd
import networkx as nx
import numpy as np
from shapely.geometry import Point

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from networks import add_walking_travel_times
from routing import opportunity_weighted_mean_time, vinbus_stop_accessibility, vinbus_stops_from_overpass
from scripts.evaluate_overture_gate import evaluate_gate
from scripts.typology_robustness import run_robustness


def _overpass_fixture(path: Path) -> Path:
    data = {
        "elements": [
            {
                "type": "relation",
                "id": 100,
                "tags": {"ref": "E01", "name": "Ocean Park test"},
                "members": [
                    {"type": "node", "ref": 10, "role": "platform", "lat": 0.0, "lon": 0.001},
                    {"type": "node", "ref": 11, "role": "platform", "lat": 0.0, "lon": 0.002},
                    {"type": "node", "ref": 10, "role": "platform", "lat": 0.0, "lon": 0.001},
                ],
            }
        ]
    }
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_vinbus_stops_from_overpass_dedupes_platform_nodes(tmp_path):
    stops = vinbus_stops_from_overpass(_overpass_fixture(tmp_path / "vinbus.json"))

    assert len(stops) == 2
    assert stops.crs.to_epsg() == 4326
    assert set(stops["node_id"]) == {10, 11}
    assert {"relation_id", "ref", "role"} <= set(stops.columns)


def test_vinbus_stops_from_overpass_missing_returns_empty(tmp_path):
    stops = vinbus_stops_from_overpass(tmp_path / "missing.json")

    assert stops.empty
    assert stops.crs.to_epsg() == 4326


def test_vinbus_stop_accessibility_on_tiny_graph_is_finite(tmp_path):
    graph = nx.MultiDiGraph()
    graph.graph["crs"] = "EPSG:4326"
    graph.add_node(1, x=0.0, y=0.0)
    graph.add_node(2, x=0.001, y=0.0)
    graph.add_node(3, x=0.002, y=0.0)
    graph.add_node(4, x=0.0022, y=0.0)
    for u, v, length in [(1, 2, 111.0), (2, 3, 111.0), (3, 4, 22.0)]:
        graph.add_edge(u, v, length=length)
        graph.add_edge(v, u, length=length)
    graph = add_walking_travel_times(graph)

    grid = gpd.GeoDataFrame({"cell_id": [1]}, geometry=[Point(0.0, 0.0)], crs="EPSG:4326")
    pois = gpd.GeoDataFrame({"name": ["clinic"]}, geometry=[Point(0.0022, 0.0)], crs="EPSG:4326")

    mai, times = vinbus_stop_accessibility(
        graph,
        grid,
        pois,
        grid_nodes=[1],
        poi_nodes=[4],
        poi_domains=["tertiary_healthcare"],
        poi_opp_weights=[1.0],
        weight_attr="walk_travel_time_s",
        overpass_json=_overpass_fixture(tmp_path / "vinbus.json"),
        access_m=800.0,
        headway_min=15.0,
        bus_speed_kph=20.0,
    )

    assert np.isfinite(mai).all()
    assert np.isfinite(times).all()
    assert mai[0] > 0
    assert times[0] < 3600.0

def test_opportunity_weighted_mean_time_uses_domain_and_poi_weights():
    graph = nx.MultiDiGraph()
    graph.add_edge(1, 2, travel_time_s=600.0)
    graph.add_edge(1, 3, travel_time_s=1800.0)
    graph.add_edge(4, 5, travel_time_s=600.0)

    out = opportunity_weighted_mean_time(
        graph,
        origin_nodes=[1, 4],
        destination_nodes=[2, 3],
        poi_domains=["economic", "healthcare"],
        poi_opp_weights=[2.0, 1.0],
        weight_attr="travel_time_s",
        domain_weights={"economic": 0.5, "healthcare": 0.5},
        t_zero_min=60.0,
    )

    assert np.isclose(out[0], (600.0 + 900.0) / 1.5)
    assert out[1] == 3600.0


def test_overture_gate_requires_all_rows_checked():
    import pandas as pd

    df = pd.DataFrame({
        "spot_check_status": ["confirmed"] * 39 + ["unchecked"] * 16,
        "category": ["retail"] * 55,
    })
    result = evaluate_gate(df)

    assert result["confirmed"] == 39
    assert result["verdict"] == "INCOMPLETE"


def test_typology_robustness_outputs_expected_variants():
    import pandas as pd

    metrics = pd.DataFrame({
        "NAI": [0, 1, 2, 3, 4, 5],
        "NAI_norm": [0, 0.2, 0.4, 0.6, 0.8, 1.0],
        "MCS_B": [0.1, 0.7, 0.2, 0.8, 0.3, 0.9],
        "typology_B": [
            "Motorcycle Lock-in",
            "Transit-Dependent",
            "Motorcycle Lock-in",
            "Integrated Capability",
            "Fragmented Capability",
            "Integrated Capability",
        ],
    })

    out = run_robustness(metrics)

    assert "absolute_norm_0.50" in set(out["variant"])
    assert "quantile_0.40" in set(out["variant"])
    assert out["kappa_vs_primary"].between(-1, 1).all()
