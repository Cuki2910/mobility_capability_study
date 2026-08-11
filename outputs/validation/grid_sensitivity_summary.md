# Grid Sensitivity Summary

All alternate grids rerun the same network, POI, 800 m threshold, shared-normalization, and Scenario A/B pipeline.
Nearest-centroid matching is a comparability device, not a claim that cells are identical.
Boundary values are descriptive near-boundary (250 m) inside-minus-outside median SMCI_B differences. HH/LL values are Queen-LISA location-set Jaccard scores using 999 permutations, not inferential confirmation.

- Primary near-boundary median difference: 0.0966
- Primary WorldPop total: 78815.7
- Population-total differences reflect raster/grid intersection tolerance and must be reported, not treated as changes in population.

| grid | n_cells | mean_SMCI_B | population_weighted_SMCI_B | zero_NAI_share | improved_share | boundary_median_inside_minus_outside_SMCI_B | boundary_difference_change_vs_primary | population_total | population_total_difference | population_total_difference_pct | high_high_primary_location_jaccard | low_low_primary_location_jaccard | spearman_NAI_nearest_primary | spearman_MAI_B_nearest_primary | spearman_RAC_B_nearest_primary | spearman_SMCI_B_nearest_primary | typology_kappa_nearest_primary |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hex | 437.0000 | 0.1780 | 0.1837 | 0.1945 | 0.6041 | 0.0816 | -0.0150 | 78815.6579 | -0.0005 | -0.0000 | 0.8198 | 0.7143 | 0.8198 | 0.9347 | 0.7655 | 0.8265 | 0.6510 |
| shift_x | 442.0000 | 0.1895 | 0.1969 | 0.1787 | 0.5905 | 0.1047 | 0.0081 | 78835.5448 | 19.8864 | 0.0252 | 0.8017 | 0.6983 | 0.8266 | 0.9380 | 0.7810 | 0.8390 | 0.6740 |
| shift_y | 428.0000 | 0.1655 | 0.1718 | 0.1986 | 0.5935 | 0.0863 | -0.0103 | 78843.6366 | 27.9782 | 0.0355 | 0.8073 | 0.7739 | 0.8239 | 0.9363 | 0.7655 | 0.8311 | 0.6879 |
| shift_xy | 449.0000 | 0.2080 | 0.2224 | 0.1826 | 0.6102 | 0.0979 | 0.0013 | 78815.6576 | -0.0008 | -0.0000 | 0.7638 | 0.7586 | 0.8331 | 0.9405 | 0.7778 | 0.8450 | 0.6820 |

## Interpretation

Scenario B improvement share remains near 60% across variants. Exact typology and hotspot boundaries are MAUP-sensitive; substantive conclusions should use the direction, population-weighted mean, and repeated broad clustering rather than a single cell assignment.
