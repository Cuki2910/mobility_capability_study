# OSM / VinBus data workflow

## Check before fetching

Read `docs/data_sources.md` and the latest relevant decisions, then verify required files in this checkout. Distinguish missing local data from a source that has never been acquired. Do not automatically re-fetch data during cleanup or a documentation audit.

For recovered or refreshed inputs, also read `docs/data_recovery.md` and the relevant local provenance/QC manifests in `data/interim/`. Separate newly downloaded sources, reconstructed historical exports, and reviewed primary inputs. Historical counts and completed reviews do not prove the replacement layers are approved.

## Network sources

- **Network B:** `data/raw/hanoi_gtfs.zip`, World Bank file vintage 2020 with service dates 2018. The deliberate pre-VinBus baseline is `baseline_limited`; a verified newer feed is a separate sensitivity, not an automatic replacement (DEC-010).
- **Network C primary:** `data/raw/vinbus_pseudo_gtfs_fixed/`, public-API-derived pseudo-GTFS processed by `scripts/fix_vinbus_gtfs.py`. No official VinBus GTFS is available; record licensing and timetable limitations.
- **Network C fallback/sensitivity:** OSM VinBus relations, then the documented corridor proxy. Missing OSM relations alone do not imply missing primary VinBus data. Do not jump to manual digitization before checking the pseudo-GTFS source and the existing fallback artifacts.
- **Network A/D:** OSM walking/driving GraphML; D additionally requires the production motorcycle calibration CSV.

## Acquisition and quality checks

- Inspect `scripts/scrape_vinbus.py` and its paths before executing: legacy scripts may contain Windows-specific locations. Use the scrape/QC workflow only when acquisition or refresh is requested.
- Validate pseudo-GTFS stop coordinates, route/stop references, distinct direction groups, frequency/headway fields, time formats, and service windows. Check `scrape_summary.json` for synthetic calendar dates; do not relabel them as verified current service. Disclose imputed fields and pseudo-GTFS limitations; ignore macOS `._*` metadata files when enumerating inputs.
- For an OSM geometry cross-check, use `scripts/archive/check_vinbus_overpass.py` or the optional local [query generator](../scripts/vinbus_overpass_query.py). The generator prints a query; it does not fetch or validate data.
- Include Ocean Park-facing E-routes and OCP1/OCP2 when checking route coverage. A Hanoi-wide query avoids dropping routes that extend beyond the study boundary; inspect relevant refs instead of assuming E01-E09 is exhaustive.
- WorldPop, building footprints, and observed opportunity magnitudes remain separate input requirements. Check local files and provenance before calling the network inputs complete.
- Record source URL/release, acquisition time, study bounds, filters, counts, and hashes. If a pinned release is unavailable, disclose the replacement and check its schema/category mapping. Generate a new POI review and gate report for changed candidates; never transfer old confirmations to replacement rows.
- Validate raster CRS, resolution, extent, nodata, and readable pixels for every study cell. A complete geographic subset is acceptable when documented; a partial national download is not. Compare recovered population against historical aggregates where available, preserving the two provenances.
- Before promoting refreshed inputs, require the applicable review gates. Keep recovery/previews in `data/interim/` and preserve published `outputs/`; recovering historical metrics from published maps does not mean the refreshed networks reproduce them.

Keep downloads immutable in `data/raw/`, cleaned/aligned artifacts in `data/interim/`, and analysis-ready tables in `data/processed/`. Update `docs/data_sources.md` when source status changes; preserve acquisition and QC evidence.
