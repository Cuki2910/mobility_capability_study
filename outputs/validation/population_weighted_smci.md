# Population-Weighted SMCI Cross-Check

Population weights from WorldPop 2020 (~92.77m raster, aggregated by 250m grid cell).
This is a post-hoc cross-check only — no formula changes.

Total estimated population in study area: 78,816
Cells with non-zero population: 462 / 462

## SMCI Mean Comparison

| Metric | Unweighted | Population-weighted | Bias |
|---|---|---|---|
| Mean SMCI_B | 0.1711 | 0.1730 | +1.1% |
| Mean SMCI_A | 0.1470 | 0.1494 | — |
| Mean Delta SMCI | 0.0242 | 0.0236 | — |
| Share improved | 60.82% | 63.48% | — |

Population-weighted mean SMCI_B is higher than the unweighted mean by 1.1%.

## Population–SMCI Rank Correlation

Spearman ρ(population, SMCI_B) = -0.0074 (p = 8.746e-01)

Near-zero correlation: population is roughly evenly distributed across SMCI levels.
Unweighted and population-weighted means are similar.

## Population Share by Typology (Scenario B)

| Typology | Population share |
|---|---:|
| Integrated Capability | 34.7% |
| Fragmented Capability | 16.0% |
| Transit-Dependent | 15.4% |
| Motorcycle Lock-in | 33.9% |

## Interpretation

If population-weighted and unweighted SMCI means differ substantially (>10%),
the Results section should report both to avoid misrepresenting the experience
of the majority of residents. The typology population shares reveal whether
the largest resident groups are in Integrated Capability or Motorcycle Lock-in cells.
