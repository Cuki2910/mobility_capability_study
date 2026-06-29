# Metric Variant Audit

Reviewer-risk variants were compared against the current strict observed MAI specification.

## Recommendation

- Recommended primary candidate: **rac_time_only**
- Legacy full-RAC max VIF: 10.06
- Recommended max VIF: 2.88
- Kappa vs current typology: 0.9125
- Spearman rho vs current SMCI_B: 0.9889
- Relabelled cells vs current: 28 / 462

Promotion rule: eligible candidates must keep kappa >= 0.85, Spearman rho >= 0.95, and not increase zero-SMCI cells; among them, the lowest-VIF candidate wins.

## Post-process Metric Candidates

| Variant | NAI | RAC | Norm | SMCI | Kappa | Rho | Max VIF | Zero SMCI | Relabelled |
|---|---|---|---|---|---:|---:|---:|---:|---:|
| legacy_full_rac | NAI | full | minmax | product | 1.0000 | 1.0000 | 10.06 | 88 | 0 |
| nai_diversity | NAI_diversity | full | minmax | product | 0.8626 | 0.9806 | 10.27 | 88 | 44 |
| nai_capped | NAI_capped | full | minmax | product | 0.9254 | 0.9923 | 10.51 | 88 | 24 |
| rac_time_only | NAI | time_only | minmax | product | 0.9125 | 0.9889 | 2.88 | 88 | 28 |
| rac_opp_only | NAI | opp_only | minmax | product | 0.8284 | 0.9870 | 3832457.14 | 88 | 56 |
| winsor_norm | NAI | full | winsor | product | 0.9875 | 0.9967 | 9.77 | 94 | 4 |
| log_norm | NAI | full | log | product | 0.9751 | 0.9975 | 17.35 | 88 | 8 |
| additive_smci | NAI | full | minmax | additive | 1.0000 | 0.8957 | 10.06 | 1 | 0 |
| reviewer_safe_capped_time_winsor | NAI_capped | time_only | winsor | product | 0.8412 | 0.9736 | 3.56 | 94 | 51 |
| reviewer_safe_diversity_time_winsor | NAI_diversity | time_only | winsor | product | 0.7815 | 0.9632 | 3.92 | 94 | 70 |
| absolute_count5_mcs60 | NAI | full | minmax | product | 0.8477 | 1.0000 | 10.06 | 88 | 49 |
| absolute_diversity4_mcs60 | NAI_diversity | full | minmax | product | 0.6629 | 0.9806 | 10.27 | 88 | 109 |

## Rebuild Sensitivities

| Variant | Mean SMCI_B | Share improved | Kappa | Rho | Zero SMCI | Relabelled |
|---|---:|---:|---:|---:|---:|---:|
| weights_equal | 0.0493 | 64.3% | 0.9378 | 0.9981 | 88 | 20 |
| weights_job_heavy | 0.0506 | 61.5% | 0.9751 | 0.9994 | 88 | 8 |
| weights_econ_light | 0.0491 | 64.3% | 0.9191 | 0.9971 | 88 | 26 |
| weights_service_health_heavy | 0.0494 | 64.3% | 0.9503 | 0.9985 | 88 | 16 |
| decay_20_40 | 0.0519 | 44.2% | 0.8488 | 0.9835 | 88 | 48 |
| decay_45_90 | 0.0460 | 64.5% | 0.9312 | 0.9923 | 89 | 22 |
| decay_exponential_30_60 | 0.0546 | 61.9% | 0.9191 | 0.9964 | 88 | 26 |
| mai_no_top1pct | 0.0527 | 61.5% | 0.9751 | 0.9994 | 88 | 8 |
| mai_no_top5pct | 0.0468 | 62.8% | 0.9316 | 0.9963 | 88 | 22 |

## Missingness

- Cells within 800 m of at least one strict-excluded POI: 27.1%
- Max strict-excluded POIs within 800 m of a cell: 2

Wrote `outputs\validation\metric_variant_audit.csv` and `outputs\validation\metric_variant_cells.csv`.
