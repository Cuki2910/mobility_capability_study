# Fragmented Mobility Capability - Ocean Park Study

Research proposal and analysis pipeline examining whether Vinhomes Ocean Park
(Hanoi) achieves a walkable local environment while remaining dependent on
motorcycles at the metropolitan scale, using a dual-scale, mode-competitive
accessibility framework.

- Proposal: `proposal/proposal_v6.docx`
- Working context: read `CLAUDE.md` first
- Data status: `docs/data_sources.md`
- Methodology decisions: `docs/decisions.md`

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v
```

## Current Next Step

VinBus OSM relations, Ocean Park-facing geometry, OSM graphs, POIs, grid,
network-v1 accessibility inputs, pilot metrics, validation tables, and the
supervisor memo are generated. Current blockers: TUMI GTFS download timed out
locally, WorldPop raster is downloaded/resolution-verified, and POIs need
manual spot-check records.

## Phase Commands

```bash
pytest tests/ -v
python scripts/check_vinbus_overpass.py --bbox 20.85 105.75 21.15 106.05
python scripts/check_vinbus_overpass.py --bbox 20.85 105.75 21.15 106.05 --refs E01,E02,E03,E10,OCP1,OCP2 --split-refs --geom --output data/raw/vinbus_overpass_relations_geom.json --summary-csv data/interim/vinbus_route_summary.csv
python scripts/fetch_osm_data.py
python scripts/fetch_hanoi_gtfs.py
python scripts/check_hanoi_gtfs.py
python scripts/audit_pois.py
python scripts/prepare_manual_checks.py
python scripts/build_accessibility_inputs.py --mode network --gtfs-status baseline_limited
python scripts/run_pilot_metrics.py
python scripts/make_validation_report.py
python scripts/make_supervisor_memo.py
python scripts/project_self_audit.py
```
