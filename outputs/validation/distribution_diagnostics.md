# Pilot Distribution Diagnostics

## Why Mean SMCI Is Small

- Mean normalized NAI: 0.1777.
- Mean normalized MAI_B: 0.6086.
- Mean normalized RAC_B: 0.5245.
- Product of those means: 0.0567.
- Actual mean SMCI_B: 0.0968.

The low mean is mainly driven by RAC compression and zero inflation, not by NAI alone. RAC_B has a normalized mean of about 0.5245 because one extreme cell reaches 1.0 while the 99th percentile is only about 0.8014. SMCI_B also equals zero for cells where any component is zero.

## Zero Inflation

- NAI zero share: 25.11%.
- MAI_B zero share: 0.00%.
- RAC_B zero share: 0.22%.
- SMCI_B zero share: 25.11%.

## Delta SMCI Groups

- Improved: 240 cells (51.95%).
- Unchanged: 222 cells (48.05%).
- Declined: 0 cells (0.00%).

## Typology Sanity

- NAI high/low margins: 231/231.
- MCS high/low margins: 231/231.
- NAI-MCS Pearson r: 0.5733.
- NAI-MCS Spearman rho: 0.6044.

The symmetric typology counts are produced by rank-based median margins plus weak positive NAI-MCS association. They are not evidence that NAI and MCS are duplicated.

## Reporting Recommendation

Report SMCI primarily through maps, percentiles, ranks, and delta groups. Treat absolute mean SMCI as a scale-dependent diagnostic, not as an intuitive welfare magnitude.
