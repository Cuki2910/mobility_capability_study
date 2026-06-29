# Observed-vs-Proxy MAI Sensitivity

Decision #21 compares proxy opportunity weights, the hybrid observed hierarchy, and the strict source-backed observed magnitude specification.

## Summary

| Metric | Proxy | Hybrid observed | Strict observed |
|---|---:|---:|---:|
| mean_SMCI_B | 0.0435 | 0.0500 | 0.0500 |
| share_improved | 0.6450 | 0.6190 | 0.6190 |
| typology_kappa | 1.0000 | 0.8762 | 0.8762 |
| cells_relabelled | 0.0000 | 40.0000 | 40.0000 |
| spearman_SMCI_B | 1.0000 | 0.9915 | 0.9915 |
| spearman_p_value | 0.0000 | 0.0000 | 0.0000 |
| VIF_MAI | 8.9557 | 10.2265 | 10.2265 |
| VIF_RAC | 8.8521 | 11.1232 | 11.1232 |

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
