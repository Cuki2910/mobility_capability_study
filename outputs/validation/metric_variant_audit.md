# Metric Variant Audit

Reviewer-risk variants were compared against the current strict observed MAI specification.

## Recommendation

- Recommended primary candidate: **rac_time_only**
- Legacy full-RAC max VIF: 10.04
- Recommended max VIF: 3.82
- Kappa vs current typology: 1.0000
- Spearman rho vs current SMCI_B: 1.0000
- Relabelled cells vs current: 0 / 462

Promotion rule: eligible candidates must keep kappa >= 0.85, Spearman rho >= 0.95, and not increase zero-SMCI cells; among them, the lowest-VIF candidate wins.

## Post-process Metric Candidates

| Variant | NAI | RAC | Norm | SMCI | Kappa | Rho | Max VIF | Zero SMCI | Relabelled |
|---|---|---|---|---|---:|---:|---:|---:|---:|
| legacy_full_rac | NAI | full | minmax | product | 0.9116 | 0.9824 | 10.04 | 34 | 28 |
| nai_diversity | NAI_diversity | full | minmax | product | 0.7219 | 0.9608 | 11.66 | 34 | 91 |
| nai_capped | NAI_capped | full | minmax | product | 0.7872 | 0.9779 | 10.49 | 34 | 69 |
| rac_time_only | NAI | time_only | minmax | product | 1.0000 | 1.0000 | 3.82 | 34 | 0 |
| rac_opp_only | NAI | opp_only | minmax | product | 0.7388 | 0.9260 | 3834910.34 | 33 | 82 |
| winsor_norm | NAI | full | winsor | product | 0.9243 | 0.9820 | 9.63 | 44 | 24 |
| log_norm | NAI | full | log | product | 0.9368 | 0.9861 | 16.73 | 34 | 20 |
| additive_smci | NAI | full | minmax | additive | 0.9116 | 0.9235 | 10.04 | 1 | 28 |
| reviewer_safe_capped_time_winsor | NAI_capped | time_only | winsor | product | 0.8529 | 0.9799 | 5.30 | 44 | 48 |
| reviewer_safe_diversity_time_winsor | NAI_diversity | time_only | winsor | product | 0.7900 | 0.9705 | 6.19 | 44 | 69 |
| absolute_count5_mcs60 | NAI | full | minmax | product | 0.2999 | 0.9824 | 10.04 | 34 | 221 |
| absolute_diversity4_mcs60 | NAI_diversity | full | minmax | product | 0.3677 | 0.9608 | 11.66 | 34 | 201 |

## Rebuild Sensitivities

| Variant | Mean SMCI_B | Share improved | Kappa | Rho | Zero SMCI | Relabelled |
|---|---:|---:|---:|---:|---:|---:|
| weights_equal | 0.0170 | 68.6% | 0.9306 | 0.9988 | 34 | 22 |
| weights_job_heavy | 0.0155 | 65.6% | 0.9812 | 0.9997 | 34 | 6 |
| weights_econ_light | 0.0173 | 68.4% | 0.9369 | 0.9976 | 33 | 20 |
| weights_service_health_heavy | 0.0170 | 68.6% | 0.9623 | 0.9985 | 34 | 12 |
| decay_20_40 | 0.0186 | 46.1% | 0.7763 | 0.9676 | 34 | 72 |
| decay_45_90 | 0.0141 | 69.0% | 0.9072 | 0.9944 | 35 | 30 |
| decay_exponential_30_60 | 0.0186 | 66.0% | 0.9314 | 0.9971 | 34 | 22 |
| mai_no_top1pct | 0.0163 | 65.6% | 0.9812 | 0.9988 | 34 | 6 |
| mai_no_top5pct | 0.0166 | 66.5% | 0.9433 | 0.9967 | 34 | 18 |

## Missingness

- Cells within 800 m of at least one strict-excluded POI: 27.1%
- Max strict-excluded POIs within 800 m of a cell: 2

Wrote `outputs\validation\metric_variant_audit.csv` and `outputs\validation\metric_variant_cells.csv`.
