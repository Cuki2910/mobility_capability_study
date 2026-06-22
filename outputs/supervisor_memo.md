# Supervisor Memo: Ocean Park Pilot

## Result Snapshot
- Grid cells: 462
- Mean SMCI Scenario A: 0.0053
- Mean SMCI Scenario B: 0.0092
- Mean Delta_SMCI: 0.0038
- Share improved: 31.82%

## Typology Counts, Scenario B
- Motorcycle Lock-in: 127
- Integrated Capability: 127
- Fragmented Capability: 104
- Transit-Dependent: 104

## Confirmed Real Data
- OSM pilot graph/POI/grid manifest present: True.
- VinBus Ocean Park geometry file present: True.
- Processed pilot metrics rows: 462.
- WorldPop/GHSL raster metadata verified: raster data\raw\worldpop\vnm_ppp_2020.tif, ~92.77m resolution.

## Inferred / Proxy Metrics
- Transit accessibility is network-v1/proxy where timetable and stop-access detail is incomplete.
- Network B GTFS status: baseline_limited.
- Population proxy decision: allow_fine_grained_proxy (raster data\raw\worldpop\vnm_ppp_2020.tif).

## Unresolved Caveats
- Network B GTFS status: baseline_limited.
- Population raster is verified but not yet integrated into MAI magnitude weighting.
- POI manual spot-check records completed: 0; target >= 20.
- Motorcycle validation remains manual consumer-app spot checks; no Google TWO_WHEELER bulk API.

## Next Decisions
- Confirm Network B currency or keep it explicitly baseline-limited.
- Complete manual Google Maps motorcycle spot-check template.
