from pathlib import Path

import pandas as pd
import pytest

from scripts.make_uncertainty_envelope import load_metric_variant_cells, make_envelope


def test_envelope_uses_per_cell_quantiles_not_aggregate_transforms():
    cells = pd.DataFrame({
        "cell_id": [1, 1], "SMCI_A": [0.1, 0.3], "SMCI_B": [0.2, 0.4], "Delta_SMCI": [0.1, 0.1],
    })
    result = make_envelope(cells)
    assert result.loc[0, "SMCI_B_min"] == 0.2
    assert result.loc[0, "SMCI_B_max"] == 0.4
    assert result.loc[0, "SMCI_B_median"] == pytest.approx(0.3)


def test_envelope_keeps_each_cell_separate():
    cells = pd.DataFrame({"cell_id": [1, 2], "SMCI_A": [0.1, 0.3], "SMCI_B": [0.2, 0.4], "Delta_SMCI": [0.1, 0.1]})
    assert len(make_envelope(cells)) == 2


def test_metric_variant_wide_cells_require_a_b_and_delta(tmp_path: Path):
    path = tmp_path / "variants.csv"
    pd.DataFrame({"cell_id": [1], "example_SMCI_A": [0.1], "example_SMCI_B": [0.2], "example_Delta_SMCI": [0.1]}).to_csv(path, index=False)
    result = load_metric_variant_cells(path)
    assert result.loc[0, "specification"] == "metric_variant:example"
