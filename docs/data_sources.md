# Data Source Status

Last updated: 2026-06-27. Update this table as data is actually obtained; do not trust the proposal text's data-source list as confirmation that data exists.

| Source | Needed for | Status | Notes |
| --- | --- | --- | --- |
| OSM walking/driving network | NAI, RAC denominator, Network A/D | **Fetched for pilot** | `scripts/fetch_osm_data.py` wrote `data/raw/pilot_walk_network.graphml` and `data/raw/pilot_drive_network.graphml`. Manifest counts: 6,846 walk nodes / 20,024 walk edges; 1,401 drive nodes / 3,408 drive edges. |
| OSM POIs (schools, retail, healthcare, parks) | NAI | **Fetched + spot-checked for pilot** | `data/interim/pilot_pois.gpkg` has 106 POIs. Manual/web spot-check sample completed 20/20 in `data/interim/poi_spot_check.csv`: 14 confirmed, 2 duplicate, 2 misclassified, 2 missing/unverified. |
| Building footprints (VIDA Google-Microsoft-OSM / Google Open Buildings V3) | Land-use mask, built-cell filter, WorldPop cross-check, MAI weighting proxy | **Fetched + aggregated for pilot** | `scripts/fetch_building_footprints.py` fetched 41,816 VIDA footprints at confidence >=0.70 to `data/raw/building_footprints.gpkg`. `scripts/aggregate_building_footprints.py` wrote `data/interim/grid_building_footprints.gpkg`: 455/462 cells have buildings, 30,988 grid-intersecting footprints, total footprint area ~3.53M m2. Use this before trusting empty/zero cells: classify grid cells as built / water-park-open-space / low-built, compute building count and footprint area per 250m cell, then cross-check WorldPop. |
| Hanoi general GTFS | Network B (baseline public transport) | **Downloaded; baseline_limited (pre-VinBus vintage)** | `data/raw/hanoi_gtfs.zip` present (World Bank CC-BY 4.0, 1.51 MB). `scripts/check_hanoi_gtfs.py` reports `status=baseline_limited`, service dates 2018-01-01 to 2018-12-31, 224 routes, 7,670 stops, 6,713 trips. Per Decision #10: 2018 vintage predates VinBus commercial launch (Sep 2021) and is treated as the deliberate pre-intervention transit baseline. Stop geometry valid for stop_accessibility(); timetable used for relative magnitude only. If a post-2021 feed is found, run alongside as a sensitivity check. |
| MobilityDatabase / TUMI GTFS catalog check | Network B feed validation | **Dead end — no current-service feed found** | MobilityDatabase: 0 Hanoi hits. TUMI Datahub: inaccessible as of 2026-06-27 (site down/blocked). No current-service (post-2021) Hanoi GTFS source identified. Keep 2018 World Bank GTFS (`data/raw/hanoi_gtfs.zip`) as the deliberate pre-VinBus Network B baseline (Decision #10); report as a design choice and limitation, not missing data. Future work only: Buyt Ha Noi app / timbus.vn scrape if current-service sensitivity is required. See `outputs/validation/gtfs_catalog_check.md` for prior catalog search log. |
| VinBus E-route geometry | Network C, MAI, RAC numerator | **No official GTFS; scraped pseudo-GTFS built + QC'd** | VinBus publishes no official GTFS. `scripts/scrape_vinbus.py` scrapes publicly accessible VinBus web-app API responses (`maps.vinbus.vn`) and packages a pseudo-GTFS; `scripts/fix_vinbus_gtfs.py` repairs frequency/headway/time-format issues, writing `data/raw/vinbus_pseudo_gtfs_fixed/` (drop-in). QC 2026-06-27: 176 routes / 5,631 stops / 19,625 stop_times; headway 5–48 min (median 15, OCP1/OCP2 imputed 10); 0 bad time formats, 0 duplicate short_names, 0 non-TC routes missing frequencies, 0 orphan stop_times stop_ids, 1/5,631 stop coord out-of-bbox; calendar service window 2025-01-01→2025-12-31 (current-service). Frequency-based (stop_times keyed on route_id+direction_id+stop_sequence, no trip_id) — adequate for stop-geometry routing. No private user data, authentication bypass, or personal data are used, but licensing/ToS uncertainty remains; treat derived route tables as academic reproducibility artifacts and replace with official GTFS if available. **Primary Network C source** in `build_network_accessibility_inputs`. The earlier vinbus.vn street-by-street text and OSM relation geometry remain as cross-checks. |
| OSM bus route relations (operator=VinBus) | Network C (best case) | **Confirmed + promoted for stop-routing** | Full tags query found 39 VinBus relations on 2026-06-21. Focused geometry query found 10 Ocean Park-facing relations (`E01,E02,E03,E10,OCP1,OCP2`) with member geometry; saved to `data/raw/vinbus_overpass_relations_geom.json` and `data/interim/vinbus_route_summary.csv`. Stop-level extraction found 254 platform/stop nodes and is now the primary Network C implementation; corridor proxy remains sensitivity. |
| GHSL / WorldPop | Population; supply-side MAI magnitude weighting | **Integrated into MAI (Decision #19)** | `data/raw/worldpop/vnm_ppp_2020.tif` (~92.77m, adequate for 250m grid; `scripts/check_population_proxy_resolution.py`). Aggregated per cell → `data/interim/grid_worldpop.csv`. As of 2026-06-27, residential density scales each POI's opportunity weight inside MAI (`m_j = clip(sqrt(pop_density_j/median), 0.5, 2.0)`, all domains) — population is now a first-class MAI input, not post-hoc. No-pop sensitivity κ=0.976. Toggle via `--no-pop-weighting`. The demand-side post-hoc cross-check (`compute_population_weighted_smci.py`, residents at origin) is retained separately as an equity sensitivity. |
| Kontur Population | Population cross-check | **Not recommended as primary** | Kontur is multi-source but the public global product is 400m H3, coarser than the 250m analysis grid and the current ~92.77m WorldPop raster. Use only as a coarse sensitivity/context layer, not as an upgrade. |
| Nighttime lights (VIIRS/DMSP) | Economic opportunity proxy in MAI v8 | **Not fetched** | MAI v8 economic domain currently uses commercial POI density only. NTL would strengthen the proxy. Candidate source: NASA Black Marble VNP46A1 (daily, 500m). Fetch deferred; mark as sensitivity-only until fetched. |
| University enrollment figures | Higher-education domain in MAI v8 | **Not fetched; no campuses in pilot area** | No university campuses in pilot POI set (suburban residential study area). Fallback = campus area from OSM polygon if enrollment unavailable. Full-study data collection should add Hanoi university OSM nodes. |
| Google Maps motorcycle-mode (consumer app) | Travel-time spot-check | **Completed for pilot (Android)** | 10/10 named OD pairs measured in `outputs/validation/manual_motorcycle_validation_template.csv`; MAE ~1.90 minutes, bias ~-1.04 minutes (model tends optimistic). iOS support not used. |
| Google Maps TWO_WHEELER (Routes/Directions API, programmatic) | Bulk travel-time validation | **Likely NOT available for Vietnam** | Do not depend on bulk API routing. Use small manually sampled consumer-app checks. |
| Property-value / population-density gradients | External validation (Section 3.11) | **Source not identified** | Open TODO. |
| Overture Maps Places | POI supplement | **Fetched + gate passed; promoted** | `scripts/fetch_overture_pois.py` wrote `data/raw/overture_pois.gpkg` with 62 relevant places. `scripts/merge_poi_sources.py` wrote `data/interim/merged_pois.gpkg` and `outputs/poi_merge_summary.md`: 161 merged POIs = 7 `both`, 99 `osm_only`, 55 `overture_only`. Gate result: `outputs/validation/overture_gate_result.md` = PASS (55/55 confirmed, no severe category bias). `data/interim/merged_pois.gpkg` is now the primary POI layer. |

## Action Items, In Priority Order

1. Keep `data/interim/merged_pois.gpkg` as primary after Overture gate PASS; preserve `data/interim/overture_only_spot_check.csv` as the audit trail.
2. Use `outputs/validation/built_population_zero_access.md` when interpreting zero-NAI/zero-SMCI cells; do not dismiss zero inflation as open space.
3. Use WorldPop/nighttime-light/employment proxies for MAI magnitude weighting only if the paper moves beyond proxy-level MAI.
4. Download/check TUMI Hanoi Morning/Midday/Afternoon GTFS only as a future current-service/time-of-day sensitivity, not as a replacement for the 2018 pre-VinBus baseline.
5. Network C now uses the scraped + QC'd VinBus pseudo-GTFS (`data/raw/vinbus_pseudo_gtfs_fixed/`) as primary geometry; OSM stop-routing and corridor proxy remain sensitivity. Re-scrape (`scripts/scrape_vinbus.py` → `scripts/fix_vinbus_gtfs.py`) if VinBus publishes an official feed or routes change.

## Reproducible Commands

```powershell
# OSM and network data (requires internet):
python scripts/check_vinbus_overpass.py --bbox 20.85 105.75 21.15 106.05
python scripts/check_vinbus_overpass.py --bbox 20.85 105.75 21.15 106.05 --refs E01,E02,E03,E10,OCP1,OCP2 --split-refs --geom --output data/raw/vinbus_overpass_relations_geom.json --summary-csv data/interim/vinbus_route_summary.csv
python scripts/fetch_osm_data.py
python scripts/check_hanoi_gtfs.py
python scripts/check_mobility_database.py --query Hanoi --output data/interim/mobility_database_hanoi_candidates.csv

# Building footprints and Overture POIs (requires internet):
python scripts/fetch_building_footprints.py
python scripts/aggregate_building_footprints.py
python scripts/fetch_overture_pois.py
python scripts/merge_poi_sources.py

# Pipeline (run in order, no internet needed):
python scripts/audit_pois.py
python scripts/build_accessibility_inputs.py --mode network --gtfs-status baseline_limited
python scripts/run_pilot_metrics.py
python scripts/aggregate_worldpop_by_grid.py
python scripts/compute_population_weighted_smci.py
python scripts/rac_scaling_sensitivity.py
python scripts/rac_time_only_sensitivity.py
python scripts/make_validation_report.py
python scripts/make_supervisor_memo.py
```
