# Western Extension Protocol - Tay Mo / Vinhomes Smart City

**Status:** candidate extension, not yet promoted to the primary comparison design.

This document records the proposed west-side extension: Tay Mo ward / Vinhomes
Smart City as a west-Hanoi counterpart to the current east-side Ocean Park
study. It should be treated as a **pre-analysis design note** until matching
variables are measured from the pipeline.

## 1. Why this extension is attractive

Tay Mo is a strong candidate because it can support a **double pairwise
comparison**:

| Side | Planned megaproject | Organic / inherited urban fabric |
| --- | --- | --- |
| East | Vinhomes Ocean Park | Trau Quy core |
| West | Vinhomes Smart City | Tay Mo core |

This is stronger than a single extra site because it tests whether the
planned-versus-organic contrast appears on both sides of Hanoi, not only around
Ocean Park.

The west-side comparison also helps answer a reviewer concern: whether the
paper is describing one unusual enclave or a broader megaproject pattern in
Hanoi.

## 2. What must be verified

The user-proposed matching profile is plausible but must be measured rather
than copied into the paper:

| Variable | User-proposed value | Required verification |
| --- | ---: | --- |
| Network distance to Hoan Kiem | about 12.5 km | OSM drive-network shortest path from area centroid |
| Area | about 5.56 km2 | official / GIS boundary or fixed comparable bbox |
| Population | about 46,894 | official ward figure and/or WorldPop aggregation |
| Density | about 8,400 people/km2 | recompute from verified area + population |
| Spillover from Ocean Park | none | confirm west-side independence; still handle Smart City spillover internally |

Do not use straight-line distance as the matching metric. Use network distance
over the actual routable road graph, following `docs/comparison_site_protocol.md`.

## 3. Treatment definitions

The key design issue is that Tay Mo contains both inherited village fabric and
Vinhomes Smart City. These must not be collapsed into one surface.

Recommended units:

| Unit | Role | Notes |
| --- | --- | --- |
| Vinhomes Smart City core | planned-west treatment | master-planned Vingroup site; has VinBus service |
| Tay Mo core | organic-west control | older lane/village/service fabric adjacent to Smart City |

The boundary must separate Smart City cells from Tay Mo core cells. Mixed cells
should be flagged and either dropped or analyzed as a transition band.

## 4. Scenario logic

Use the same guardrail as the east-side protocol:

- **Planning-form comparison:** use Scenario A for all planned/organic units
  where possible, so the built form is not confused with the private bus layer.
- **Bus-intervention comparison:** report VinBus / electric-bus contribution as
  a separate delta layer for sites with VinBus service.

For the west side, this likely means:

| Question | Comparison |
| --- | --- |
| Does planned form differ from organic form? | Smart City Scenario A vs Tay Mo core Scenario A |
| What does the private electric-bus layer add? | Smart City Scenario B - Scenario A |
| Is the pattern east-west consistent? | pooled/shared-scale comparison across Ocean Park, Trau Quy, Smart City, Tay Mo |

## 5. Go / no-go gates

Promote Tay Mo / Smart City only if these gates pass:

1. **Distance match:** Tay Mo / Smart City network distance to Hoan Kiem is
   within +/-15% of Ocean Park, or the mismatch is explicitly modeled as a
   west-side limitation.
2. **Boundary separability:** Smart City core and Tay Mo core can be separated
   cleanly enough that planned and organic cells are not mostly mixed.
3. **Data parity:** OSM, Overture, building footprints, WorldPop, POI audit, and
   observed-opportunity magnitudes can be collected with the same source tiers
   used in Ocean Park.
4. **Transit comparability:** conventional bus and VinBus layers can be encoded
   without giving one site a data-quality advantage.
5. **Scale parity:** the west-side grid extent is comparable to the Ocean Park
   grid or is analyzed with shared-scale pooled normalization.

If these fail, keep Tay Mo as a discussion/future-work candidate rather than a
headline empirical extension.

## 6. Claim discipline

A four-site design is still observational. It can support:

- "The planned/organic capability contrast is similar or different across east
  and west Hanoi."
- "Megaproject cores perform as mobility enclaves when capability drops at the
  boundary."
- "VinBus adds capability unevenly across planned cores and adjacent organic
  fabric."

It still cannot support a clean causal claim that master planning alone causes
the difference.

Cross-site typology shares must not be compared using within-site median labels.
Use absolute SMCI/RAC values or pooled/shared-scale normalization, as required
by Decision #25.

## 7. Immediate measurement checklist

- [x] Import Smart City core boundary from OSM/Nominatim (`way 776941617`).
- [x] Trace Tay Mo organic core from OSM local fabric/building footprints after Overpass returned no usable administrative polygon.
- [ ] Measure network distance from both centroids to Hoan Kiem.
- [ ] Build identical 250 m grids and record area/cell counts.
- [ ] Aggregate WorldPop population and density.
- [ ] Fetch OSM walking/driving graphs for west-side bbox.
- [ ] Fetch and gate OSM/Overture POIs.
- [ ] Fetch building footprints and compute built-cell coverage.
- [ ] Check conventional bus stops/routes and VinBus west-side routes.
- [ ] Build observed-opportunity magnitude audit from scratch.

## 8. Implemented config-driven runbook

Primary config: `config/sites/west_taymo.yml`.

Dry-run smoke checks:

```powershell
python scripts/fetch_osm_data.py --site-config config/sites/west_taymo.yml --dry-run
python scripts/fetch_overture_pois.py --site-config config/sites/west_taymo.yml --dry-run
python scripts/fetch_building_footprints.py --site-config config/sites/west_taymo.yml --dry-run
python scripts/fetch_osm_landuse.py --site-config config/sites/west_taymo.yml --dry-run
python scripts/merge_poi_sources.py --site-config config/sites/west_taymo.yml --dry-run
python scripts/merge_economic_features.py --site-config config/sites/west_taymo.yml --dry-run
python scripts/aggregate_worldpop_by_grid.py --site-config config/sites/west_taymo.yml --dry-run
python scripts/derive_all_observed.py --site-config config/sites/west_taymo.yml --dry-run
python scripts/build_accessibility_inputs.py --site-config config/sites/west_taymo.yml --dry-run
python scripts/run_pilot_metrics.py --site-config config/sites/west_taymo.yml --dry-run
python scripts/label_site_cells.py --site-config config/sites/west_taymo.yml --dry-run
python scripts/west_site_setup_report.py --site-config config/sites/west_taymo.yml --dry-run
```

Actual data setup order after boundary files are available:

```powershell
python scripts/fetch_osm_data.py --site-config config/sites/west_taymo.yml
python scripts/fetch_overture_pois.py --site-config config/sites/west_taymo.yml
python scripts/merge_poi_sources.py --site-config config/sites/west_taymo.yml
python scripts/fetch_osm_landuse.py --site-config config/sites/west_taymo.yml
python scripts/merge_economic_features.py --site-config config/sites/west_taymo.yml
python scripts/fetch_building_footprints.py --site-config config/sites/west_taymo.yml
python scripts/aggregate_worldpop_by_grid.py --site-config config/sites/west_taymo.yml
python scripts/label_site_cells.py --site-config config/sites/west_taymo.yml
python scripts/build_accessibility_inputs.py --site-config config/sites/west_taymo.yml
python scripts/run_pilot_metrics.py --site-config config/sites/west_taymo.yml
python scripts/west_site_setup_report.py --site-config config/sites/west_taymo.yml
```

The config intentionally defaults West v1 to `opportunity_basis=proxy` for the
first full run. Switch to `observed_strict` only after
`outputs/west_taymo/observed_opportunity_gap_audit.csv` has no `needs_source`
rows.
