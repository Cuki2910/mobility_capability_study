# Spatial Autocorrelation Audit

> Global Moran's I and Local Moran's I are spatial diagnostics, not causal estimates.

## Protocol

- Permutations: 9999; seed: 2026; FDR alpha: 0.05
- Primary weights: Queen contiguity. Sensitivities: Rook contiguity and 8-nearest-neighbour.
- Local cluster labels are shown only after Benjamini-Hochberg FDR correction.

## Global and Local Summary

| metric | weight_spec | n_cells | permutations | seed | global_moran_i | global_p_value | global_expected_i | local_significant_cells | high_high_cells | low_low_cells | high_low_cells | low_high_cells |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SMCI_B | queen | 462 | 9999 | 2026 | 0.769679 | 0.0001 | -0.002169 | 189 | 93 | 92 | 0 | 4 |
| Delta_SMCI | queen | 462 | 9999 | 2026 | 0.744489 | 0.0001 | -0.002169 | 140 | 76 | 62 | 0 | 2 |
| NAI | queen | 462 | 9999 | 2026 | 0.783925 | 0.0001 | -0.002169 | 151 | 54 | 94 | 0 | 3 |
| MAI_B | queen | 462 | 9999 | 2026 | 0.904813 | 0.0001 | -0.002169 | 199 | 115 | 83 | 0 | 1 |
| RAC_B | queen | 462 | 9999 | 2026 | 0.326978 | 0.0001 | -0.002169 | 92 | 5 | 83 | 1 | 3 |
| SMCI_B | rook | 462 | 9999 | 2026 | 0.797893 | 0.0001 | -0.002169 | 57 | 35 | 21 | 0 | 1 |
| Delta_SMCI | rook | 462 | 9999 | 2026 | 0.77693 | 0.0001 | -0.002169 | 40 | 21 | 19 | 0 | 0 |
| NAI | rook | 462 | 9999 | 2026 | 0.812507 | 0.0001 | -0.002169 | 54 | 25 | 29 | 0 | 0 |
| MAI_B | rook | 462 | 9999 | 2026 | 0.920508 | 0.0001 | -0.002169 | 105 | 60 | 45 | 0 | 0 |
| RAC_B | rook | 462 | 9999 | 2026 | 0.398649 | 0.0001 | -0.002169 | 13 | 2 | 10 | 0 | 1 |
| SMCI_B | knn | 462 | 9999 | 2026 | 0.76438 | 0.0001 | -0.002169 | 198 | 96 | 98 | 0 | 4 |
| Delta_SMCI | knn | 462 | 9999 | 2026 | 0.735905 | 0.0001 | -0.002169 | 157 | 84 | 71 | 0 | 2 |
| NAI | knn | 462 | 9999 | 2026 | 0.780852 | 0.0001 | -0.002169 | 168 | 56 | 108 | 0 | 4 |
| MAI_B | knn | 462 | 9999 | 2026 | 0.898198 | 0.0001 | -0.002169 | 203 | 115 | 87 | 0 | 1 |
| RAC_B | knn | 462 | 9999 | 2026 | 0.307595 | 0.0001 | -0.002169 | 103 | 6 | 92 | 1 | 4 |

## Interpretation Rule

A cluster is considered robust only when its substantive pattern appears under Queen weights and at least one sensitivity specification. Zero inflation in SMCI is retained and disclosed; no normality claim is made.
