# Population-Weighted SMCI Cross-Check

Population weights from WorldPop 2020 (~92.77m raster, aggregated by 250m grid cell).
This is a post-hoc cross-check only — no formula changes.

Total estimated population in study area: 78,816
Cells with non-zero population: 462 / 462

## SMCI Mean Comparison

| Metric | Unweighted | Population-weighted | Bias |
|---|---|---|---|
| Mean SMCI_B | 0.0881 | 0.0862 | -2.2% |
| Mean SMCI_A | 0.0497 | 0.0604 | — |
| Mean Delta SMCI | 0.0384 | 0.0259 | — |
| Share improved | 67.10% | 65.34% | — |

Population-weighted mean SMCI_B is lower than the unweighted mean by 2.2%.

## Population–SMCI Rank Correlation

Spearman ρ(population, SMCI_B) = -0.0182 (p = 6.967e-01)

Near-zero correlation: population is roughly evenly distributed across SMCI levels.
Unweighted and population-weighted means are similar.

## Population Share by Typology (Scenario B)

| Typology | Population share |
|---|---:|
| Integrated Capability | 29.8% |
| Fragmented Capability | 20.9% |
| Transit-Dependent | 17.0% |
| Motorcycle Lock-in | 32.4% |

## Interpretation

If population-weighted and unweighted SMCI means differ substantially (>10%),
the Results section should report both to avoid misrepresenting the experience
of the majority of residents. The typology population shares reveal whether
the largest resident groups are in Integrated Capability or Motorcycle Lock-in cells.
