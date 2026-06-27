# RAC_time-only Sensitivity (VIF Contingency)

**Motivation:** VIF(MAI)=8.21 and VIF(RAC)=7.90 in the pilot both exceed the
threshold of 5. This is structural: RAC_opp numerator = MAI_transit (decisions.md #3).
The contingency is to replace RAC = sqrt(RAC_time × RAC_opp) with RAC_time alone.

## VIF — Primary Specification (full RAC)

| Variable | VIF | Flag |
|---|---:|---|
| NAI | 2.67 | OK |
| MAI | 8.21 | HIGH ⚠ |
| RAC | 7.90 | HIGH ⚠ |

## VIF — RAC_time-only Specification

| Variable | VIF | Flag |
|---|---:|---|
| NAI | 2.59 | OK |
| MAI | 3.25 | OK |
| RAC_time | 1.86 | OK |

## Typology Agreement

- Cohen's κ: **0.9004** (near-perfect)
- Spearman ρ (SMCI rank): **0.9875**
- Cells that changed label: **32 / 462** (6.9%)

## Typology Shift Matrix

Rows = primary label; columns = RAC_time-only label. Diagonal = no change.

| From (primary) \ To (RAC_time) | Integrated Capability | Fragmented Capability | Transit-Dependent | Motorcycle Lock-in |
|---|---|---|---|---|
| Integrated Capability | 164 | 2 | 0 | 0 |
| Fragmented Capability | 9 | 56 | 0 | 0 |
| Transit-Dependent | 0 | 0 | 51 | 14 |
| Motorcycle Lock-in | 0 | 0 | 7 | 159 |

## Interpretation

κ = 0.9004 ≥ 0.70: typology findings are **robust** to replacing
the full RAC composite with RAC_time alone. Despite high VIF between MAI and
RAC in the primary specification, the classification outcome is not driven by
the shared MAI_transit component in RAC_opp.

**Recommendation:** report the primary (full RAC) specification as the main
result. Report RAC_time-only as a VIF robustness check in the validation section.
