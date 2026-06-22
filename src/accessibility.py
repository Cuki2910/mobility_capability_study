"""
src/accessibility.py

Core index formulas for the Fragmented Mobility Capability framework.
These are the SAME formulas specified in proposal/proposal_v6.docx,
Section 3.6-3.8 — kept in one place so the proposal text and the code
can never silently drift apart.

Import this module from scripts/ and notebooks/; do not re-implement
these formulas inline elsewhere.
"""
import numpy as np


def norm01(x: np.ndarray) -> np.ndarray:
    """Min-max normalize an array to [0, 1]. Primary normalization per Section 3.7-3.8."""
    x = np.asarray(x, dtype=float)
    lo, hi = x.min(), x.max()
    if hi == lo:
        return np.zeros_like(x)
    return (x - lo) / (hi - lo)


def compute_rac(rac_time_raw: np.ndarray, rac_opp_raw: np.ndarray) -> dict:
    """
    Relative Accessibility Competitiveness (Section 3.7).

    rac_time_raw = motorcycle_travel_time / walk_transit_travel_time   (higher = transit faster)
    rac_opp_raw  = opportunities_walk_transit / opportunities_motorcycle (higher = transit reaches more)

    Both are min-max normalized, then combined as a geometric mean so that
    a very low value on either sub-index pulls the composite down (a transit
    system that is fast but reaches almost nothing should NOT score well).
    """
    rt = norm01(rac_time_raw)
    ro = norm01(rac_opp_raw)
    rac = np.sqrt(rt * ro)
    return {"RAC_time": rt, "RAC_opp": ro, "RAC": rac}


def compute_smci(nai: np.ndarray, mai: np.ndarray, rac: np.ndarray) -> np.ndarray:
    """
    Sustainable Mobility Capability Index (Section 3.8), PRIMARY specification.
    SMCI = NAI_norm * MAI_norm * RAC_norm  (multiplicative — a "weakest link" index).

    NOTE — lesson learned 2026-06-21 (see docs/decisions.md #4):
    Do NOT validate this against a geometric-mean alternative
    (NAI*MAI*RAC)**(1/3) — that is a monotonic transform of the product
    itself and will ALWAYS give Spearman rho = 1.0. It tests nothing.
    Use `compute_smci_additive` below for the real robustness comparison.
    """
    return norm01(nai) * norm01(mai) * norm01(rac)


def compute_smci_additive(nai: np.ndarray, mai: np.ndarray, rac: np.ndarray) -> np.ndarray:
    """Additive alternative for the SMCI robustness check (replaces the vacuous geometric-mean check)."""
    return (norm01(nai) + norm01(mai) + norm01(rac)) / 3


def metropolitan_competitiveness_score(mai: np.ndarray, rac: np.ndarray) -> np.ndarray:
    """MCS (Section 3.10) = geometric mean of normalized MAI and RAC, used for theory-first classification."""
    return np.sqrt(norm01(mai) * norm01(rac))


def theory_first_typology(nai: np.ndarray, mcs: np.ndarray) -> np.ndarray:
    """
    Primary classification (Section 3.10): median-split NAI x median-split MCS
    -> exactly 4 named typologies, by construction (not data-dependent k).

    Uses rank-based (ordinal) split to guarantee all 4 typologies appear even
    when MCS has a large point mass at 0 (e.g. baseline_limited GTFS pilot).
    With continuous data, rank-based and value-based splits are equivalent.
    """
    n = len(nai)
    nai_rank = np.argsort(np.argsort(nai, kind="stable"), kind="stable")
    mcs_rank = np.argsort(np.argsort(mcs, kind="stable"), kind="stable")
    nai_hi = nai_rank >= n // 2
    mcs_hi = mcs_rank >= n // 2
    labels = np.empty(n, dtype=object)
    labels[nai_hi & mcs_hi] = "Integrated Capability"
    labels[nai_hi & ~mcs_hi] = "Fragmented Capability"
    labels[~nai_hi & mcs_hi] = "Transit-Dependent"
    labels[~nai_hi & ~mcs_hi] = "Motorcycle Lock-in"
    return labels
