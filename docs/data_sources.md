# Data Source Status

Last updated: 2026-06-21. Update this table as data is actually obtained; do not trust the proposal text's data-source list as confirmation that data exists.

| Source | Needed for | Status | Notes |
|---|---|---|---|
| OSM walking/driving network | NAI, RAC denominator, Network A/D | **Fetched for pilot** | `scripts/fetch_osm_data.py` wrote `data/raw/pilot_walk_network.graphml` and `data/raw/pilot_drive_network.graphml`. Manifest counts: 6,846 walk nodes / 20,024 walk edges; 1,401 drive nodes / 3,408 drive edges. |
| OSM POIs (schools, retail, healthcare, parks) | NAI | **Fetched for pilot** | `data/interim/pilot_pois.gpkg` has 106 POIs. Quality/completeness in Vietnam still needs spot-checking. |
| Hanoi general GTFS | Network B (baseline public transport) | **Candidate identified; download blocked locally** | `scripts/fetch_hanoi_gtfs.py` targets TUMI Hanoi GTFS Midday (`hanoi_gtfs_md.zip`) and writes `data/interim/hanoi_gtfs_source.json`. On 2026-06-21 the download timed out from this environment, so `data/raw/hanoi_gtfs.zip` is absent and `scripts/check_hanoi_gtfs.py` reports `missing`. Treat Network B as baseline-limited until the feed is downloaded and validated. |
| VinBus E-route geometry | Network C, MAI, RAC numerator | **No public GTFS found** | vinbus.vn publishes street-by-street text descriptions for E01-E09. `maps.vinbus.vn` likely serves geometry via an internal API but is robots-disallowed for automated fetch. |
| OSM bus route relations (operator=VinBus) | Network C (best case) | **Confirmed available** | Full tags query found 39 VinBus relations on 2026-06-21. Focused geometry query found 10 Ocean Park-facing relations (`E01,E02,E03,E10,OCP1,OCP2`) with member geometry; saved to `data/raw/vinbus_overpass_relations_geom.json` and `data/interim/vinbus_route_summary.csv`. Network C should use OSM relations before manual digitization. |
| GHSL / WorldPop | Population, employment proxy | **WorldPop raster downloaded** | `data/raw/worldpop/vnm_ppp_2020.tif` downloaded from WorldPop. `scripts/check_population_proxy_resolution.py --raster data/raw/worldpop/vnm_ppp_2020.tif` reports ~92.77m resolution, `resolution_source=raster_metadata`, adequate for 250m grid. |
| Nighttime lights | Employment density proxy | Available | Candidate secondary proxy. |
| University enrollment figures | MAI magnitude weighting | **Not yet checked** | Fallback proxy = building footprint area if enrollment is not public. |
| Google Maps motorcycle-mode (consumer app) | Travel-time spot-check | **Confirmed to exist for Vietnam (Android)** | iOS support historically unclear; reverify manually. |
| Google Maps TWO_WHEELER (Routes/Directions API, programmatic) | Bulk travel-time validation | **Likely NOT available for Vietnam** | Do not depend on bulk API routing. Use small manually sampled consumer-app checks. |
| Property-value / population-density gradients | External validation (Section 3.11) | **Source not identified** | Open TODO. |

## Action Items, In Priority Order

1. Complete at least 20 manual records in `data/interim/poi_spot_check.csv`; file now includes lat/lon, OSM URLs, and Google Maps search URLs.
2. Download or manually place `data/raw/hanoi_gtfs.zip`, then run `scripts/check_hanoi_gtfs.py` to unlock Network B stops.
3. Use the downloaded WorldPop raster for real population/opportunity weighting if MAI magnitude weighting is needed.
4. Replace transit corridor proxies with stop/timetable-derived metrics once GTFS is valid.

## Reproducible Commands

```powershell
python scripts/check_vinbus_overpass.py --bbox 20.85 105.75 21.15 106.05
python scripts/check_vinbus_overpass.py --bbox 20.85 105.75 21.15 106.05 --refs E01,E02,E03,E10,OCP1,OCP2 --split-refs --geom --output data/raw/vinbus_overpass_relations_geom.json --summary-csv data/interim/vinbus_route_summary.csv
python scripts/fetch_osm_data.py
python scripts/check_hanoi_gtfs.py
python scripts/audit_pois.py
python scripts/build_accessibility_inputs.py --mode network --gtfs-status baseline_limited
python scripts/run_pilot_metrics.py
python scripts/make_validation_report.py
python scripts/make_supervisor_memo.py
```
