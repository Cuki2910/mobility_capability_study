"""Regression checks for analytical safeguards in the generated map."""
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "scripts" / "make_interactive_map.py"


def test_map_uses_primary_nai_spec_and_exact_study_boundary():
    source = SOURCE.read_text(encoding="utf-8")
    assert "study_boundary_geom = unary_union(grid.geometry)" in source
    assert "study_union.convex_hull" not in source


def test_map_preserves_missing_values_and_uses_dedicated_delta_scale():
    source = SOURCE.read_text(encoding="utf-8")
    assert "return None if pd.isna(v) else float(v)" in source
    assert "DELTA_EPSILON = 1e-10" in source
    assert 'shared_visual_bounds(grid_features, "Delta_raw", diverging=True)' in source
    assert "gridMode === 'delta' ? DELTA : VIRIDIS" in source


def test_map_precomputes_population_and_project_boundary_attributes():
    source = SOURCE.read_text(encoding="utf-8")
    for field in (
        "share_inside_project",
        "boundary_side",
        "distance_to_boundary_m",
        "boundary_band",
        "population_density",
        "population_exposure",
        "data_quality_grade",
    ):
        assert field in source


def test_map_represents_typology_difference_as_a_transition():
    source = SOURCE.read_text(encoding="utf-8")
    assert "def typology_transition" in source
    assert '"Moved toward Integrated Capability"' in source
    assert '"Changed between intermediate classes"' in source


def test_map_implements_scenario_aware_controls_and_shareable_state():
    source = SOURCE.read_text(encoding="utf-8")
    for token in (
        "differenceOption.disabled = gridMode === 'nai'",
        "typology_transition",
        "updateUrlState",
        "data-preset=",
        "fit-study",
        "Fit project boundary",
        "population_exposure",
        "Boundary fragmentation",
    ):
        assert token in source


def test_map_uses_progressive_disclosure_for_non_primary_controls():
    source = SOURCE.read_text(encoding="utf-8")
    for token in (
        'id="primary-controls"',
        'id="advanced-layers"',
        'id="advanced-diagnostics"',
        'id="map-method-notes"',
        "Quick views",
        "Reset view",
    ):
        assert token in source


def test_map_has_quality_view_and_selected_cell_comparison_bars():
    source = SOURCE.read_text(encoding="utf-8")
    for token in (
        '"quality": {"label": "Data quality grade"',
        "data_quality_grade",
        "function comparisonBar",
        "function componentBar",
        "Scenario comparison",
        "Scenario B component balance",
    ):
        assert token in source
