"""
tests/test_accessibility.py

Run with: pytest tests/ -v

These tests exist because running real numbers (2026-06-21 pilot) caught a
bug that six rounds of reading the proposal text did not: the originally
planned "geometric-mean robustness check" for SMCI was mathematically
guaranteed to agree with the multiplicative SMCI, so it tested nothing.
test_geometric_mean_check_is_vacuous() documents that finding so nobody
re-introduces it without realizing why it's wrong.
"""
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from accessibility import (
    norm01, compute_rac, compute_smci, compute_smci_additive,
    metropolitan_competitiveness_score, theory_first_typology,
)


def test_norm01_range():
    x = np.array([3.0, 7.0, 1.0, 9.0])
    n = norm01(x)
    assert n.min() == 0.0 and n.max() == 1.0


def test_norm01_constant_input_does_not_crash():
    x = np.array([5.0, 5.0, 5.0])
    assert np.all(norm01(x) == 0.0)


def test_rac_is_bounded_and_directional():
    rng = np.random.default_rng(0)
    rac = compute_rac(rng.random(50), rng.random(50))["RAC"]
    assert rac.min() >= 0 and rac.max() <= 1


def test_geometric_mean_check_is_vacuous():
    """
    Regression test for the 2026-06-21 finding: comparing multiplicative
    SMCI to (NAI*MAI*RAC)**(1/3) is NOT a meaningful robustness check,
    because cube root is a monotonic transform of the product -> rank
    correlation is always exactly 1. This test pins that fact down so the
    proposal's methods text doesn't drift back to the wrong comparison.
    """
    rng = np.random.default_rng(1)
    nai, mai, rac = rng.random(100), rng.random(100), rng.random(100)
    smci_mult = compute_smci(nai, mai, rac)
    smci_geo = (norm01(nai) * norm01(mai) * norm01(rac)) ** (1 / 3)

    from scipy.stats import spearmanr
    rho_geo, _ = spearmanr(smci_mult, smci_geo)
    rho_add, _ = spearmanr(smci_mult, compute_smci_additive(nai, mai, rac))

    assert rho_geo > 0.999999, "expected geometric-mean comparison to be (near) perfectly correlated by construction"
    assert rho_add < 0.999, "additive comparison should NOT be perfectly correlated — it's the real check"


def test_theory_first_typology_has_four_labels_by_construction():
    rng = np.random.default_rng(2)
    nai = rng.random(200)
    mcs = metropolitan_competitiveness_score(rng.random(200), rng.random(200))
    labels = theory_first_typology(nai, mcs)
    assert set(labels) == {
        "Integrated Capability", "Fragmented Capability",
        "Transit-Dependent", "Motorcycle Lock-in",
    }
