# Typology Robustness

Purpose: test whether the four-cell typology is only an artefact of the rank-based median split.

## Variants

- `absolute_norm_0.50`: high NAI and high MCS require normalized scores >= 0.50.
- `quantile_*`: high/low thresholds are moved away from the median to 40%, 45%, 55%, and 60% cut points.

## Agreement With Primary Typology

| Variant | Kappa | Relabelled | Integrated | Fragmented | Transit-Dependent | Motorcycle Lock-in |
|---|---:|---:|---:|---:|---:|---:|
| absolute_norm_0.50 | 0.371 | 218 (47.2%) | 43 | 0 | 231 | 188 |
| quantile_0.40 | 0.726 | 89 (19.3%) | 209 | 68 | 68 | 117 |
| quantile_0.45 | 0.789 | 68 (14.7%) | 202 | 75 | 52 | 133 |
| quantile_0.55 | 0.891 | 35 (7.6%) | 150 | 68 | 58 | 186 |
| quantile_0.60 | 0.822 | 57 (12.3%) | 142 | 76 | 43 | 201 |

## Interpretation

Across variants, minimum kappa is 0.371; maximum relabelled cells is 218/462.
The exact 169/169/62/62 primary balance is therefore a property of the median split, but the broad spatial ordering can be checked against non-median and absolute thresholds.
Report this table with the primary typology to pre-empt the by-construction critique.
