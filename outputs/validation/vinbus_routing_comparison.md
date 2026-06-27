# VinBus Routing Comparison

Verdict: **PROMOTE_STOPS**

## Inputs

- Stop/platform nodes extracted: 254
- Cells compared: 462
- Per-cell comparison CSV: `outputs\validation\vinbus_routing_comparison.csv`

## Agreement

- Typology kappa, corridor vs stops: 0.714
- Spearman rho, SMCI_B: 0.979
- Spearman rho, RAC_B: 0.586
- Relabelled cells: 94/462 (20.3%)

## Typology Counts

| Typology B | Corridor | Stops |
|---|---:|---:|
| Motorcycle Lock-in | 155 | 169 |
| Integrated Capability | 155 | 169 |
| Fragmented Capability | 76 | 62 |
| Transit-Dependent | 76 | 62 |

## Recommendation

Use stop-level VinBus routing as the primary Network C specification. Keep corridor routing as a sensitivity/proxy comparison.
