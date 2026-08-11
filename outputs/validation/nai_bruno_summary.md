# Bruno NAI Robustness

- Primary threshold: 800 m network walking
- Sensitivity thresholds: 600, 800, 1000, 1200 m
- Missing-category penalty: 20 min
- The four observed categories are school, healthcare, retail, and park. K=5 adds one declared penalty slot rather than silently using K=4.
- Mean CCS (800 m): 0.344
- Population-weighted CCS Gini (800 m): 0.521

## Local access classes

- Zero: 166 cells
- Low: 98 cells
- Abundant-but-incomplete: 95 cells
- Incomplete: 69 cells
- Locally-complete: 34 cells

## Coverage

| threshold_m | completeness_threshold | cell_share | population_share |
| --- | --- | --- | --- |
| 600 | 0.500 | 0.277 | 0.277 |
| 600 | 0.670 | 0.149 | 0.176 |
| 600 | 0.750 | 0.149 | 0.176 |
| 600 | zero_access | 0.496 | 0.488 |
| 800 | 0.500 | 0.429 | 0.431 |
| 800 | 0.670 | 0.234 | 0.265 |
| 800 | 0.750 | 0.234 | 0.265 |
| 800 | zero_access | 0.359 | 0.347 |
| 1000 | 0.500 | 0.556 | 0.566 |
| 1000 | 0.670 | 0.361 | 0.393 |
| 1000 | 0.750 | 0.361 | 0.393 |
| 1000 | zero_access | 0.266 | 0.241 |
| 1200 | 0.500 | 0.671 | 0.678 |
| 1200 | 0.670 | 0.472 | 0.496 |
| 1200 | 0.750 | 0.472 | 0.496 |
| 1200 | zero_access | 0.162 | 0.136 |

## Interpretation

These are supplementary local-access robustness diagnostics. They do not replace the primary rank-based NAI x MCS typology and are not observed travel behavior.
