import numpy as np
import pytest

from src.neighborhood_access import (
    category_completeness,
    neighborhood_proximity_time,
    npt_benefit,
    weighted_gini,
    weighted_quantile,
)


def test_category_completeness_and_missing_penalty():
    counts = np.array([[1, 0, 3], [0, 0, 0]])
    assert np.allclose(category_completeness(counts), [2 / 3, 0])
    times = np.array([[3.0, np.nan, 9.0], [np.nan, np.nan, 5.0]])
    assert np.allclose(neighborhood_proximity_time(times, k=2, missing_penalty_min=20), [6, 12.5])


def test_weighted_gini_invariants():
    assert weighted_gini(np.array([2.0, 2.0]), np.array([1.0, 3.0])) == 0.0
    assert np.isclose(weighted_gini(np.array([0.0, 1.0]), np.array([1.0, 1.0])), 0.5)
    with pytest.raises(ValueError):
        weighted_gini(np.array([1.0]), np.array([-1.0]))


def test_npt_k_five_is_explicitly_penalized_when_framework_has_four_categories():
    times = np.array([[2.0, 4.0, 6.0, 8.0]])
    assert np.isclose(
        neighborhood_proximity_time(times, k=5, missing_penalty_min=20, category_slots=5)[0],
        8.0,
    )
    assert np.isclose(npt_benefit(np.array([8.0]), missing_penalty_min=20)[0], 0.6)
    with pytest.raises(ValueError):
        neighborhood_proximity_time(times, k=5)


def test_weighted_quantile_rejects_invalid_weights_and_preserves_endpoints():
    values = np.array([1.0, 3.0, 9.0])
    assert np.allclose(weighted_quantile(values, np.ones(3), np.array([0.0, 1.0])), [1.0, 9.0])
    with pytest.raises(ValueError):
        weighted_quantile(values, np.array([1.0, -1.0, 1.0]), np.array([0.5]))
