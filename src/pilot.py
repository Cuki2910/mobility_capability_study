"""Pilot metric assembly for Ocean Park Scenario A/B analysis."""
from __future__ import annotations

import pandas as pd

import numpy as np

try:
    from .accessibility import (
        compute_rac_shared,
        compute_smci_additive_from_normalized,
        compute_smci_from_normalized,
        metropolitan_competitiveness_score_from_normalized,
        norm01,
        norm01_with_bounds,
        shared_minmax,
        theory_first_typology,
    )
except ImportError:  # pragma: no cover
    from accessibility import (
        compute_rac_shared,
        compute_smci_additive_from_normalized,
        compute_smci_from_normalized,
        metropolitan_competitiveness_score_from_normalized,
        norm01,
        norm01_with_bounds,
        shared_minmax,
        theory_first_typology,
    )


REQUIRED_COLUMNS = {
    "cell_id",
    "NAI",
    "MAI_A",
    "MAI_B",
    "RAC_time_A_raw",
    "RAC_time_B_raw",
    "RAC_opp_A_raw",
    "RAC_opp_B_raw",
}


def compute_pilot_metrics(inputs: pd.DataFrame) -> pd.DataFrame:
    """
    Compute Scenario A/B NAI, MAI, RAC, MCS, SMCI, Delta_SMCI, typology.

    Inputs are already accessibility-ready per grid cell. Network construction
    scripts are responsible for producing these raw columns from real data.
    """
    missing = REQUIRED_COLUMNS - set(inputs.columns)
    if missing:
        raise ValueError(f"Pilot input missing columns: {sorted(missing)}")

    out = inputs.copy()
    rac_shared = compute_rac_shared(
        out["RAC_time_A_raw"].to_numpy(),
        out["RAC_opp_A_raw"].to_numpy(),
        out["RAC_time_B_raw"].to_numpy(),
        out["RAC_opp_B_raw"].to_numpy(),
    )
    rac_a = rac_shared["A"]
    rac_b = rac_shared["B"]

    for key, values in rac_a.items():
        out[f"{key}_A"] = values
    for key, values in rac_b.items():
        out[f"{key}_B"] = values

    mai_lo, mai_hi = shared_minmax(out["MAI_A"].to_numpy(), out["MAI_B"].to_numpy())
    rac_lo, rac_hi = shared_minmax(out["RAC_A"].to_numpy(), out["RAC_B"].to_numpy())

    out["NAI_norm"] = norm01(out["NAI"].to_numpy())
    out["MAI_A_norm"] = norm01_with_bounds(out["MAI_A"].to_numpy(), mai_lo, mai_hi)
    out["MAI_B_norm"] = norm01_with_bounds(out["MAI_B"].to_numpy(), mai_lo, mai_hi)
    out["RAC_A_norm"] = norm01_with_bounds(out["RAC_A"].to_numpy(), rac_lo, rac_hi)
    out["RAC_B_norm"] = norm01_with_bounds(out["RAC_B"].to_numpy(), rac_lo, rac_hi)

    out["MCS_A"] = metropolitan_competitiveness_score_from_normalized(out["MAI_A_norm"].to_numpy(), out["RAC_A_norm"].to_numpy())
    out["MCS_B"] = metropolitan_competitiveness_score_from_normalized(out["MAI_B_norm"].to_numpy(), out["RAC_B_norm"].to_numpy())
    out["SMCI_A"] = compute_smci_from_normalized(out["NAI_norm"].to_numpy(), out["MAI_A_norm"].to_numpy(), out["RAC_A_norm"].to_numpy())
    out["SMCI_B"] = compute_smci_from_normalized(out["NAI_norm"].to_numpy(), out["MAI_B_norm"].to_numpy(), out["RAC_B_norm"].to_numpy())
    out["SMCI_additive_A"] = compute_smci_additive_from_normalized(out["NAI_norm"].to_numpy(), out["MAI_A_norm"].to_numpy(), out["RAC_A_norm"].to_numpy())
    out["SMCI_additive_B"] = compute_smci_additive_from_normalized(out["NAI_norm"].to_numpy(), out["MAI_B_norm"].to_numpy(), out["RAC_B_norm"].to_numpy())
    out["Delta_SMCI"] = out["SMCI_B"] - out["SMCI_A"]
    out["typology_A"] = theory_first_typology(out["NAI"].to_numpy(), out["MCS_A"].to_numpy())
    out["typology_B"] = theory_first_typology(out["NAI"].to_numpy(), out["MCS_B"].to_numpy())

    # RAC_time-only sensitivity (VIF contingency per Decision #3).
    # Uses only the time subcomponent — drops RAC_opp entirely.
    time_lo, time_hi = shared_minmax(out["RAC_time_A_raw"].to_numpy(), out["RAC_time_B_raw"].to_numpy())
    rt_a_only = norm01_with_bounds(out["RAC_time_A_raw"].to_numpy(), time_lo, time_hi)
    rt_b_only = norm01_with_bounds(out["RAC_time_B_raw"].to_numpy(), time_lo, time_hi)
    rac_a_lo, rac_a_hi = shared_minmax(rt_a_only, rt_b_only)
    rt_a_norm = norm01_with_bounds(rt_a_only, rac_a_lo, rac_a_hi)
    rt_b_norm = norm01_with_bounds(rt_b_only, rac_a_lo, rac_a_hi)
    mcs_b_time_only = metropolitan_competitiveness_score_from_normalized(out["MAI_B_norm"].to_numpy(), rt_b_norm)
    out["SMCI_B_time_only"] = compute_smci_from_normalized(out["NAI_norm"].to_numpy(), out["MAI_B_norm"].to_numpy(), rt_b_norm)
    out["typology_B_time_only"] = theory_first_typology(out["NAI"].to_numpy(), mcs_b_time_only)

    return out


def typology_kappa(labels_a: np.ndarray, labels_b: np.ndarray) -> float:
    """Cohen's kappa between two typology label arrays."""
    from sklearn.metrics import cohen_kappa_score
    return float(cohen_kappa_score(labels_a, labels_b))


def pilot_summary(metrics: pd.DataFrame) -> pd.Series:
    """Compact supervisor-facing summary of pilot results."""
    return pd.Series({
        "n_cells": int(len(metrics)),
        "mean_SMCI_A": float(metrics["SMCI_A"].mean()),
        "mean_SMCI_B": float(metrics["SMCI_B"].mean()),
        "mean_Delta_SMCI": float(metrics["Delta_SMCI"].mean()),
        "share_improved": float((metrics["Delta_SMCI"] > 0).mean()),
    })
