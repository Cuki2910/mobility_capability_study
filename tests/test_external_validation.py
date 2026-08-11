from pathlib import Path

import pandas as pd
import pytest

from scripts.external_validation import (
    REQUIRED,
    completed_android_motorcycle_observations,
    motorcycle_error_metrics,
)


def test_external_validation_contract_requires_all_fields(tmp_path: Path):
    path = tmp_path / "observations.csv"
    pd.DataFrame({"cell_id": [1]}).to_csv(path, index=False)
    frame = pd.read_csv(path)
    assert [column for column in REQUIRED if column not in frame]


def test_external_validation_template_is_header_only():
    template = Path(__file__).resolve().parents[1] / "data/raw/external_validation_template.csv"
    assert pd.read_csv(template).empty


def test_completed_android_observations_require_audited_od_fields():
    frame = pd.DataFrame(
        {
            "sample_id": [1],
            "origin_lat": [20.99],
            "origin_lon": [105.94],
            "destination_lat": [20.98],
            "destination_lon": [105.95],
            "google_maps_android_minutes": [8.0],
            "android_lookup_date": ["2026-06-22"],
            "android_check_status": ["done"],
        }
    )
    result = completed_android_motorcycle_observations(frame)
    assert len(result) == 1


def test_motorcycle_error_metrics_use_exact_od_model_times():
    frame = pd.DataFrame(
        {
            "google_maps_android_minutes": [10.0, 20.0],
            "model_motorcycle_minutes": [8.0, 23.0],
        }
    )
    metrics = motorcycle_error_metrics(frame)
    assert metrics == {"n": 2, "mae_min": 2.5, "mape_pct": 17.5, "mbe_min": 0.5, "rmse_min": 2.54951}
