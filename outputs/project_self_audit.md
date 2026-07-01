# Project Self-Audit

## Snapshot

- grid_cells: 462
- mean_SMCI_A: 0.0070377752800668
- mean_SMCI_B: 0.0132898043722475
- share_improved: 0.6082251082251082
- gtfs_status: baseline_limited
- pre_vinbus_baseline: True
- poi_spot_checks: {'total': 20, 'completed': 20, 'breakdown': {'confirmed': 14, 'misclassified': 2, 'duplicate': 2, 'missing_in_osm': 2}}
- motorcycle_android_checks: {'rows': 10, 'android_completed': 10, 'has_android_column': True, 'mae_minutes': 1.9, 'bias_minutes': -1.0399999999999998}
- android_emulator: {'status_file': True, 'installed': True, 'motorcycle_mode_available': False}
- population_resolution: {'resolution_m': 92.76666629760172, 'grid_size_m': 250.0, 'decision': 'allow_fine_grained_proxy', 'adequate_for_250m_pilot': True, 'resolution_source': 'raster_metadata', 'raster': 'data\\raw\\worldpop\\vnm_ppp_2020.tif'}
- distribution_diagnostics: {'NAI_zero_share': 0.1904761904761904, 'SMCI_B_zero_share': 0.1904761904761904, 'improved_share': 0.6082251082251082, 'unchanged_share': 0.1904761904761904, 'declined_share': 0.2012987012987013}
- high_vif: False
- built_population_zero_access_audit: True
- merged_poi_sensitivity: True
- gtfs_catalog_check: True

## Strengths

- End-to-end pilot pipeline has real OSM graph/POI/grid inputs and processed metrics.
- WorldPop raster is downloaded and resolution-verified against the 250m grid.
- Current NAI/MAI/RAC VIF diagnostics are below threshold 5.
- 2018 Hanoi GTFS is documented as a deliberate pre-VinBus Network B baseline, not missing data.
- POI spot-check completed: 20/20 records reviewed ({'confirmed': 14, 'misclassified': 2, 'duplicate': 2, 'missing_in_osm': 2}).
- Android motorcycle validation completed: 10/10 OD pairs; MAE=1.90 minutes.
- Building footprints are fetched and aggregated by grid cell for built-cell masking and WorldPop cross-checks.
- Overture Places are fetched and merged with OSM POIs using source-agreement labels.
- Built/population zero-access audit is complete; zero inflation is checked against building footprints and WorldPop.
- Overture POI gate passed; merged OSM+Overture POI layer is primary.
- GTFS catalog check documents MobilityDatabase and TUMI/Datahub candidates without replacing the 2018 pre-VinBus baseline.
- Quick-look maps and GIS layers are generated for supervisor review.
- Supervisor review package index is available.
- Population raster is verified and supply-side WorldPop weighting is integrated into MAI.

## Blockers

- None

## Warnings

- Network B uses a 2018 pre-VinBus GTFS vintage; report as baseline and sensitivity limitation, not current service.
- Android emulator lacks motorcycle mode; physical Android measurements are used instead.

## Next Actions

- Preserve Overture gate audit trail and monitor merged POI layer for systematic errors.
- Preserve strict observed MAI audit trail and upgrade weak derived tiers with named facility sources where possible.
- Report Network B as a 2018 pre-VinBus baseline and keep post-2021 GTFS as a sensitivity target if found.
- Proceed to supervisor review with promoted RAC_time primary, full-RAC robustness, and explicit source-tier limitations.
