"""New specifications change behavior without restoring historical defaults."""
import json

import numpy as np
import pandas as pd

from src.pilot import compute_pilot_metrics
from src.site_config import load_analytical_spec


def test_new_spec_controls_compensation_and_rac(tmp_path, monkeypatch):
    config = tmp_path / "pipeline.json"
    spec = {"nai_primary_threshold_m": 1000, "smci_primary_operator": "additive", "rac_primary": "time", "opportunity_basis": "observed_strict"}
    config.write_text(json.dumps({"analytical_spec": spec}))
    spec = load_analytical_spec(config)
    import src.pilot as pilot
    monkeypatch.setattr(pilot, "load_analytical_spec", lambda: spec)
    inputs = pd.DataFrame({
        "cell_id": range(4), "NAI": [1, 0, 2, 3],
        "MAI_A": [1, 2, 3, 4], "MAI_B": [4, 3, 2, 1],
        "RAC_time_A_raw": [1, 2, 3, 4], "RAC_time_B_raw": [2, 3, 4, 5],
        "RAC_opp_A_raw": [4, 3, 2, 1], "RAC_opp_B_raw": [5, 4, 3, 2],
    })
    additive = compute_pilot_metrics(inputs)
    geometric = compute_pilot_metrics(inputs, {**spec, "smci_primary_operator": "equal_weight_geometric_mean"})
    assert np.isclose(additive.loc[1, "SMCI_B"], 7 / 18)
    assert geometric.loc[1, "SMCI_B"] == 0
    assert set(additive.smci_operator) == {"additive"}
    full = compute_pilot_metrics(inputs, {**spec, "rac_primary": "full"})
    assert np.allclose(full.RAC_B, full.RAC_full_B)
    assert not np.allclose(full.RAC_B, additive.RAC_B)


def test_invalid_threshold_rejected(tmp_path):
    config = tmp_path / "pipeline.json"
    config.write_text(json.dumps({"analytical_spec": {"nai_primary_threshold_m": -1}}))
    try:
        load_analytical_spec(config)
    except ValueError as error:
        assert "positive" in str(error)
    else:
        raise AssertionError("invalid threshold accepted")
