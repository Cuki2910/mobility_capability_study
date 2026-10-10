# Ocean Park local data recovery — 2026-10-10

The previous machine's untracked data were lost. Public sources were downloaded again into `data/raw/`; aligned layers are in `data/interim/`. This restores local inputs, not the exact historical source snapshot. Published files in `outputs/` were preserved.

| Source | Local recovery | Provenance / limitation |
| --- | --- | --- |
| OSM | Walking graph: 6,873 nodes / 20,126 edges; driving: 1,407 / 3,424; 161 POIs; 462 grid cells; 50 economic land-use candidates | Fresh acquisition; `data/interim/pilot_data_manifest.json`. The new POI spot-check is unchecked. |
| Hanoi GTFS | `data/raw/hanoi_gtfs.zip`; 224 routes, 7,670 stops, 6,713 trips | World Bank midday feed; service dates **2018**, Network B `baseline_limited`. Source URL and QC in `data/interim/hanoi_gtfs_source.json` and `hanoi_gtfs_status.json`. |
| VinBus | 176 raw API details; pseudo-GTFS: 176 routes, 5,494 stops, 13,232 stop-sequences; fixed feed: 173 frequency rows | Public route-list/detail API. Directions separated correctly. OCP1/OCP2 headways imputed at 10 minutes. Calendar is a **synthetic legacy 2025 placeholder**, not verified current service dates. Geometry routing does not use it. `data/raw/vinbus_raw_json/scrape_summary.json`. |
| OSM VinBus relations | 10 Ocean Park-facing relations | E01/E02/E03/E10/OCP1/OCP2; fallback/cross-check, not the primary Network C source. |
| VIDA buildings | 41,816 footprints; 455/462 built cells | VNM country GeoParquet, confidence >=0.70; 30,988 grid-intersecting footprints, ~3.53 million m². |
| Overture | Release **2026-09-23.1**; 2,137 candidate places; 1,868 merged POIs | Historical `2026-06-17.0` release no longer hosted. New taxonomy mapped to the existing broad categories; detail retained. **1,707 Overture-only POIs unchecked**; recovery gate INCOMPLETE. Historical 55/55 confirmations do not apply. |
| WorldPop | `data/raw/worldpop/vnm_ppp_2020.tif`: valid geographic subset covering Ocean Park grid plus buffer | Official VNM 2020 raster, DOI `10.5258/SOTON/WP00645`, record 6449. Original pixel values/resolution/CRS preserved; this file is **not the full Vietnam raster**. See `data/interim/worldpop_recovery_source.json`. |

WorldPop's official server ignores HTTP range requests. Recovery reads the complete TIFF strips needed for Ocean Park from a sequential download, then writes a standalone GeoTIFF. The incomplete national download is never used as a raster input. Validate with:

```sh
python scripts/archive/check_population_proxy_resolution.py --raster data/raw/worldpop/vnm_ppp_2020.tif
python scripts/aggregate_worldpop_by_grid.py --output data/interim/grid_worldpop_recovery.csv
```

## Historical exports recovered separately

- Ocean Park boundary recovered from the published interactive map's OSM way 761986888: `data/interim/ocean_park_1_boundary.geojson`.
- Historical population table recovered from the published map: `data/interim/grid_worldpop.csv`, 462 cells, total 78,815.6584. A fresh raster aggregation is saved separately as `grid_worldpop_recovery.csv`: population matches every historical cell exactly; all 462 cells have valid pixels. Raster resolution: 92.7667 m. Comparison evidence: `data/interim/worldpop_recovery_comparison.json`.
- Historical accessibility properties recovered from `outputs/maps/pilot_metrics_map.geojson`: `data/interim/published_accessibility_inputs_recovered.csv`. This export also contains legacy derived metric columns; it is not a fresh network computation.
- `data/processed/pilot_metrics.csv` reconstructed from those historical accessibility inputs using current `src/pilot.py`; reproduces published mean SMCI_A 0.1469502071, SMCI_B 0.1711114883, Delta_SMCI 0.0241612812. It does not use the newly downloaded POIs/networks.

The new merged/observed POI layers are recovery candidates only. Use OSM-only candidates for previews until manual review; do not run the default pipeline to publish them as primary. A fresh `pilot_accessibility_inputs.csv` has intentionally not been built. Derived opportunity magnitudes are source-backed estimates, not new named-site observations. Historical manual motorcycle checks remain in tracked `outputs/validation/`.

## Acquisition repairs

`scripts/scrape_vinbus.py`: portable paths, public API acquisition with retries and cache resume, distinct route directions, explicit synthetic-calendar annotation. `scripts/fix_vinbus_gtfs.py`: skips macOS metadata. `scripts/fetch_building_footprints.py`: verified HTTPS path-style S3 access. `scripts/fetch_overture_pois.py`: available release, validated `--release`, current taxonomy. Offline regressions: `tests/test_data_recovery.py`.

Dependencies installed in `/Users/cuki2910/.venvs/mobility_capability_study` from `requirements-fetch.txt`. Data remain local/ignored by Git; a separate backup is needed to retain this acquisition. Hashes and local inventory: `data/interim/data_recovery_manifest.json`.

Validation: 169 tests passed, 2 browser tests skipped; `scripts/agent_gate.py` passed. Geometry checks found no invalid recovered POI/grid/building features; pseudo-GTFS route/stop references and coordinate ranges passed. SHA-256 confirmed all 149 pre-existing tracked output files unchanged. The gate's self-audit uses historical output artifacts and cannot certify the new POI review; the recovery gate remains INCOMPLETE.
