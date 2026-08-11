import pandas as pd

from scripts.find_west_taymo_matching_candidates import matching_bounds, rank_candidates


def test_matching_bounds_use_preregistered_plus_minus_15_percent():
    assert matching_bounds(16.0) == (13.6, 18.4)


def test_rank_candidates_keeps_only_cells_inside_matching_band():
    candidates = pd.DataFrame(
        {
            "cell_id": [1, 2, 3],
            "drive_distance_km": [13.5, 15.0, 18.5],
        }
    )
    result = rank_candidates(candidates, reference_km=16.0)
    assert result["cell_id"].tolist() == [2]
    assert result.iloc[0]["ratio_to_ocean_park"] == 0.9375
