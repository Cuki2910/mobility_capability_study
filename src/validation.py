"""Validation checks from proposal/proposal_v6.docx Sections 3.9 and 3.11."""
from __future__ import annotations

import numpy as np
import pandas as pd
from statsmodels.stats.outliers_influence import variance_inflation_factor


def collinearity_check(df: pd.DataFrame, cols=("NAI", "MAI", "RAC")) -> pd.Series:
    """
    Section 3.9: VIF among NAI, MAI, RAC.

    If VIF > 5 for MAI or RAC, the proposal contingency is to report RAC using
    RAC_time only. This function reports the diagnostic; it does not change the
    primary formula.
    """
    X = df[list(cols)].astype(float).values
    vifs = {c: variance_inflation_factor(X, i) for i, c in enumerate(cols)}
    return pd.Series(vifs, name="VIF")


def correlation_matrix(df: pd.DataFrame, cols=("NAI", "MAI", "RAC")) -> pd.DataFrame:
    """Pairwise Pearson correlation matrix for index diagnostics."""
    return df[list(cols)].astype(float).corr()


def vif_flags(vif: pd.Series, threshold: float = 5.0) -> pd.DataFrame:
    """Flag variables whose VIF exceeds the proposal threshold."""
    out = vif.rename("VIF").reset_index().rename(columns={"index": "variable"})
    out["threshold"] = threshold
    out["flag_high_vif"] = out["VIF"] > threshold
    return out


def robustness_summary(primary: np.ndarray, additive: np.ndarray) -> pd.Series:
    """Compare primary multiplicative SMCI with the additive robustness index."""
    from scipy.stats import spearmanr

    rho, p_value = spearmanr(primary, additive)
    return pd.Series({
        "spearman_rho_primary_vs_additive": float(rho),
        "p_value": float(p_value),
    })


def network_validation_sample(n_pairs: int = 10) -> pd.DataFrame:
    """
    Blank motorcycle validation template (fallback only).

    The real template with pre-computed model_motorcycle_minutes and named
    OD pairs is at outputs/validation/manual_motorcycle_validation_template.csv.
    This function produces a blank skeleton used only when that file is absent.
    Fill google_maps_android_minutes via Android Google Maps motorcycle mode
    (do NOT use the programmatic TWO_WHEELER API — unconfirmed for Vietnam).
    """
    return pd.DataFrame({
        "sample_id": range(n_pairs),
        "origin_name": [None] * n_pairs,
        "origin_lat": [np.nan] * n_pairs,
        "origin_lon": [np.nan] * n_pairs,
        "destination_name": [None] * n_pairs,
        "destination_lat": [np.nan] * n_pairs,
        "destination_lon": [np.nan] * n_pairs,
        "model_motorcycle_minutes": [np.nan] * n_pairs,
        "google_maps_android_minutes": [np.nan] * n_pairs,
        "abs_error_minutes": [np.nan] * n_pairs,
        "pct_error": [np.nan] * n_pairs,
        "measurement_notes": ["manual consumer-app lookup required"] * n_pairs,
        "validation_notes": [""] * n_pairs,
    })


def external_validation_proxies() -> pd.DataFrame:
    """Empty template for property-value and population-density proxy tracking."""
    return pd.DataFrame(columns=["proxy", "source", "status", "notes"])
