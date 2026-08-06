# NAI Threshold Sensitivity

Decision #27 promotes 800 m (10-min neighborhood, ~10 min at 80 m/min) to the primary
NAI walking catchment: it matches the international 10-minute-neighborhood convention and
the Vietnam/HCMC pedestrian-shed literature (800 m ~ 10 min at 1.3 m/s), and it is more
defensible than 1200 m for a motorcycle-dependent city where willingness-to-walk is low.
1200 m (15 min) is retained as an optimistic 15-minute-city upper-bound sensitivity.
This audit rebuilds NAI and downstream SMCI metrics across the catchment range.

Reference threshold for agreement columns: 800 m (new primary).

| Threshold | Cutoff min | Zero NAI | Mean NAI | Mean SMCI_B | Improved | Declined | Kappa | Spearman |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 600 | 7.5 | 133/462 (28.8%) | 3.56 | 0.0107 | 262 | 67 | 0.862 | 0.954 |
| 800 | 10.0 | 88/462 (19.0%) | 6.09 | 0.0133 | 281 | 93 | 1.000 | 1.000 |
| 1000 | 12.5 | 58/462 (12.6%) | 9.47 | 0.0148 | 295 | 109 | 0.868 | 0.969 |
| 1200 | 15.0 | 33/462 (7.1%) | 13.47 | 0.0169 | 298 | 131 | 0.756 | 0.941 |

Interpretation guide:

- The primary story runs at 800 m. The four-typology structure (Integrated / Fragmented /
  Transit-Dependent / Motorcycle Lock-in) is stable across 600-1200 m (near-equal quadrant
  counts), so the headline does not hinge on the exact catchment.
- Relaxing to 1200 m raises absolute SMCI and lowers the zero-NAI share; it is reported as
  an optimistic upper bound rather than a universal 15-minute-walkability claim.
- Tightening to 600 m sharpens fragmentation (higher zero-NAI) but adds zero-inflation;
  800 m balances Hanoi walking plausibility against signal retention.
