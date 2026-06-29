# Observed-vs-Proxy MAI Sensitivity

Decision #21 compares proxy opportunity weights, the hybrid observed hierarchy, and the strict source-backed observed magnitude specification.

## Summary

| Metric | Proxy | Hybrid observed | Strict observed |
|---|---:|---:|---:|
| mean_SMCI_B | 0.0129 | 0.0125 | 0.0125 |
| share_improved | 0.6450 | 0.6190 | 0.6190 |
| typology_kappa | 1.0000 | 0.9245 | 0.9245 |
| cells_relabelled | 0.0000 | 24.0000 | 24.0000 |
| spearman_SMCI_B | 1.0000 | 0.9966 | 0.9966 |
| spearman_p_value | 0.0000 | 0.0000 | 0.0000 |
| VIF_MAI | 3.3102 | 2.9308 | 2.9308 |
| VIF_RAC | 1.9456 | 2.0186 | 2.0186 |

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
