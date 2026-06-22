import sys
import zipfile
from datetime import date
from pathlib import Path
from urllib.error import HTTPError

import networkx as nx
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from accessibility_inputs import build_proxy_accessibility_inputs, validate_accessibility_inputs
from calibration import apply_motorcycle_calibration, calibration_table
from networks import add_walking_travel_times
from pilot import compute_pilot_metrics, pilot_summary
from validation import robustness_summary, vif_flags
from scripts.check_hanoi_gtfs import inspect_gtfs
from scripts.check_population_proxy_resolution import classify_resolution
from scripts.check_vinbus_overpass import build_query, fetch_with_retry, merge_overpass_results, summarize
from scripts.fetch_osm_data import build_manifest, pilot_bbox
from scripts.fetch_hanoi_gtfs import download_file, write_metadata
from scripts.make_supervisor_memo import build_memo
from scripts.audit_pois import audit_pois


def test_motorcycle_calibration_adds_non_raw_travel_time():
    graph = nx.MultiDiGraph()
    graph.add_edge(1, 2, length=1000.0, highway="residential", speed_kph=50.0)

    calibrated = apply_motorcycle_calibration(graph)
    edge = next(iter(calibrated.edges(data=True)))[2]

    assert edge["motorcycle_speed_kph"] != edge["speed_kph"]
    assert edge["motorcycle_travel_time_s"] > 0
    assert "calibration_source" in edge


def test_calibration_table_is_reportable():
    table = calibration_table()
    assert {"highway", "base_speed_kph", "multiplier", "motorcycle_speed_kph"} <= set(table.columns)
    assert "residential" in set(table["highway"])


def test_walk_network_adds_travel_time():
    graph = nx.MultiDiGraph()
    graph.add_edge(1, 2, length=480.0)
    walked = add_walking_travel_times(graph, walk_speed_kph=4.8)
    edge = next(iter(walked.edges(data=True)))[2]
    assert np.isclose(edge["walk_travel_time_s"], 360.0)


def test_pilot_metrics_compute_scenarios_and_typology():
    inputs = pd.DataFrame({
        "cell_id": range(6),
        "NAI": [1, 2, 3, 4, 5, 6],
        "MAI_A": [1, 1, 2, 2, 3, 3],
        "MAI_B": [2, 2, 3, 4, 5, 6],
        "RAC_time_A_raw": [1, 2, 3, 4, 5, 6],
        "RAC_time_B_raw": [2, 3, 4, 5, 6, 7],
        "RAC_opp_A_raw": [1, 2, 1, 2, 1, 2],
        "RAC_opp_B_raw": [2, 3, 2, 4, 3, 5],
    })

    metrics = compute_pilot_metrics(inputs)
    summary = pilot_summary(metrics)

    assert {"SMCI_A", "SMCI_B", "Delta_SMCI", "typology_A", "typology_B"} <= set(metrics.columns)
    assert summary["n_cells"] == 6


def test_validation_helpers_flag_high_vif_and_additive_robustness():
    vif = pd.Series({"NAI": 1.2, "MAI": 8.0, "RAC": 9.0}, name="VIF")
    flags = vif_flags(vif)
    assert flags.loc[flags["variable"] == "MAI", "flag_high_vif"].item()

    summary = robustness_summary(np.array([0.0, 0.1, 0.4, 1.0]), np.array([0.2, 0.3, 0.6, 0.9]))
    assert "spearman_rho_primary_vs_additive" in summary


def test_overpass_query_filters_refs_and_geometry():
    query = build_query(20.85, 105.75, 21.15, 106.05, geom=True, refs="E01,E02,OCP1")
    assert 'relation[route=bus][ref="E01"]' in query
    assert 'relation[route=bus][ref="OCP1"]' in query
    assert "out geom" in query


def test_overpass_429_retry_is_mockable(monkeypatch):
    import scripts.check_vinbus_overpass as mod

    calls = {"n": 0, "sleep": []}

    def fake_fetch(query, endpoint):
        calls["n"] += 1
        if calls["n"] == 1:
            raise HTTPError(endpoint, 429, "Too Many Requests", hdrs=None, fp=None)
        return {"elements": []}

    monkeypatch.setattr(mod, "fetch_overpass", fake_fetch)
    data = fetch_with_retry("query", "endpoint", backoff_seconds=(1,), sleep=lambda seconds: calls["sleep"].append(seconds))
    assert data == {"elements": []}
    assert calls == {"n": 2, "sleep": [1]}


def test_overpass_summary_counts_member_geometry():
    rows = summarize({"elements": [{"type": "relation", "id": 1, "tags": {"ref": "E01"}, "members": [{"geometry": [{"lat": 1, "lon": 2}]}]}]})
    assert rows[0]["has_geometry"]
    assert rows[0]["member_geometry_count"] == 1


def test_overpass_merge_deduplicates_elements():
    merged = merge_overpass_results([
        {"version": 0.6, "elements": [{"type": "relation", "id": 1}]},
        {"version": 0.6, "elements": [{"type": "relation", "id": 1}, {"type": "relation", "id": 2}]},
    ])
    assert [element["id"] for element in merged["elements"]] == [1, 2]


def test_fetch_manifest_shape():
    bbox = pilot_bbox(20.993, 105.945, 2.5)
    manifest = build_manifest(bbox, 20.993, 105.945, 2.5, 250, 1, 2, 3, 4, 5, 6)
    assert manifest["bbox_west_south_east_north"] == list(bbox)
    assert manifest["counts"]["grid_cells"] == 6


def test_accessibility_input_required_columns_and_stale_gtfs_flag():
    inputs = build_proxy_accessibility_inputs([1, 2, 3], [4, 5, 6], gtfs_status="stale")
    validate_accessibility_inputs(inputs)
    assert inputs["MAI_A_baseline_limited"].all()
    assert (inputs["MAI_A"] == 0).all()


def test_gtfs_checker_marks_old_feed_stale(tmp_path):
    gtfs = tmp_path / "gtfs.zip"
    calendar = "service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date\n1,1,1,1,1,1,0,0,20200101,20201231\n"
    with zipfile.ZipFile(gtfs, "w") as zf:
        zf.writestr("calendar.txt", calendar)
    result = inspect_gtfs(gtfs, today=date(2026, 6, 21), stale_years=2)
    assert result["status"] == "baseline_limited"
    assert result["network_b_baseline_limited"]


def test_gtfs_checker_detects_missing_required_files(tmp_path):
    gtfs = tmp_path / "bad_gtfs.zip"
    with zipfile.ZipFile(gtfs, "w") as zf:
        zf.writestr("calendar.txt", "service_id,start_date,end_date\n1,20250101,20251231\n")
    result = inspect_gtfs(gtfs, today=date(2026, 6, 21), stale_years=2)
    assert result["status"] == "baseline_limited"
    assert "routes.txt" in result["missing_required_files"]


def test_gtfs_fetch_does_not_overwrite_existing_file(tmp_path):
    output = tmp_path / "hanoi_gtfs.zip"
    output.write_text("keep", encoding="utf-8")
    downloaded = download_file("https://example.invalid/file.zip", output, force=False)
    assert downloaded is False
    assert output.read_text(encoding="utf-8") == "keep"
    metadata = write_metadata(output, "url", "page", downloaded, tmp_path / "metadata.json")
    assert metadata["downloaded_this_run"] is False


def test_population_resolution_decision():
    assert classify_resolution(100, 250)["decision"] == "allow_fine_grained_proxy"
    assert classify_resolution(1000, 250)["decision"] == "contextual_covariate_only"
    assert classify_resolution(100, 250)["resolution_source"] == "manual_parameter"


def test_poi_audit_detects_duplicate_and_empty_category(tmp_path):
    import geopandas as gpd
    from shapely.geometry import Point

    pois = gpd.GeoDataFrame({
        "name": ["A", "A", "Shop"],
        "amenity": ["school", "school", None],
        "shop": [None, None, "convenience"],
        "leisure": [None, None, None],
    }, geometry=[Point(105.9, 20.9), Point(105.9, 20.9), Point(105.91, 20.91)], crs="EPSG:4326")
    path = tmp_path / "pois.gpkg"
    pois.to_file(path, driver="GPKG")
    counts, duplicates, spot = audit_pois(path, sample_per_category=1)
    assert len(duplicates) == 2
    assert counts.loc[counts["nai_category"] == "park", "empty_category_flag"].item()
    assert "spot_check_status" in spot.columns


def test_supervisor_memo_lists_data_caveats(tmp_path):
    metrics = compute_pilot_metrics(pd.DataFrame({
        "cell_id": range(6),
        "NAI": [1, 2, 3, 4, 5, 6],
        "MAI_A": [1, 1, 2, 2, 3, 3],
        "MAI_B": [2, 2, 3, 4, 5, 6],
        "RAC_time_A_raw": [1, 2, 3, 4, 5, 6],
        "RAC_time_B_raw": [2, 3, 4, 5, 6, 7],
        "RAC_opp_A_raw": [1, 2, 1, 2, 1, 2],
        "RAC_opp_B_raw": [2, 3, 2, 4, 3, 5],
    }))
    metrics_path = tmp_path / "pilot_metrics.csv"
    summary_path = tmp_path / "pilot_summary.csv"
    output_path = tmp_path / "supervisor_memo.md"
    metrics.to_csv(metrics_path, index=False)
    pilot_summary(metrics).to_frame("value").to_csv(summary_path)

    memo = build_memo(metrics_path, summary_path, output_path)
    assert "Unresolved Caveats" in memo
    assert "Confirmed Real Data" in memo
    assert output_path.exists()
