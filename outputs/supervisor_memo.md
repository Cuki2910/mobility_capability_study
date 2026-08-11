# Supervisor Memo: Ocean Park Pilot

## Result Snapshot
- Grid cells: <!-- headline:/n_cells|int -->462<!-- /headline -->
- Mean SMCI Scenario A: <!-- headline:/smci/mean_A|.4f -->0.1470<!-- /headline -->
- Mean SMCI Scenario B: <!-- headline:/smci/mean_B|.4f -->0.1711<!-- /headline -->
- Mean Delta_SMCI: 0.0242
- Share improved: <!-- headline:/delta_groups/improved|int -->281<!-- /headline --> cells (60.82%)
- Improved / unchanged / declined cells: 281 (60.82%) / 88 (19.05%) / 93 (20.13%)
- Distribution note: Mean SMCI is small mainly because RAC_B is compressed by an extreme max (mean normalized RAC_B=0.0819; p99=0.2116; max=1.0000) and zero-valued components make multiplicative SMCI exactly zero for many cells.

## Typology Counts, Scenario B
- Fragmented Capability: 60
- Integrated Capability: 171
- Motorcycle Lock-in: 171
- Transit-Dependent: 60

## Confirmed Real Data
- OSM pilot graph/POI/grid manifest present: True.
- VinBus Ocean Park geometry file present: True.
- Processed pilot metrics rows: 462.
- POI spot-check completed: 20/20 ({'confirmed': 14, 'misclassified': 2, 'duplicate': 2, 'missing_in_osm': 2}).
- Android motorcycle validation completed: 10/10; MAE=1.90 min, bias=-1.04 min.
- WorldPop/GHSL raster metadata verified: raster data\raw\worldpop\vnm_ppp_2020.tif, ~92.77m resolution.
- MobilityDatabase catalog checked for Hanoi GTFS candidates: 0 found.
- TUMI/Datahub GTFS candidates documented as future current-service/time-of-day sensitivity, not baseline replacement.
- Built/population zero-access audit completed with building footprints and WorldPop.
- Overture POI gate passed; merged OSM+Overture POI layer is now primary.
- Quick-look SVG maps and GIS map layer generated in outputs/maps/.

## Inferred / Proxy Metrics
- Transit accessibility is network-v1/proxy where timetable and stop-access detail is incomplete.
- Network B GTFS status: baseline_limited (vintage 2018; pre-VinBus conventional transit baseline (stop geometry valid; timetable reflects 2018 service, before VinBus commercial launch Sep 2021)).
- Population proxy decision: allow_fine_grained_proxy (raster data\raw\worldpop\vnm_ppp_2020.tif).

## Unresolved Caveats
- Network B uses 2018 GTFS as a pre-VinBus conventional transit baseline; it is not current-service validation.
- Population raster is verified but not yet integrated into MAI magnitude weighting.
- Transit metrics use stop-level VinBus routing; full timetable routing remains a future upgrade.
- Google TWO_WHEELER bulk API remains unavailable/unconfirmed; validation uses manual Android consumer-app checks.
- Building footprints and WorldPop are used as audit layers, not yet as primary MAI weights.
- Overture POI gate passed; keep the user-confirmed spot-check CSV as audit trail for the merged primary POI layer.

## Next Decisions
- Spot-check 55 Overture-only POIs and decide whether merged POIs can become primary.
- Decide whether to integrate building/population/employment proxy into MAI weighting or label current MAI as proxy-level.
- Use generated maps for supervisor review; final cartographic styling can come later.
- Prepare supervisor review using pilot results plus explicit proxy limitations.
