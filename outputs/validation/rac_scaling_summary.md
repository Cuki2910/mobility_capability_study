# RAC Scaling Sensitivity

Primary specification: min-max normalization on raw RAC subcomponents.
Sensitivity variants: log(1+x)→min-max (log_minmax) and sqrt→min-max (sqrt_minmax).
All variants use shared Scenario A+B bounds for Delta_SMCI comparability.

## RAC_B Normalized — Distribution Summary

| Scaler | mean | p99 | max | max/p99 |
|---|---|---|---|---|
| minmax | 0.4833 | 0.8777 | 1.0000 | 1.14x |
| log_minmax | 0.5180 | 0.8915 | 1.0000 | 1.12x |
| sqrt_minmax | 0.6230 | 0.9202 | 1.0000 | 1.09x |

## SMCI_B Summary

| Scaler | mean SMCI_B | median SMCI_B |
|---|---|---|
| minmax | 0.088260 | 0.016904 |
| log_minmax | 0.091935 | 0.018832 |
| sqrt_minmax | 0.102249 | 0.025703 |

## Typology Agreement (Cohen's Kappa)

- **minmax vs log_minmax**: κ = 1.0 (near-perfect)
- **minmax vs sqrt_minmax**: κ = 0.9817 (near-perfect)
- **log_minmax vs sqrt_minmax**: κ = 0.9817 (near-perfect)

## SMCI Rank Agreement (Spearman ρ)

- **minmax vs log_minmax**: ρ = 1.0
- **minmax vs sqrt_minmax**: ρ = 0.9996
- **log_minmax vs sqrt_minmax**: ρ = 0.9997

## Typology Shift: minmax → log_minmax

Rows = primary (minmax) label; columns = log_minmax label.
Diagonal = cells that did not change.

| From \ To | Integrated Capability | Fragmented Capability | Transit-Dependent | Motorcycle Lock-in |
|---|---|---|---|---|
| Integrated Capability | 162 | 0 | 0 | 0 |
| Fragmented Capability | 0 | 69 | 0 | 0 |
| Transit-Dependent | 0 | 0 | 69 | 0 |
| Motorcycle Lock-in | 0 | 0 | 0 | 162 |

## Interpretation

If κ ≥ 0.70 between minmax and log_minmax, typology findings are robust to the
choice of RAC scaling. If κ < 0.70, the Discussion should acknowledge that
log-transform re-ranks a meaningful fraction of cells and consider it as
a co-equal specification rather than just a robustness check.

The SMCI mean under log_minmax will be higher than under minmax because the
long right tail of RAC_raw is compressed — this does not invalidate the primary
specification but should be disclosed when reporting headline means.
