# RAC_time-only Sensitivity (VIF Contingency)

**Motivation:** VIF(MAI)=16.50 and VIF(RAC)=18.14 in the pilot both exceed the
threshold of 5. This is structural: RAC_opp numerator = MAI_transit (decisions.md #3).
The contingency is to replace RAC = sqrt(RAC_time × RAC_opp) with RAC_time alone.

## VIF — Primary Specification (full RAC)

| Variable | VIF | Flag |
|---|---:|---|
| NAI | 2.83 | OK |
| MAI | 16.50 | HIGH ⚠ |
| RAC | 18.14 | HIGH ⚠ |

## VIF — RAC_time-only Specification

| Variable | VIF | Flag |
|---|---:|---|
| NAI | 2.74 | OK |
| MAI | 4.81 | OK |
| RAC_time | 4.37 | OK |

## Typology Agreement

- Cohen's κ: **0.8704** (near-perfect)
- Spearman ρ (SMCI rank): **0.9917**
- Cells that changed label: **42 / 462** (9.1%)

## Typology Shift Matrix

Rows = primary label; columns = RAC_time-only label. Diagonal = no change.

| From (primary) \ To (RAC_time) | Integrated Capability | Fragmented Capability | Transit-Dependent | Motorcycle Lock-in |
|---|---|---|---|---|
| Integrated Capability | 159 | 1 | 0 | 0 |
| Fragmented Capability | 15 | 56 | 0 | 0 |
| Transit-Dependent | 0 | 0 | 51 | 20 |
| Motorcycle Lock-in | 0 | 0 | 6 | 154 |

## Interpretation

κ = 0.8704 ≥ 0.70: typology findings are **robust** to replacing
the full RAC composite with RAC_time alone. Despite high VIF between MAI and
RAC in the primary specification, the classification outcome is not driven by
the shared MAI_transit component in RAC_opp.

**Recommendation:** report the primary (full RAC) specification as the main
result. Report RAC_time-only as a VIF robustness check in the validation section.
