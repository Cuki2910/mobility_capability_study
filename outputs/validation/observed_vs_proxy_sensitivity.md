# Observed-vs-Proxy MAI Sensitivity

Decision #21 compares proxy opportunity weights, the hybrid observed hierarchy, and the strict source-backed observed magnitude specification.

## Summary

| Metric | Proxy | Hybrid observed | Strict observed |
|---|---:|---:|---:|
| mean_SMCI_B | 0.0163 | 0.0160 | 0.0160 |
| share_improved | 0.6861 | 0.6602 | 0.6602 |
| typology_kappa | 1.0000 | 0.9245 | 0.9245 |
| cells_relabelled | 0.0000 | 24.0000 | 24.0000 |
| spearman_SMCI_B | 1.0000 | 0.9950 | 0.9950 |
| spearman_p_value | 0.0000 | 0.0000 | 0.0000 |
| VIF_MAI | 4.6460 | 3.7839 | 3.7839 |
| VIF_RAC | 1.9390 | 1.9993 | 1.9993 |

## Strict Observed Coverage

| Coverage column | Share |
|---|---:|
| obs_coverage_economic | 100.0% |
| obs_coverage_higher_education | 100.0% |
| obs_coverage_metro_commercial | 100.0% |
| obs_coverage_tertiary_healthcare | 100.0% |
| obs_coverage_total | 100.0% |

## Interpretation

Strict observed mode has no tag-only proxy fallback. Excluded POIs carry explicit audit reasons; proxy mode remains the regression baseline for sensitivity comparison.
