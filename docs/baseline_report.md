# Baseline Report

Last updated: 2026-06-21.

## Phase 0 Results

- Test baseline: `pytest tests/ -v` passed, 5/5 before implementation.
- Repo status: no `.git` directory detected at `D:\GREEN-X\mobility-capability-study`, so file-level git diff/status is unavailable in this workspace.
- Dependencies: `requirements.txt` includes osmnx, networkx, geopandas, shapely, pandas, numpy, scipy, scikit-learn, statsmodels, pytest.
- Existing source state before this pass: formulas implemented in `src/accessibility.py`; `src/networks.py` and `src/validation.py` were mostly stubs.

## Data Already Present

- `proposal/proposal_v6.docx`: current proposal.
- `docs/data_sources.md`: data-source status log.
- `docs/decisions.md`: methodology decision log.
- `tests/test_accessibility.py`: formula regression tests.

## Data Not Yet Present

- OSM pilot networks verified in `data/raw/`: walk graph has 6,846 nodes / 20,024 edges; drive graph has 1,401 nodes / 3,408 edges.
- Pilot POIs and grid verified in `data/interim/`: 106 POIs and 462 grid cells.
- VinBus route tags verified in `data/raw/vinbus_overpass_relations.json` from Overpass on 2026-06-21: 39 relations found.
- VinBus route geometry verified in `data/raw/vinbus_overpass_relations_geom.json`: 10 Ocean Park-facing relations with member geometry.
- Accessibility-ready pilot input table exists at `data/interim/pilot_accessibility_inputs.csv` with 462 rows, rebuilt in `network` mode using graph shortest paths plus VinBus corridor proxy.
- Processed pilot metrics exist at `data/processed/pilot_metrics.csv`; supervisor memo exists at `outputs/supervisor_memo.md`.
- POI audit exists at `outputs/poi_audit.md`; category counts are healthcare 10, park 42, retail 35, school 19, duplicate rows 0.

## Current Blockers

1. Network-v1 still uses transit corridor/stop proxies; replace with full stop/timetable metrics after GTFS validates.
2. TUMI GTFS candidate download timed out locally; Network B remains baseline-limited until `data/raw/hanoi_gtfs.zip` exists.
3. WorldPop raster is downloaded and resolution-verified from metadata (~92.77m), but integration into MAI magnitude weighting is not implemented yet.
4. POI audit is automated and spot-check CSV is ready with map links; complete at least 20 manual spot-check records.
