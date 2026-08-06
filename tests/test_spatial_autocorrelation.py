import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pytest
from shapely.geometry import box

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from spatial_autocorrelation import build_weights, classify_local_quadrants, run_spatial_autocorrelation


def _grid() -> gpd.GeoDataFrame:
    geometries = [box(x, y, x + 1, y + 1) for y in range(3) for x in range(3)]
    return gpd.GeoDataFrame(
        {"cell_id": list(range(9)), "value": [9, 8, 1, 8, 7, 1, 1, 1, 0]},
        geometry=geometries,
        crs="EPSG:3857",
    )


def test_weights_have_expected_neighbourhood_shapes():
    cells = _grid()
    queen = build_weights(cells, "queen")
    rook = build_weights(cells, "rook")
    knn = build_weights(cells, "knn", k=2)
    assert len(queen.neighbors[4]) == 8
    assert len(rook.neighbors[4]) == 4
    assert len(knn.neighbors[4]) == 2


def test_cluster_labels_hide_non_significant_cells():
    labels = classify_local_quadrants(np.array([1, 2, 3, 4]), np.array([True, False, True, True]))
    assert labels.tolist() == ["High-High", "Not Significant", "Low-Low", "High-Low"]


def test_spatial_results_are_deterministic_with_fixed_seed():
    first = run_spatial_autocorrelation(_grid(), metrics=["value"], weight_specs=["queen"], permutations=99, seed=7)
    second = run_spatial_autocorrelation(_grid(), metrics=["value"], weight_specs=["queen"], permutations=99, seed=7)
    assert first.global_summary.equals(second.global_summary)
    assert first.cell_results.drop(columns="geometry").equals(second.cell_results.drop(columns="geometry"))


def test_constant_metric_is_rejected():
    cells = _grid().assign(value=1.0)
    with pytest.raises(ValueError, match="constant"):
        run_spatial_autocorrelation(cells, metrics=["value"], permutations=99)
