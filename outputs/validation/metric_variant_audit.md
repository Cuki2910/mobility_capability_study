# Metric Variant Audit

Reviewer-risk variants were compared against the current strict observed MAI specification.

## Recommendation

- Recommended primary candidate: **rac_time_only**
- Legacy full-RAC max VIF: 9.73
- Recommended max VIF: 2.91
- Kappa vs current typology: 1.0000
- Spearman rho vs current SMCI_B: 1.0000
- Relabelled cells vs current: 0 / 462

Promotion rule: eligible candidates must keep kappa >= 0.85, Spearman rho >= 0.95, and not increase zero-SMCI cells; among them, the lowest-VIF candidate wins.

## Post-process Metric Candidates

| Variant | NAI | RAC | Norm | SMCI | Kappa | Rho | Max VIF | Zero SMCI | Relabelled |
|---|---|---|---|---|---:|---:|---:|---:|---:|
| legacy_full_rac | NAI | full | minmax | product | 0.9065 | 0.9878 | 9.73 | 88 | 30 |
| nai_diversity | NAI_diversity | full | minmax | product | 0.7777 | 0.9634 | 9.77 | 88 | 71 |
| nai_capped | NAI_capped | full | minmax | product | 0.8410 | 0.9819 | 10.05 | 88 | 51 |
| rac_time_only | NAI | time_only | minmax | product | 1.0000 | 1.0000 | 2.91 | 88 | 0 |
| rac_opp_only | NAI | opp_only | minmax | product | 0.7170 | 0.9476 | 2865501.84 | 88 | 92 |
| winsor_norm | NAI | full | winsor | product | 0.9066 | 0.9789 | 9.40 | 93 | 30 |
| log_norm | NAI | full | log | product | 0.9252 | 0.9911 | 16.58 | 88 | 24 |
| additive_smci | NAI | full | minmax | additive | 0.9065 | 0.8685 | 9.73 | 1 | 30 |
| reviewer_safe_capped_time_winsor | NAI_capped | time_only | winsor | product | 0.9191 | 0.9845 | 3.53 | 93 | 26 |
| reviewer_safe_diversity_time_winsor | NAI_diversity | time_only | winsor | product | 0.8562 | 0.9714 | 3.89 | 93 | 46 |
| absolute_count5_mcs60 | NAI | full | minmax | product | 0.4924 | 0.9878 | 9.73 | 88 | 171 |
| absolute_diversity4_mcs60 | NAI_diversity | full | minmax | product | 0.3310 | 0.9634 | 9.77 | 88 | 231 |

## Rebuild Sensitivities

| Variant | Mean SMCI_B | Share improved | Kappa | Rho | Zero SMCI | Relabelled |
|---|---:|---:|---:|---:|---:|---:|
| weights_equal | 0.0139 | 60.6% | 0.9686 | 0.9996 | 88 | 10 |
| weights_job_heavy | 0.0128 | 60.6% | 0.9751 | 0.9997 | 88 | 8 |
| weights_econ_light | 0.0143 | 61.0% | 0.9562 | 0.9992 | 88 | 14 |
| weights_service_health_heavy | 0.0140 | 60.8% | 0.9749 | 0.9996 | 88 | 8 |
| weights_utm_derived | 0.0123 | 60.0% | 0.9440 | 0.9988 | 88 | 18 |
| decay_20_40 | 0.0158 | 47.6% | 0.7417 | 0.9773 | 88 | 82 |
| decay_45_90 | 0.0112 | 64.5% | 0.9253 | 0.9955 | 89 | 24 |
| decay_exponential_30_60 | 0.0146 | 61.0% | 0.9625 | 0.9966 | 89 | 12 |
| mai_no_top1pct | 0.0134 | 62.1% | 0.9813 | 0.9990 | 88 | 6 |
| mai_no_top5pct | 0.0137 | 61.7% | 0.9497 | 0.9979 | 88 | 16 |

## Missingness

- Cells within 800 m of at least one strict-excluded POI: 48.5%
- Max strict-excluded POIs within 800 m of a cell: 6

Wrote `outputs\validation\metric_variant_audit.csv` and `outputs\validation\metric_variant_cells.csv`.
