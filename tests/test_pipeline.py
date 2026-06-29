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

from accessibility_inputs import (
    build_proxy_accessibility_inputs,
    classify_poi_opportunity,
    classify_poi_opportunity_domain,
    population_supply_multiplier,
    validate_accessibility_inputs,
)
from routing import composite_mai_from_graph, weighted_decay_sum, corridor_accessibility
from calibration import apply_motorcycle_calibration, calibration_table
from networks import add_walking_travel_times
from pilot import compute_pilot_metrics, pilot_summary, typology_kappa
from routing import composite_mai_from_graph, corridor_accessibility, weighted_decay_sum
from validation import robustness_summary, vif_flags
from scripts.archive.check_hanoi_gtfs import inspect_gtfs
from scripts.archive.check_population_proxy_resolution import classify_resolution
from scripts.archive.check_vinbus_overpass import build_query, fetch_with_retry, merge_overpass_results, summarize
from scripts.fetch_osm_data import build_manifest, pilot_bbox
from scripts.fetch_hanoi_gtfs import download_file, write_metadata
from scripts.make_supervisor_memo import build_memo
from scripts.audit_pois import audit_pois
from scripts.archive.check_mobility_database import search_catalog


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

def test_pilot_metrics_use_shared_scenario_scale_for_delta():
    inputs = pd.DataFrame({
        "cell_id": range(4),
        "NAI": [1, 2, 3, 4],
        "MAI_A": [1, 2, 3, 4],
        "MAI_B": [2, 3, 4, 5],
        "RAC_time_A_raw": [1, 2, 3, 4],
        "RAC_time_B_raw": [2, 3, 4, 5],
        "RAC_opp_A_raw": [1, 2, 3, 4],
        "RAC_opp_B_raw": [2, 3, 4, 5],
    })

    metrics = compute_pilot_metrics(inputs)

    assert {"NAI_norm", "MAI_A_norm", "MAI_B_norm", "RAC_A_norm", "RAC_B_norm"} <= set(metrics.columns)
    assert (metrics["MAI_B_norm"] >= metrics["MAI_A_norm"]).all()
    assert (metrics["RAC_B_norm"] >= metrics["RAC_A_norm"]).all()
    assert (metrics["Delta_SMCI"] >= 0).all()


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
    import scripts.archive.check_vinbus_overpass as mod

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

def test_mobility_database_search_handles_empty_and_hanoi_match():
    catalog = pd.DataFrame({
        "mdb_source_id": [1, 2],
        "data_type": ["gtfs", "gtfs"],
        "location.country_code": ["VN", "VN"],
        "location.municipality": ["Hanoi", "Da Nang"],
        "provider": ["Example Hanoi Transit", "Other"],
        "name": ["Hanoi GTFS", "Da Nang GTFS"],
        "note": ["", ""],
        "status": ["active", "active"],
        "location.bounding_box.minimum_latitude": [20.9, 16.0],
        "location.bounding_box.maximum_latitude": [21.1, 16.1],
        "location.bounding_box.minimum_longitude": [105.8, 108.0],
        "location.bounding_box.maximum_longitude": [106.0, 108.1],
    })

    hanoi = search_catalog(catalog, "Hanoi", "VN")
    missing_country = search_catalog(catalog, "Hanoi", "LA")

    assert set(hanoi["mdb_source_id"]) == {1}
    assert missing_country.empty


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


def test_classify_poi_opportunity_domain_known_tags():
    assert classify_poi_opportunity_domain({"amenity": "hospital"}) == ("tertiary_healthcare", 1.0)
    assert classify_poi_opportunity_domain({"amenity": "clinic"}) == ("tertiary_healthcare", 0.4)
    assert classify_poi_opportunity_domain({"amenity": "school"}) == ("higher_education", 0.5)
    assert classify_poi_opportunity_domain({"shop": "mall"}) == ("metro_commercial", 1.0)
    assert classify_poi_opportunity_domain({"shop": "supermarket"}) == ("metro_commercial", 0.6)


def test_classify_poi_opportunity_domain_fallback():
    domain, weight = classify_poi_opportunity_domain({"amenity": None, "shop": None})
    assert domain == "metro_commercial"
    assert weight > 0


def test_classify_poi_economic_amenity_tags():
    # Hướng C: financial / market amenities map to economic domain
    assert classify_poi_opportunity_domain({"amenity": "bank"}) == ("economic", 0.6)
    assert classify_poi_opportunity_domain({"amenity": "marketplace"}) == ("economic", 0.8)
    assert classify_poi_opportunity_domain({"amenity": "post_office"}) == ("economic", 0.3)


def test_classify_poi_economic_office_tags():
    # Hướng C: office=* tags map to economic (or higher_education for educational)
    assert classify_poi_opportunity_domain({"office": "company"}) == ("economic", 1.0)
    assert classify_poi_opportunity_domain({"office": "government"}) == ("economic", 0.8)
    assert classify_poi_opportunity_domain({"office": "it"}) == ("economic", 1.0)
    assert classify_poi_opportunity_domain({"office": "yes"}) == ("economic", 0.6)
    assert classify_poi_opportunity_domain({"office": "educational"}) == ("higher_education", 0.7)
    # Unknown office value falls back to economic 0.6
    assert classify_poi_opportunity_domain({"office": "weird_unmapped"}) == ("economic", 0.6)


def test_classify_poi_economic_landuse_uses_capped_area_scaling():
    # Hướng B: landuse weight = base_density × sqrt(area/2000) area multiplier,
    # capped at 5.0 so a single industrial park cannot dominate (Decision #18 fix).
    import numpy as np
    domain, weight = classify_poi_opportunity_domain(
        {"landuse": "commercial", "building_area_m2": 8000.0}
    )
    assert domain == "economic"
    expected = float(np.clip(0.7 * np.sqrt(8000.0 / 2000.0), 0.1, 5.0))  # 0.7 * 2.0 = 1.4
    assert abs(weight - expected) < 1e-6
    # Large industrial zone is capped at 5.0, and industrial density (0.3) < office
    domain2, weight2 = classify_poi_opportunity_domain(
        {"landuse": "industrial", "building_area_m2": 1_000_000.0}
    )
    assert domain2 == "economic"
    assert weight2 <= 5.0  # hard cap prevents domain domination
    # Office land of equal size outweighs industrial of equal size (higher density)
    office_w = classify_poi_opportunity_domain({"landuse": "office", "building_area_m2": 20000.0})[1]
    indus_w = classify_poi_opportunity_domain({"landuse": "industrial", "building_area_m2": 20000.0})[1]
    assert office_w > indus_w


def test_classify_poi_office_precedence_over_generic_fallback():
    # office tag must win over the generic metro_commercial fallback
    domain, _ = classify_poi_opportunity_domain(
        {"amenity": None, "shop": None, "landuse": None, "office": "company"}
    )
    assert domain == "economic"


def test_classify_poi_nan_tags_do_not_force_economic():
    # Regression: float('nan') is truthy, so `str(x or "")` yielded "nan",
    # which made every untagged park/garden fall into the economic branch.
    import numpy as np
    row = {"amenity": np.nan, "shop": np.nan, "office": np.nan, "landuse": np.nan, "name": np.nan}
    domain, weight = classify_poi_opportunity_domain(row)
    assert domain == "metro_commercial"  # generic fallback, NOT economic
    assert weight > 0


def test_classify_poi_office_education_values_map_to_higher_education():
    # OSM tags lecture halls as office=educational_institution/university/research
    assert classify_poi_opportunity_domain({"office": "educational_institution"})[0] == "higher_education"
    assert classify_poi_opportunity_domain({"office": "university"})[0] == "higher_education"
    assert classify_poi_opportunity_domain({"office": "research"})[0] == "higher_education"


def test_classify_poi_education_name_heuristic_rescues_generic_office():
    # office=company but the name says "Giảng đường" (lecture hall) → higher_education
    domain, _ = classify_poi_opportunity_domain(
        {"office": "company", "name": "Giảng đường Nguyễn Đăng"}
    )
    assert domain == "higher_education"


def test_classify_poi_nha_khoa_is_not_education():
    # "Nha khoa" (dentistry) must not be caught by an education keyword.
    # It is a clinic by amenity/healthcare, classified as tertiary_healthcare.
    domain, _ = classify_poi_opportunity_domain(
        {"amenity": "clinic", "name": "Nha Khoa Hải Âu - OceanPark Dental"}
    )
    assert domain == "tertiary_healthcare"


def test_classify_poi_economic_weight_is_bounded_against_domain_domination():
    # Regression for Decision #18 over-correction: a huge industrial polygon must not
    # produce a weight that dwarfs ordinary point POIs (max ~1.0) by an order of magnitude.
    # All economic area-scaled weights are capped at 5.0.
    for area in (50_000.0, 500_000.0, 5_000_000.0, 50_000_000.0):
        _, w_landuse = classify_poi_opportunity_domain(
            {"landuse": "industrial", "building_area_m2": area}
        )
        assert w_landuse <= 5.0, f"industrial landuse weight {w_landuse} exceeds cap at area={area}"
        _, w_office = classify_poi_opportunity_domain(
            {"office": "company", "building_area_m2": area}
        )
        assert w_office <= 5.0, f"office weight {w_office} exceeds cap at area={area}"


def test_classify_poi_industrial_density_below_office():
    # Factories employ fewer people per m² than offices — base density must reflect this.
    _, indus = classify_poi_opportunity_domain({"landuse": "industrial"})
    _, office = classify_poi_opportunity_domain({"landuse": "office"})
    assert indus < office


def test_classify_poi_building_area_string_is_numeric():
    # GeoPackage roundtrips can return synthetic building_area_m2 as string;
    # classifier must coerce it rather than crash on string > int.
    domain, weight = classify_poi_opportunity_domain(
        {"landuse": "commercial", "building_area_m2": "8000.0"}
    )
    assert domain == "economic"
    assert weight > 1.0


def test_population_supply_multiplier_centered_at_median():
    # Decision #19: a POI at the median density gets multiplier ~1.0 (no global inflation).
    dens = np.array([100.0, 200.0, 400.0, 800.0])  # median = 300
    mult = population_supply_multiplier(dens)
    median_dens = float(np.median(dens))
    at_median = population_supply_multiplier(np.array([median_dens]))
    assert np.isclose(at_median[0], 1.0)
    # sqrt-damped: a 4x denser POI than median is sqrt(4)=2x, not 4x (then bounded).
    assert mult[-1] <= 2.0


def test_population_supply_multiplier_bounded():
    # Extreme densities are clipped to [lo, hi]; no POI can dominate via population alone.
    dens = np.array([1.0, 1e9])  # absurdly sparse and absurdly dense vs median
    mult = population_supply_multiplier(dens, lo=0.5, hi=2.0)
    assert mult.min() >= 0.5
    assert mult.max() <= 2.0


def test_population_supply_multiplier_neutral_on_missing():
    # NaN / non-positive density → neutral multiplier 1.0 (POI keeps its base weight).
    dens = np.array([np.nan, 0.0, -5.0])
    mult = population_supply_multiplier(dens)
    assert np.allclose(mult, 1.0)


def test_population_supply_multiplier_all_missing_is_identity():
    # When no density is available at all, weighting is a no-op.
    mult = population_supply_multiplier(np.array([np.nan, np.nan]))
    assert np.allclose(mult, 1.0)


def test_classify_poi_opportunity_domain_unchanged_by_pop_weighting():
    # Regression: population weighting lives OUTSIDE the classifier (it is applied as a
    # separate per-POI factor at assembly). classify_poi tuples must be untouched.
    assert classify_poi_opportunity_domain({"amenity": "hospital"}) == ("tertiary_healthcare", 1.0)
    assert classify_poi_opportunity_domain({"shop": "mall"}) == ("metro_commercial", 1.0)
    assert classify_poi_opportunity_domain({"office": "company"}) == ("economic", 1.0)


def test_classify_poi_opportunity_observed_values_win_over_proxy():
    health = classify_poi_opportunity({"amenity": "hospital", "obs_beds": 100, "building_area_m2": 1000})
    edu = classify_poi_opportunity({"amenity": "university", "obs_enrollment": 2500})
    # economic ref=500 → 200 jobs → weight = clip(200/500, 0.1, 5.0) = 0.4
    econ = classify_poi_opportunity({"office": "company", "obs_jobs": 200})
    retail = classify_poi_opportunity({"shop": "mall", "obs_retail_gla_m2": 3500})

    assert health.domain == "tertiary_healthcare"
    assert health.weight == 2.0
    assert health.opportunity_source == "observed_point"
    assert health.observed_unit == "beds"
    assert edu.weight == 2.5
    # ref=500: 200/500=0.4 (within cap=5.0)
    assert abs(econ.weight - 0.4) < 1e-6
    assert retail.weight == 3.5
    assert retail.opportunity_source == "observed_derived"


def test_classify_poi_opportunity_proxy_basis_reproduces_legacy_tuple():
    row = {"landuse": "commercial", "building_area_m2": 8000.0, "obs_jobs": 5000}
    legacy = classify_poi_opportunity_domain(row)
    proxy = classify_poi_opportunity(row, opportunity_basis="proxy")

    assert (proxy.domain, proxy.weight) == legacy
    assert proxy.opportunity_source == "proxy_area"


def test_classify_poi_opportunity_strict_blocks_missing_observed():
    strict = classify_poi_opportunity({"shop": "mall"}, opportunity_basis="observed_strict")

    assert strict.opportunity_source == "needs_source"
    assert strict.audit_status == "needs_source"
    assert strict.weight == 0.0

def test_classify_poi_opportunity_strict_uses_generic_observed_schema():
    park = classify_poi_opportunity(
        {
            "leisure": "park",
            "obs_magnitude": 12000,
            "obs_unit": "m2_park_or_leisure_area",
            "obs_source_tier": "geometry_measured",
            "obs_audit_status": "geometry_measured",
        },
        opportunity_basis="observed_strict",
    )

    assert park.domain == "metro_commercial"
    assert park.observed_unit == "m2_park_or_leisure_area"
    assert park.opportunity_source == "geometry_measured"
    assert np.isclose(park.weight, 1.2)

def test_classify_poi_opportunity_strict_excludes_non_destination():
    excluded = classify_poi_opportunity(
        {
            "category": "transportation",
            "include_in_mai": False,
            "obs_audit_status": "exclude_not_destination",
            "exclusion_reason": "point-only service listing",
        },
        opportunity_basis="observed_strict",
    )

    assert excluded.opportunity_source == "excluded_not_destination"
    assert excluded.include_in_mai is False
    assert excluded.weight == 0.0

def test_classify_poi_opportunity_falls_back_area_then_tag():
    area = classify_poi_opportunity({"amenity": "hospital", "building_area_m2": 1000.0})
    tag = classify_poi_opportunity({"amenity": "hospital"})

    assert area.opportunity_source == "proxy_area"
    assert area.weight == 2.0
    assert tag.opportunity_source == "proxy_tag"
    assert tag.weight == 1.0


def test_classify_poi_opportunity_observed_caps_and_dasymetric_source():
    # economic ref=500, cap=5.0 — a very large industrial park hits the cap
    capped = classify_poi_opportunity({"office": "company", "obs_jobs": 100000})
    dasymetric = classify_poi_opportunity(
        {"office": "company", "obs_jobs": 100, "obs_source": "GSO_ward_dasymetric"}
    )

    assert capped.weight == 5.0  # cap=5.0 (Decision #18 discipline, ref=500)
    assert dasymetric.opportunity_source == "observed_dasymetric"


def test_weighted_decay_sum_zero_when_all_out_of_range():
    graph = nx.MultiDiGraph()
    graph.add_edge(1, 2, walk_travel_time_s=4000.0)  # >60 min → decay=0
    scores = weighted_decay_sum(graph, [1], [2], [1.0], "walk_travel_time_s")
    assert scores[0] == 0.0


def test_weighted_decay_sum_full_weight_within_threshold():
    graph = nx.MultiDiGraph()
    graph.add_edge(1, 2, walk_travel_time_s=600.0)  # 10 min → decay=1.0
    scores = weighted_decay_sum(graph, [1], [2], [2.5], "walk_travel_time_s")
    assert np.isclose(scores[0], 2.5)


def test_composite_mai_from_graph_sums_domains():
    graph = nx.MultiDiGraph()
    graph.add_edge(1, 2, walk_travel_time_s=600.0)   # 10 min, hospital, full decay
    graph.add_edge(1, 3, walk_travel_time_s=600.0)   # 10 min, mall, full decay
    domains = ["tertiary_healthcare", "metro_commercial"]
    opp_weights = [1.0, 1.0]
    domain_weights = {"economic": 0.0, "higher_education": 0.0,
                      "tertiary_healthcare": 0.5, "metro_commercial": 0.5}
    mai = composite_mai_from_graph(
        graph, [1], [2, 3], domains, opp_weights, "walk_travel_time_s",
        domain_weights=domain_weights
    )
    # Both reachable, full decay: 0.5*1.0 + 0.5*1.0 = 1.0
    assert np.isclose(mai[0], 1.0)


def _pilot_inputs_6():
    return pd.DataFrame({
        "cell_id": range(6),
        "NAI": [1, 2, 3, 4, 5, 6],
        "MAI_A": [1, 1, 2, 2, 3, 3],
        "MAI_B": [2, 2, 3, 4, 5, 6],
        "RAC_time_A_raw": [1, 2, 3, 4, 5, 6],
        "RAC_time_B_raw": [2, 3, 4, 5, 6, 7],
        "RAC_opp_A_raw": [1, 2, 1, 2, 1, 2],
        "RAC_opp_B_raw": [2, 3, 2, 4, 3, 5],
    })


def test_pilot_metrics_includes_rac_time_only_columns():
    metrics = compute_pilot_metrics(_pilot_inputs_6())
    assert "SMCI_B_time_only" in metrics.columns
    assert "typology_B_time_only" in metrics.columns
    valid = {"Integrated Capability", "Fragmented Capability",
             "Transit-Dependent", "Motorcycle Lock-in"}
    assert set(metrics["typology_B_time_only"]) <= valid


def test_typology_kappa_identical_labels_is_one():
    labels = np.array(["Integrated Capability", "Motorcycle Lock-in",
                        "Fragmented Capability", "Transit-Dependent"])
    assert np.isclose(typology_kappa(labels, labels), 1.0)


def test_typology_kappa_different_labels_below_one():
    a = np.array(["Integrated Capability"] * 4)
    b = np.array(["Motorcycle Lock-in", "Integrated Capability",
                  "Transit-Dependent", "Fragmented Capability"])
    assert typology_kappa(a, b) < 1.0


def test_corridor_accessibility_headway_increases_travel_time():
    import geopandas as gpd
    from shapely.geometry import LineString, Point
    corridor = gpd.GeoDataFrame(
        {"relation_id": [1], "ref": ["E01"], "geometry": [LineString([(105.94, 20.99), (105.95, 20.99)])]},
        crs="EPSG:4326"
    )
    grid = gpd.GeoDataFrame(
        {"cell_id": [0]},
        geometry=[Point(105.945, 20.99)],
        crs="EPSG:4326"
    )
    pois = gpd.GeoDataFrame(
        {"amenity": ["hospital"]},
        geometry=[Point(105.947, 20.99)],
        crs="EPSG:4326"
    )
    _, t_10 = corridor_accessibility(grid, pois, corridor, 800.0, 800.0, headway_min=10.0)
    _, t_30 = corridor_accessibility(grid, pois, corridor, 800.0, 800.0, headway_min=30.0)
    # longer headway → longer wait → longer total time
    assert t_30[0] > t_10[0]


def test_corridor_accessibility_default_headway_is_15():
    import geopandas as gpd
    from shapely.geometry import LineString, Point
    corridor = gpd.GeoDataFrame(
        {"relation_id": [1], "ref": ["E01"], "geometry": [LineString([(105.94, 20.99), (105.95, 20.99)])]},
        crs="EPSG:4326"
    )
    grid = gpd.GeoDataFrame({"cell_id": [0]}, geometry=[Point(105.945, 20.99)], crs="EPSG:4326")
    pois = gpd.GeoDataFrame({"amenity": ["hospital"]}, geometry=[Point(105.947, 20.99)], crs="EPSG:4326")
    _, t_default = corridor_accessibility(grid, pois, corridor, 800.0, 800.0)
    _, t_15 = corridor_accessibility(grid, pois, corridor, 800.0, 800.0, headway_min=15.0)
    assert np.isclose(t_default[0], t_15[0])


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


# ---------------------------------------------------------------------------
# WorldPop aggregation tests
# ---------------------------------------------------------------------------

def test_worldpop_aggregation_output_columns(tmp_path):
    """aggregate_worldpop_by_grid returns required columns for all grid cells."""
    import geopandas as gpd
    import rasterio
    from rasterio.transform import from_bounds
    from shapely.geometry import box
    import numpy as np

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    from aggregate_worldpop_by_grid import aggregate_worldpop_by_grid

    # Synthetic 3-cell grid in WGS84
    cells = gpd.GeoDataFrame(
        {"cell_id": [0, 1, 2]},
        geometry=[
            box(105.90, 20.90, 105.91, 20.91),
            box(105.91, 20.90, 105.92, 20.91),
            box(105.92, 20.90, 105.93, 20.91),
        ],
        crs="EPSG:4326",
    )
    grid_path = tmp_path / "grid.gpkg"
    cells.to_file(grid_path, driver="GPKG")

    # Synthetic GeoTIFF covering the area with known population values
    raster_path = tmp_path / "pop.tif"
    transform = from_bounds(105.89, 20.89, 105.94, 20.92, width=50, height=30)
    data = np.full((1, 30, 50), 10.0, dtype=np.float32)
    with rasterio.open(
        raster_path, "w", driver="GTiff",
        height=30, width=50, count=1,
        dtype="float32", crs="EPSG:4326",
        transform=transform, nodata=-99999.0,
    ) as dst:
        dst.write(data)

    result = aggregate_worldpop_by_grid(raster_path, grid_path)

    required = {"cell_id", "pop_sum", "pop_mean", "pop_density_per_km2", "n_valid_pixels"}
    assert required <= set(result.columns), f"Missing columns: {required - set(result.columns)}"
    assert len(result) == 3
    assert (result["pop_sum"] >= 0).all()
    assert (result["n_valid_pixels"] >= 0).all()


def test_worldpop_aggregation_zero_for_nodata_cells(tmp_path):
    """Cells outside raster coverage get pop_sum = 0."""
    import geopandas as gpd
    import rasterio
    from rasterio.transform import from_bounds
    from shapely.geometry import box

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    from aggregate_worldpop_by_grid import aggregate_worldpop_by_grid

    # Grid cell placed OUTSIDE the raster extent
    cells = gpd.GeoDataFrame(
        {"cell_id": [0]},
        geometry=[box(106.50, 21.50, 106.51, 21.51)],
        crs="EPSG:4326",
    )
    grid_path = tmp_path / "grid.gpkg"
    cells.to_file(grid_path, driver="GPKG")

    raster_path = tmp_path / "pop.tif"
    transform = from_bounds(105.90, 20.90, 105.93, 20.93, width=10, height=10)
    import numpy as np
    data = np.full((1, 10, 10), 5.0, dtype=np.float32)
    with rasterio.open(
        raster_path, "w", driver="GTiff",
        height=10, width=10, count=1,
        dtype="float32", crs="EPSG:4326",
        transform=transform, nodata=-99999.0,
    ) as dst:
        dst.write(data)

    result = aggregate_worldpop_by_grid(raster_path, grid_path)
    assert result.loc[0, "pop_sum"] == 0.0
    assert result.loc[0, "n_valid_pixels"] == 0


def test_population_weighted_smci_weights_sum_to_one(tmp_path):
    """Population-weighted SMCI: weights sum to 1.0 by construction."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    from compute_population_weighted_smci import compute_weighted_stats

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
    worldpop = pd.DataFrame({
        "cell_id": range(6),
        "pop_sum": [100.0, 200.0, 150.0, 50.0, 300.0, 200.0],
    })

    stats, df = compute_weighted_stats(metrics, worldpop)
    weights = df["pop_sum"] / df["pop_sum"].sum()
    assert abs(weights.sum() - 1.0) < 1e-9
    assert 0.0 <= stats["popweighted_mean_SMCI_B"] <= 1.0


def test_poi_merge_source_labels(tmp_path):
    """merge_poi_sources correctly labels OSM/Overture/both POIs."""
    import geopandas as gpd
    from shapely.geometry import Point

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    from merge_poi_sources import merge_poi_sources

    # OSM: 2 POIs — one will be matched, one won't
    osm = gpd.GeoDataFrame(
        {"name": ["School", "Hospital"], "amenity": ["school", "hospital"]},
        geometry=[Point(105.900, 20.900), Point(105.910, 20.910)],
        crs="EPSG:4326",
    )
    # Overture: 2 POIs — first within 30m of OSM[0], second is new
    overture = gpd.GeoDataFrame(
        {"name": ["School OV", "Cafe"], "category": ["education", "food_and_beverage"],
         "confidence": [0.9, 0.8]},
        geometry=[Point(105.9001, 20.9001), Point(105.920, 20.920)],
        crs="EPSG:4326",
    )
    osm_path = tmp_path / "osm.gpkg"
    ov_path  = tmp_path / "overture.gpkg"
    osm.to_file(osm_path, driver="GPKG")
    overture.to_file(ov_path, driver="GPKG")

    merged = merge_poi_sources(osm_path, ov_path, match_distance_m=30.0)

    sources = set(merged["source"].unique())
    assert "both" in sources,          "Expected at least one 'both' match"
    assert "osm_only" in sources,      "Expected at least one 'osm_only'"
    assert "overture_only" in sources, "Expected at least one 'overture_only'"
    # Total = OSM (2) + unmatched Overture (1) = 3
    assert len(merged) == 3

def test_built_population_zero_access_classification():
    """Zero-access audit classifies built and suspect cells deterministically."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    from built_population_zero_access_audit import classify_land_use

    assert classify_land_use(pd.Series({"building_count": 1, "pop_sum": 0.0})) == "built"
    assert classify_land_use(pd.Series({"building_count": 0, "pop_sum": 0.2})) == "unbuilt_or_open_space"
    assert classify_land_use(pd.Series({"building_count": 0, "pop_sum": 3.0})) == "suspect_under_mapped"

def test_motorcycle_speed_scenarios_change_target_road_classes():
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    from motorcycle_speed_sensitivity import adjust_motorcycle_calibration

    calibration = pd.DataFrame({
        "highway": ["primary", "secondary", "service"],
        "base_speed_kph": [40.0, 30.0, 10.0],
        "multiplier": [1.0, 1.2, 1.0],
        "motorcycle_speed_kph": [40.0, 36.0, 10.0],
    })

    slow = adjust_motorcycle_calibration(calibration, "slow_congestion")
    fast = adjust_motorcycle_calibration(calibration, "fast_lane_splitting")

    assert slow.loc[slow["highway"] == "primary", "motorcycle_speed_kph"].iloc[0] == 32.0
    assert slow.loc[slow["highway"] == "service", "motorcycle_speed_kph"].iloc[0] == 10.0
    assert fast.loc[fast["highway"] == "secondary", "motorcycle_speed_kph"].iloc[0] > 36.0
    assert fast.loc[fast["highway"] == "primary", "motorcycle_speed_kph"].iloc[0] == 40.0

def test_transit_impedance_penalizes_time_only():
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    from transit_impedance_sensitivity import apply_transit_impedance

    inputs = pd.DataFrame({
        "cell_id": [1, 2],
        "NAI": [1.0, 2.0],
        "MAI_A": [0.5, 0.6],
        "MAI_B": [0.7, 0.8],
        "RAC_time_A_raw": [0.4, 0.5],
        "RAC_time_B_raw": [0.5, 0.6],
        "RAC_opp_A_raw": [0.6, 0.7],
        "RAC_opp_B_raw": [0.8, 0.9],
        "moto_mean_opp_time_min": [12.0, 18.0],
        "wt_B_mean_opp_time_min": [24.0, 30.0],
        "transit_walk_access_min": [4.0, 0.0],
        "transit_wait_min": [6.0, 0.0],
        "transit_linehaul_min": [10.0, 0.0],
        "transit_egress_min": [4.0, 0.0],
    })

    out = apply_transit_impedance(inputs, "conservative")

    assert out.loc[0, "wt_B_mean_opp_time_min"] > inputs.loc[0, "wt_B_mean_opp_time_min"]
    assert out.loc[1, "wt_B_mean_opp_time_min"] == inputs.loc[1, "wt_B_mean_opp_time_min"] + 5.0
    assert out.loc[0, "RAC_time_B_raw"] < inputs.loc[0, "RAC_time_B_raw"]
    assert out["MAI_B"].equals(inputs["MAI_B"])

def test_numeric_bins_separate_zero_from_positive_quantiles():
    """Map quantiles keep zero-access cells out of the positive color ramp."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    from make_pilot_maps import ZERO_COLOR, _numeric_bins, _numeric_color

    _, bins = _numeric_bins(pd.Series([0.0, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5]))

    assert bins.iloc[0] == -1
    assert bins.iloc[1] == -1
    assert _numeric_color(int(bins.iloc[0])) == ZERO_COLOR
    assert set(bins.iloc[2:]).issubset({0, 1, 2, 3, 4})

def test_merged_poi_spot_check_contains_map_url(tmp_path):
    """Overture-only spot-check sheet contains reviewer-friendly coordinates and map URLs."""
    import geopandas as gpd
    from shapely.geometry import Point

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    from merged_poi_sensitivity import make_spot_check

    merged = gpd.GeoDataFrame(
        {
            "name": ["OSM Cafe", "Overture Clinic"],
            "category": ["food", "health"],
            "confidence": [0.8, 0.9],
            "source": ["osm_only", "overture_only"],
        },
        geometry=[Point(105.9, 20.9), Point(105.91, 20.91)],
        crs="EPSG:4326",
    )
    merged_path = tmp_path / "merged.gpkg"
    output = tmp_path / "spot.csv"
    merged.to_file(merged_path, driver="GPKG")

    spot = make_spot_check(merged_path, output)

    assert len(spot) == 1
    assert spot.loc[0, "spot_check_status"] == "unchecked"
    assert "google.com/maps/search" in spot.loc[0, "map_url"]
