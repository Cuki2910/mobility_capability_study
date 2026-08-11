import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import box

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from boundary_discontinuity import attach_boundary_metrics, bootstrap_near_boundary, merge_cell_data, summarize_bands


def _fixture():
    grid = gpd.GeoDataFrame(
        {"cell_id": [1, 2, 3, 4]},
        geometry=[box(-75, -25, -25, 25), box(25, -25, 75, 25), box(125, -25, 175, 25), box(275, -25, 325, 25)],
        crs="EPSG:3857",
    )
    boundary = gpd.GeoDataFrame({"name": ["site"]}, geometry=[box(0, -100, 200, 100)], crs="EPSG:3857")
    metrics = pd.DataFrame({
        "cell_id": [1, 2, 3, 4], "NAI": [0., 2., 4., 0.], "MAI_B": [1., 2., 3., 4.],
        "RAC_B": [1., 2., 3., 4.], "SMCI_B": [0., 2., 4., 0.], "Delta_SMCI": [0., 1., 2., 0.],
        "typology_B": ["F", "I", "I", "M"],
    })
    population = pd.DataFrame({"cell_id": [1, 2, 3, 4], "pop_sum": [1., 1., 3., 1.]})
    return grid, boundary, metrics, population


def test_signed_distance_overlap_and_band_edges():
    grid, boundary, _, _ = _fixture()
    cells = attach_boundary_metrics(grid, boundary)
    by_id = cells.set_index("cell_id")
    assert by_id.loc[1, "signed_distance_m"] < 0
    assert by_id.loc[2, "signed_distance_m"] > 0
    assert by_id.loc[3, "overlap_ratio"] == pytest.approx(1.)
    assert by_id.loc[4, "signed_distance_m"] < 0
    assert set(cells["distance_band"]) == {"inside_0_250m", "outside_0_250m"}


def test_population_weighting_and_sparse_flag():
    grid, boundary, metrics, population = _fixture()
    cells = merge_cell_data(attach_boundary_metrics(grid, boundary), metrics, population)
    summary = summarize_bands(cells, min_cells=3).set_index("distance_band")
    assert summary.loc["inside_0_250m", "SMCI_B_population_weighted"] == pytest.approx(3.5)
    assert bool(summary.loc["inside_0_250m", "sparse_band"])
    assert summary.loc["outside_0_250m", "zero_nai_share"] == 1.


def test_bootstrap_is_deterministic():
    grid, boundary, metrics, population = _fixture()
    cells = merge_cell_data(attach_boundary_metrics(grid, boundary), metrics, population)
    first = bootstrap_near_boundary(cells, metrics=["SMCI_B"], iterations=100, seed=7)
    second = bootstrap_near_boundary(cells, metrics=["SMCI_B"], iterations=100, seed=7)
    pd.testing.assert_frame_equal(first, second)


def test_duplicate_and_mismatched_cell_ids_fail():
    grid, boundary, metrics, population = _fixture()
    duplicate = grid.copy()
    duplicate.loc[1, "cell_id"] = 1
    with pytest.raises(ValueError, match="unique"):
        attach_boundary_metrics(duplicate, boundary)
    with pytest.raises(ValueError, match="do not match"):
        merge_cell_data(attach_boundary_metrics(grid, boundary), metrics.iloc[:-1], population)


def test_missing_crs_fails():
    grid, boundary, _, _ = _fixture()
    grid = grid.set_crs(None, allow_override=True)
    with pytest.raises(ValueError, match="defined CRS"):
        attach_boundary_metrics(grid, boundary)
