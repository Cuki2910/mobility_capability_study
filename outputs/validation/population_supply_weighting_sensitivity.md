# Supply-Side Population Weighting Sensitivity (Decision #19)

Compares the primary specification (MAI opportunity weights scaled by residential
density around each POI) against a no-population baseline (`--no-pop-weighting`).

## Setup

- POI source: `data/interim/merged_pois.gpkg` (208 merged OSM+Overture+economic POIs).
- Multiplier: `m_j = clip( sqrt(pop_density_j / median), 0.5, 2.0 )`, median-centered.
- 193/208 POIs matched to a grid cell; multiplier range [0.50, 1.81], mean 0.98.

## Results

| Metric | No-pop baseline | Supply-side pop (primary) |
|---|---|---|
| mean SMCI_B | 0.0902 | 0.0881 |
| typology_B partition | 161/161/70/70 (≈) | 160/160/71/71 |
| MAI domain shares | economic 54.1 / higher_ed 24.7 / health 5.8 / commercial 15.5 | unchanged |

- **Typology kappa (pop vs no-pop) = 0.976**, 8/462 cells relabelled — highly robust.
- mean SMCI_B shifts only −2.3% (0.0902 → 0.0881); no shock.
- Domain decomposition unchanged → population scales all domains proportionally and does
  not reintroduce the single-domain over-domination caught in Decision #18.

## Interpretation

Adding supply-side population to MAI is a principled accessibility refinement (denser
catchment = larger market for a sited opportunity) that does **not** materially disturb
the typology partition or the SMCI distribution. The primary specification retains it;
the no-pop run is reported here as robustness evidence, analogous to the RAC_time-only
sensitivity for VIF.

VIF is essentially unchanged (MAI≈20.2, RAC≈22.8): population scales MAI and the RAC_opp
numerator proportionally, so it neither worsens nor cures the structural MAI/RAC
collinearity. RAC_time-only remains the VIF remedy (see decisions #3).
