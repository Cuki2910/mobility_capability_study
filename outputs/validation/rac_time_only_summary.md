# RAC_time-only Sensitivity (Promoted Primary)

**Motivation:** VIF(MAI)=10.04 and VIF(RAC)=9.89 in the pilot both exceed the
threshold of 5. This is structural: RAC_opp numerator = MAI_transit (decisions.md #3).
The promoted primary replaces RAC = sqrt(RAC_time x RAC_opp) with RAC_time alone.

## VIF - Legacy Full-RAC Specification

| Variable | VIF | Flag |
|---|---:|---|
| NAI | 3.41 | OK |
| MAI | 10.04 | HIGH ⚠ |
| RAC | 9.89 | HIGH ⚠ |

## VIF - Promoted RAC_time-only Specification

| Variable | VIF | Flag |
|---|---:|---|
| NAI | 3.26 | OK |
| MAI | 3.82 | OK |
| RAC_time | 1.92 | OK |

## Typology Agreement

- Cohen's κ: **0.9116** (near-perfect)
- Spearman ρ (SMCI rank): **0.9824**
- Cells that changed label: **28 / 462** (6.1%)

## Typology Shift Matrix

Rows = legacy full-RAC label; columns = promoted RAC_time-only label. Diagonal = no change.

| From (legacy full RAC) \ To (RAC_time primary) | Integrated Capability | Fragmented Capability | Transit-Dependent | Motorcycle Lock-in |
|---|---|---|---|---|
| Integrated Capability | 169 | 7 | 0 | 0 |
| Fragmented Capability | 3 | 52 | 0 | 0 |
| Transit-Dependent | 0 | 0 | 48 | 7 |
| Motorcycle Lock-in | 0 | 0 | 11 | 165 |

## Interpretation

κ = 0.9116 ≥ 0.70: typology findings are **robust** to replacing
the full RAC composite with RAC_time alone. Despite high VIF between MAI and
RAC in the primary specification, the classification outcome is not driven by
the shared MAI_transit component in RAC_opp.

**Recommendation:** use RAC_time-only as the primary reviewer-safe RAC specification.
Report full RAC as a construct-rich robustness check.
