"""
src/accessibility.py

Core index formulas for the Fragmented Mobility Capability framework.
Current methods are described in proposal/proposal_v7.md, Sections 7-10.
Keep implementation and the corresponding proposal methods together so they
can never silently drift apart.

Import this module from scripts/ and notebooks/; do not re-implement
these formulas inline elsewhere.
"""
import numpy as np

# MAI v8 domain weights (Decision #12). Keys match classify_poi_opportunity_domain() output.
# "default" is a theory-informed prior (employment-centrality), not raw revealed-demand.
# "utm_derived" is survey-informed from UTM-Hanoi trip-purpose counts and retained
# as sensitivity unless the paper explicitly decides to promote it.
# Robustness across schemes is strong (metric audit: equal/job_heavy/econ_light all κ≥0.92).
MAI_DOMAIN_WEIGHTS = {
    "default":   {"economic": 0.40, "higher_education": 0.20, "tertiary_healthcare": 0.20, "metro_commercial": 0.20},
    "equal":     {"economic": 0.25, "higher_education": 0.25, "tertiary_healthcare": 0.25, "metro_commercial": 0.25},
    "job_heavy": {"economic": 0.50, "higher_education": 0.15, "tertiary_healthcare": 0.15, "metro_commercial": 0.20},
    "econ_light": {"economic": 0.20, "higher_education": 0.30, "tertiary_healthcare": 0.30, "metro_commercial": 0.20},
    "service_health_heavy": {"economic": 0.25, "higher_education": 0.25, "tertiary_healthcare": 0.30, "metro_commercial": 0.20},
    "utm_derived": {"economic": 0.6885, "higher_education": 0.2043, "tertiary_healthcare": 0.0198, "metro_commercial": 0.0874},
}


def time_decay_linear(t_min: np.ndarray, t_full: float = 30.0, t_zero: float = 60.0) -> np.ndarray:
    """
    Thresholded linear decay (MAI v8, Decision #12).

    f(t) = 1                              if t <= t_full
         = (t_zero-t)/(t_zero-t_full)    if t_full < t <= t_zero
         = 0                              if t > t_zero

    t_min: travel time in minutes.
    """
    t = np.asarray(t_min, dtype=float)
    return np.where(
        t <= t_full, 1.0,
        np.where(t <= t_zero, (t_zero - t) / (t_zero - t_full), 0.0),
    )

def time_decay_exponential(t_min: np.ndarray, half_life_min: float = 30.0, t_zero: float = 60.0) -> np.ndarray:
    """
    Exponential MAI decay robustness variant.

    Uses a half-life so access decays smoothly instead of breaking at t_full,
    while still truncating beyond t_zero to preserve the metropolitan catchment.
    """
    t = np.asarray(t_min, dtype=float)
    half_life = max(float(half_life_min), 1e-9)
    decay = np.exp(-np.log(2.0) * t / half_life)
    return np.where(t <= t_zero, decay, 0.0)


def norm01(x: np.ndarray) -> np.ndarray:
    """Min-max normalize an array to [0, 1]. Primary normalization per Section 3.7-3.8."""
    x = np.asarray(x, dtype=float)
    lo, hi = x.min(), x.max()
    if hi == lo:
        return np.zeros_like(x)
    return (x - lo) / (hi - lo)

def norm01_with_bounds(x: np.ndarray, lo: float, hi: float) -> np.ndarray:
    """Min-max normalize an array against explicit bounds, used for shared Scenario A/B scaling."""
    x = np.asarray(x, dtype=float)
    if hi == lo:
        return np.zeros_like(x)
    return (x - lo) / (hi - lo)

def shared_minmax(*arrays: np.ndarray) -> tuple[float, float]:
    """Return common min/max over multiple arrays so scenario deltas use the same scale."""
    combined = np.concatenate([np.asarray(arr, dtype=float) for arr in arrays])
    return float(combined.min()), float(combined.max())


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

def compute_rac_shared(
    rac_time_a_raw: np.ndarray,
    rac_opp_a_raw: np.ndarray,
    rac_time_b_raw: np.ndarray,
    rac_opp_b_raw: np.ndarray,
) -> dict:
    """
    Compute Scenario A/B RAC on shared min-max scales.

    Scenario deltas are not interpretable if A and B are normalized separately.
    This function normalizes each RAC subcomponent against common A+B bounds,
    then forms the RAC composite for each scenario.
    """
    time_lo, time_hi = shared_minmax(rac_time_a_raw, rac_time_b_raw)
    opp_lo, opp_hi = shared_minmax(rac_opp_a_raw, rac_opp_b_raw)
    rt_a = norm01_with_bounds(rac_time_a_raw, time_lo, time_hi)
    rt_b = norm01_with_bounds(rac_time_b_raw, time_lo, time_hi)
    ro_a = norm01_with_bounds(rac_opp_a_raw, opp_lo, opp_hi)
    ro_b = norm01_with_bounds(rac_opp_b_raw, opp_lo, opp_hi)
    return {
        "A": {"RAC_time": rt_a, "RAC_opp": ro_a, "RAC": np.sqrt(rt_a * ro_a)},
        "B": {"RAC_time": rt_b, "RAC_opp": ro_b, "RAC": np.sqrt(rt_b * ro_b)},
        "bounds": {"RAC_time": (time_lo, time_hi), "RAC_opp": (opp_lo, opp_hi)},
    }


def compute_smci_product(nai: np.ndarray, mai: np.ndarray, rac: np.ndarray) -> np.ndarray:
    """
    Legacy product-form Sustainable Mobility Capability Index.
    SMCI = NAI_norm * MAI_norm * RAC_norm
    (multiplicative, weak-link-sensitive, with zero annihilation).

    A zero normalized component sets the product to zero; among positive
    values, partial compensation remains possible. This is not a strict
    minimum or fully non-compensatory operator.

    NOTE — lesson learned 2026-06-21 (see docs/decisions.md #4):
    Do NOT validate this against a geometric-mean alternative
    (NAI*MAI*RAC)**(1/3) — that is a monotonic transform of the product
    itself and will ALWAYS give Spearman rho = 1.0. It tests nothing.
    Use `compute_smci_additive` below for the real robustness comparison.
    """
    return compute_smci_product_from_normalized(norm01(nai), norm01(mai), norm01(rac))

def compute_smci_product_from_normalized(nai_norm: np.ndarray, mai_norm: np.ndarray, rac_norm: np.ndarray) -> np.ndarray:
    """Legacy product SMCI from normalized components."""
    return np.asarray(nai_norm, dtype=float) * np.asarray(mai_norm, dtype=float) * np.asarray(rac_norm, dtype=float)


def compute_smci_geometric(nai: np.ndarray, mai: np.ndarray, rac: np.ndarray) -> np.ndarray:
    """Equal-weight geometric-mean SMCI from raw components."""
    return compute_smci_geometric_from_normalized(norm01(nai), norm01(mai), norm01(rac))


def compute_smci_geometric_from_normalized(
    nai_norm: np.ndarray, mai_norm: np.ndarray, rac_norm: np.ndarray
) -> np.ndarray:
    """Primary zero-preserving SMCI scale from normalized components."""
    return np.cbrt(compute_smci_product_from_normalized(nai_norm, mai_norm, rac_norm))


def compute_smci_min(nai: np.ndarray, mai: np.ndarray, rac: np.ndarray) -> np.ndarray:
    """Extreme bottleneck diagnostic from raw components."""
    return compute_smci_min_from_normalized(norm01(nai), norm01(mai), norm01(rac))


def compute_smci_min_from_normalized(nai_norm: np.ndarray, mai_norm: np.ndarray, rac_norm: np.ndarray) -> np.ndarray:
    """Extreme bottleneck diagnostic from normalized components."""
    return np.minimum.reduce((np.asarray(nai_norm, dtype=float), np.asarray(mai_norm, dtype=float), np.asarray(rac_norm, dtype=float)))


# Backwards-compatible aliases for callers that still request the legacy product scale.
compute_smci = compute_smci_product
compute_smci_from_normalized = compute_smci_product_from_normalized


def compute_smci_additive(nai: np.ndarray, mai: np.ndarray, rac: np.ndarray) -> np.ndarray:
    """Additive alternative for the SMCI robustness check (replaces the vacuous geometric-mean check)."""
    return (norm01(nai) + norm01(mai) + norm01(rac)) / 3

def compute_smci_additive_from_normalized(nai_norm: np.ndarray, mai_norm: np.ndarray, rac_norm: np.ndarray) -> np.ndarray:
    """Additive robustness index from already-normalized components."""
    return (np.asarray(nai_norm, dtype=float) + np.asarray(mai_norm, dtype=float) + np.asarray(rac_norm, dtype=float)) / 3


def metropolitan_competitiveness_score(mai: np.ndarray, rac: np.ndarray) -> np.ndarray:
    """MCS (Section 3.10) = geometric mean of normalized MAI and RAC, used for theory-first classification."""
    return np.sqrt(norm01(mai) * norm01(rac))

def metropolitan_competitiveness_score_from_normalized(mai_norm: np.ndarray, rac_norm: np.ndarray) -> np.ndarray:
    """MCS from already-normalized MAI and RAC components."""
    return np.sqrt(np.asarray(mai_norm, dtype=float) * np.asarray(rac_norm, dtype=float))


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
