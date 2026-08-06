# Dasymetric Population Exposure Sensitivity

> This is a population-exposure sensitivity. NAI, MAI, RAC, SMCI, and typology are unchanged.

## Population Conservation

- Baseline aggregated population: 78815.6584
- Dasymetric allocated population: 78815.6581
- Difference: -0.0003
- Footprint-weighted allocation: 63638.5168
- Area-fallback allocation where a source pixel has no building: 15177.1413

## Exposure Comparison

| Metric | Baseline WorldPop | Dasymetric sensitivity | Difference |
| --- | ---: | ---: | ---: |
| Population-weighted SMCI_B | 0.012862 | 0.012906 | 0.000044 |
| Population share: Fragmented Capability | 16.0127% | 16.3389% | 0.3262% |
| Population share: Integrated Capability | 34.6622% | 34.7973% | 0.1351% |
| Population share: Motorcycle Lock-in | 33.8944% | 33.6347% | -0.2598% |
| Population share: Transit-Dependent | 15.4307% | 15.2291% | -0.2016% |

## Limitation

Building footprints are not dwelling counts, floor area, height, or residential-use labels. This sensitivity reallocates only within WorldPop source pixels and retains an area fallback for pixels without footprints; it must not be interpreted as a building-level population estimate.
