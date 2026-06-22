"""Pilot metric assembly for Ocean Park Scenario A/B analysis."""
from __future__ import annotations

import pandas as pd

try:
    from .accessibility import (
        compute_rac,
        compute_smci,
        compute_smci_additive,
        metropolitan_competitiveness_score,
        theory_first_typology,
    )
except ImportError:  # pragma: no cover
    from accessibility import (
        compute_rac,
        compute_smci,
        compute_smci_additive,
        metropolitan_competitiveness_score,
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
    rac_a = compute_rac(out["RAC_time_A_raw"].to_numpy(), out["RAC_opp_A_raw"].to_numpy())
    rac_b = compute_rac(out["RAC_time_B_raw"].to_numpy(), out["RAC_opp_B_raw"].to_numpy())

    for key, values in rac_a.items():
        out[f"{key}_A"] = values
    for key, values in rac_b.items():
        out[f"{key}_B"] = values

    out["MCS_A"] = metropolitan_competitiveness_score(out["MAI_A"].to_numpy(), out["RAC_A"].to_numpy())
    out["MCS_B"] = metropolitan_competitiveness_score(out["MAI_B"].to_numpy(), out["RAC_B"].to_numpy())
    out["SMCI_A"] = compute_smci(out["NAI"].to_numpy(), out["MAI_A"].to_numpy(), out["RAC_A"].to_numpy())
    out["SMCI_B"] = compute_smci(out["NAI"].to_numpy(), out["MAI_B"].to_numpy(), out["RAC_B"].to_numpy())
    out["SMCI_additive_A"] = compute_smci_additive(out["NAI"].to_numpy(), out["MAI_A"].to_numpy(), out["RAC_A"].to_numpy())
    out["SMCI_additive_B"] = compute_smci_additive(out["NAI"].to_numpy(), out["MAI_B"].to_numpy(), out["RAC_B"].to_numpy())
    out["Delta_SMCI"] = out["SMCI_B"] - out["SMCI_A"]
    out["typology_A"] = theory_first_typology(out["NAI"].to_numpy(), out["MCS_A"].to_numpy())
    out["typology_B"] = theory_first_typology(out["NAI"].to_numpy(), out["MCS_B"].to_numpy())
    return out


def pilot_summary(metrics: pd.DataFrame) -> pd.Series:
    """Compact supervisor-facing summary of pilot results."""
    return pd.Series({
        "n_cells": int(len(metrics)),
        "mean_SMCI_A": float(metrics["SMCI_A"].mean()),
        "mean_SMCI_B": float(metrics["SMCI_B"].mean()),
        "mean_Delta_SMCI": float(metrics["Delta_SMCI"].mean()),
        "share_improved": float((metrics["Delta_SMCI"] > 0).mean()),
    })
