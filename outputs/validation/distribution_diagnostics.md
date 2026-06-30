# Pilot Distribution Diagnostics

## Why Mean SMCI Is Small

- Mean normalized NAI: 0.2495.
- Mean normalized MAI_B: 0.5649.
- Mean normalized RAC_B: 0.0817.
- Product of those means: 0.0115.
- Actual mean SMCI_B: 0.0160.

The low mean is mainly driven by RAC compression and zero inflation, not by NAI alone. RAC_B has a normalized mean of about 0.0817 because one extreme cell reaches 1.0 while the 99th percentile is only about 0.1983. SMCI_B also equals zero for cells where any component is zero.

## Zero Inflation

- NAI zero share: 7.14%.
- MAI_B zero share: 0.00%.
- RAC_B zero share: 0.22%.
- SMCI_B zero share: 7.36%.

## Delta SMCI Groups

- Improved: 305 cells (66.02%).
- Unchanged: 33 cells (7.14%).
- Declined: 124 cells (26.84%).

## Typology Sanity

- NAI high/low margins: 231/231.
- MCS high/low margins: 231/231.
- NAI-MCS Pearson r: 0.5602.
- NAI-MCS Spearman rho: 0.6507.

The symmetric typology counts are produced by rank-based median margins plus weak positive NAI-MCS association. They are not evidence that NAI and MCS are duplicated.

## Reporting Recommendation

Report SMCI primarily through maps, percentiles, ranks, and delta groups. Treat absolute mean SMCI as a scale-dependent diagnostic, not as an intuitive welfare magnitude.
