# Fragmented Mobility Capability - Ocean Park Study

> Current reporting scale: equal-weight geometric-mean SMCI (cell level). The canonical Ocean Park primary result is mean SMCI_A=0.1470, SMCI_B=0.1711, Delta_SMCI=+0.0242; legacy product values are retained only for scale-transition auditing.

Research proposal and analysis pipeline examining whether Vinhomes Ocean Park
(Hanoi) achieves a walkable local environment while remaining dependent on
motorcycles at the metropolitan scale, using a dual-scale, mode-competitive
accessibility framework.

- Proposal: `proposal/proposal_v7.md`
- Working context: read `CLAUDE.md` first
- Data status: `docs/data_sources.md`
- Methodology decisions: `docs/decisions.md`
- Proposed future work: `docs/roadmap.md` (not adopted methodology)

## Workspace

| Directory | Contents |
| --- | --- |
| `src/`, `scripts/`, `tests/` | Reusable analysis, executable commands, tests |
| `config/` | Pipeline and analysis configuration |
| `data/raw/`, `data/interim/`, `data/processed/` | Source, cleaned, and analysis-ready data |
| `outputs/` | Generated reports, maps, validation, and run provenance |
| `proposal/`, `paper/` | Single final proposal (`proposal_v7.md`) and manuscript |
| `docs/` | Data status, decisions, methods, and agent workflow |
| `references/` | Supporting reference documents |

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v
```

## Standard Pipeline

```bash
python scripts/run_research_pipeline.py --dry-run
python scripts/run_research_pipeline.py
```

The versioned DAG lives in `config/pipeline.json`. Each real run writes an atomic
JSON manifest under `outputs/lineage/runs/`; the disposable SQLite lineage index
is rebuilt at `outputs/lineage/research_lineage.sqlite`. Use `--node`, `--from`,
`--to`, or `--force` for targeted reruns.

## Agent Workflow

Use a separate Git worktree per agent, reserve file ownership, then run the
policy-driven gate before independent review and human merge:

```powershell
git worktree add ..\mcs-task -b agent/task development
Copy-Item .agent/ownership.example.json .agent/ownership.json
python scripts/check_agent_ownership.py
python scripts/agent_gate.py --dry-run
python scripts/agent_gate.py
```

See `docs/agent_workflow.md` for ownership setup, gate policy, review checks,
change reports, user confirmation, and integration recovery.

## Current Next Step

VinBus OSM relations, Ocean Park-facing stop geometry, OSM graphs, POIs, grid,
stop-routing network-v1 accessibility inputs, pilot metrics, validation tables,
maps, and the supervisor memo are generated. Overture-only POIs are confirmed and
the merged OSM+Overture POI layer is now primary.

## Phase Commands

Local data were recovered on 2026-10-10; see [source provenance and recovery limits](docs/data_recovery.md). The recovered Overture supplement is unchecked; historical promotion above does not apply to the new layers. Review the recovery report before rebuilding outputs.

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
python scripts/evaluate_overture_gate.py
python scripts/vinbus_routing_comparison.py
python scripts/make_supervisor_memo.py
python scripts/project_self_audit.py
```
