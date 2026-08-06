# Spatial Autocorrelation Audit

> Global Moran's I and Local Moran's I are spatial diagnostics, not causal estimates.

## Protocol

- Permutations: 9999; seed: 2026; FDR alpha: 0.05
- Primary weights: Queen contiguity. Sensitivities: Rook contiguity and 8-nearest-neighbour.
- Local cluster labels are shown only after Benjamini-Hochberg FDR correction.

## Global and Local Summary

| metric | weight_spec | n_cells | permutations | seed | global_moran_i | global_p_value | global_expected_i | local_significant_cells | high_high_cells | low_low_cells | high_low_cells | low_high_cells |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SMCI_B | queen | 462 | 9999 | 2026 | 0.749568 | 0.0001 | -0.002169 | 172 | 58 | 111 | 0 | 3 |
| Delta_SMCI | queen | 462 | 9999 | 2026 | 0.710362 | 0.0001 | -0.002169 | 75 | 44 | 30 | 0 | 1 |
| NAI | queen | 462 | 9999 | 2026 | 0.783925 | 0.0001 | -0.002169 | 151 | 54 | 94 | 0 | 3 |
| MAI_B | queen | 462 | 9999 | 2026 | 0.904813 | 0.0001 | -0.002169 | 199 | 115 | 83 | 0 | 1 |
| RAC_B | queen | 462 | 9999 | 2026 | 0.326978 | 0.0001 | -0.002169 | 92 | 5 | 83 | 1 | 3 |
| SMCI_B | rook | 462 | 9999 | 2026 | 0.779842 | 0.0001 | -0.002169 | 41 | 23 | 18 | 0 | 0 |
| Delta_SMCI | rook | 462 | 9999 | 2026 | 0.74781 | 0.0001 | -0.002169 | 19 | 16 | 3 | 0 | 0 |
| NAI | rook | 462 | 9999 | 2026 | 0.812507 | 0.0001 | -0.002169 | 54 | 25 | 29 | 0 | 0 |
| MAI_B | rook | 462 | 9999 | 2026 | 0.920508 | 0.0001 | -0.002169 | 105 | 60 | 45 | 0 | 0 |
| RAC_B | rook | 462 | 9999 | 2026 | 0.398649 | 0.0001 | -0.002169 | 13 | 2 | 10 | 0 | 1 |
| SMCI_B | knn | 462 | 9999 | 2026 | 0.747102 | 0.0001 | -0.002169 | 186 | 59 | 124 | 0 | 3 |
| Delta_SMCI | knn | 462 | 9999 | 2026 | 0.70836 | 0.0001 | -0.002169 | 77 | 44 | 32 | 0 | 1 |
| NAI | knn | 462 | 9999 | 2026 | 0.780852 | 0.0001 | -0.002169 | 168 | 56 | 108 | 0 | 4 |
| MAI_B | knn | 462 | 9999 | 2026 | 0.898198 | 0.0001 | -0.002169 | 203 | 115 | 87 | 0 | 1 |
| RAC_B | knn | 462 | 9999 | 2026 | 0.307595 | 0.0001 | -0.002169 | 103 | 6 | 92 | 1 | 4 |

## Interpretation Rule

A cluster is considered robust only when its substantive pattern appears under Queen weights and at least one sensitivity specification. Zero inflation in SMCI is retained and disclosed; no normality claim is made.
