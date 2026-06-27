# Economic-Domain Inclusion Sensitivity

Does the conclusion depend on the 47 economic POIs added in Decision #18?
Compares the full pipeline on the pre-enrichment 161-POI layer vs the enriched
208-POI layer.

| Metric | Value |
|---|---|
| Typology Cohen's κ (base161 vs econ208) | 0.8646 |
| Spearman ρ SMCI_B | 0.9596 |
| Spearman ρ MAI_B | 0.9854 |
| Cells relabelled | 44 / 462 (9.5%) |

## Typology distribution shift

| Typology | base161 | econ208 |
|---|---|---|
| Fragmented Capability | 63 | 68 |
| Integrated Capability | 168 | 163 |
| Motorcycle Lock-in | 168 | 163 |
| Transit-Dependent | 63 | 68 |

## Interpretation

Conclusions are **robust** to the economic enrichment: the typology partition is near-identical (κ close to 1).
