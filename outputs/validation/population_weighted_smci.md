# Population-Weighted SMCI Cross-Check

Population weights from WorldPop 2020 (~92.77m raster, aggregated by 250m grid cell).
This is a post-hoc cross-check only — no formula changes.

Total estimated population in study area: 78,816
Cells with non-zero population: 462 / 462

## SMCI Mean Comparison

| Metric | Unweighted | Population-weighted | Bias |
|---|---|---|---|
| Mean SMCI_B | 0.0125 | 0.0122 | -2.9% |
| Mean SMCI_A | 0.0064 | 0.0064 | — |
| Mean Delta SMCI | 0.0061 | 0.0058 | — |
| Share improved | 61.90% | 64.45% | — |

Population-weighted mean SMCI_B is lower than the unweighted mean by 2.9%.

## Population–SMCI Rank Correlation

Spearman ρ(population, SMCI_B) = -0.006 (p = 8.973e-01)

Near-zero correlation: population is roughly evenly distributed across SMCI levels.
Unweighted and population-weighted means are similar.

## Population Share by Typology (Scenario B)

| Typology | Population share |
|---|---:|
| Integrated Capability | 34.9% |
| Fragmented Capability | 15.8% |
| Transit-Dependent | 14.9% |
| Motorcycle Lock-in | 34.5% |

## Interpretation

If population-weighted and unweighted SMCI means differ substantially (>10%),
the Results section should report both to avoid misrepresenting the experience
of the majority of residents. The typology population shares reveal whether
the largest resident groups are in Integrated Capability or Motorcycle Lock-in cells.
