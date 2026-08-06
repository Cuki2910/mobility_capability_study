# West Tay Mo Data Setup Report

Generated UTC: 2026-07-02T10:13:49.500908+00:00
Site config: `config\sites\west_taymo.yml`

## Seed Bbox

- Center: 21.0027, 105.7472
- Half box km: 2.5
- Bbox W/S/E/N: (105.72467747747748, 20.98017747747748, 105.76972252252253, 21.025222522522522)

## Data Artifacts

| key | path | exists | size_bytes |
| --- | --- | --- | --- |
| grid | data\interim\west_taymo_grid.gpkg | True | 192512.0 |
| walk_graph | data\raw\west_taymo_walk_network.graphml | True | 5670603.0 |
| drive_graph | data\raw\west_taymo_drive_network.graphml | True | 1140665.0 |
| osm_pois | data\interim\west_taymo_osm_pois.gpkg | True | 200704.0 |
| overture_pois | data\raw\west_taymo_overture_pois.gpkg | True | 135168.0 |
| merged_pois | data\interim\west_taymo_merged_pois.gpkg | True | 258048.0 |
| landuse_poi_synthetic | data\interim\west_taymo_landuse_poi_synthetic.gpkg | True | 106496.0 |
| merged_pois_economic | data\interim\west_taymo_merged_pois_economic.gpkg | True | 258048.0 |
| merged_pois_observed | data\interim\west_taymo_merged_pois_observed.gpkg | False | nan |
| building_footprints | data\raw\west_taymo_building_footprints.gpkg | True | 15085568.0 |
| worldpop_csv | data\interim\west_taymo_grid_worldpop.csv | True | 19633.0 |
| accessibility_inputs | data\interim\west_taymo_accessibility_inputs.csv | True | 453715.0 |
| metrics | data\processed\west_taymo_metrics.csv | True | 676206.0 |

## Gate Reminder

- Run proxy mode first (`pipeline.default_opportunity_basis=proxy`).
- Promote `observed_strict` only after `observed_audit` has `needs_source=0`.
- Boundary labels require Smart City and Tay Mo core boundary layers.
