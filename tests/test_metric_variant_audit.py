import numpy as np
import pandas as pd

from scripts.metric_variant_audit import compute_variant


def test_metric_variant_emits_geometric_a_b_and_delta_cells():
    base = pd.DataFrame({
        "cell_id": [1, 2, 3, 4],
        "MAI_A": [1.0, 2.0, 3.0, 4.0], "MAI_B": [2.0, 3.0, 4.0, 5.0],
        "RAC_time_A_raw": [2.0, 1.0, 4.0, 3.0], "RAC_time_B_raw": [3.0, 1.0, 5.0, 2.0],
        "RAC_opp_A_raw": [4.0, 2.0, 1.0, 3.0], "RAC_opp_B_raw": [5.0, 3.0, 1.0, 4.0],
    })
    _, cells = compute_variant(base, np.array([1.0, 2.0, 3.0, 4.0]), "example")
    assert {"example_SMCI_A", "example_SMCI_B", "example_Delta_SMCI"}.issubset(cells.columns)
    assert np.allclose(cells["example_Delta_SMCI"], cells["example_SMCI_B"] - cells["example_SMCI_A"])
