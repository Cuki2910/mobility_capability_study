---
name: mobility-capability-study
description: 'Project-specific workflow for the GREEN-X mobility-capability-study repo: Vinhomes Ocean Park accessibility research, OSM/osmnx/geopandas/networkx pipelines, VinBus/Overpass/GTFS data checks, NAI/MAI/RAC/SMCI formulas, typology validation, proposal-method consistency, and paper outputs. Use when working in or discussing D:\GREEN-X\mobility-capability-study, the Fragmented Mobility Capability/Ocean Park study, VinBus route data, Hanoi motorcycle/transit accessibility, proposal_v6.docx, or the repo''s Python analysis code/tests/docs.'
---

# Mobility Capability Study

## First Moves

1. Read repo context before edits: `CLAUDE.md`, `docs/data_sources.md`, `docs/decisions.md`.
2. Treat `src/accessibility.py` as formula source of truth. If formulas change, update proposal Section 3 too.
3. Check current blocker before broad work: VinBus OSM route relations via Overpass.
4. Run `pytest tests/ -v` after code changes touching formulas, validation, network construction, or calibration.

## Project Guardrails

- Preserve exact terms: `NAI`, `MAI`, `RAC`, `MCS`, `SMCI`, Network `A/B/C/D`, Scenario `A/B`.
- Do not replace theory-first median-split typology with k-means; k-means is robustness only.
- Do not reintroduce geometric-mean SMCI robustness; it is vacuous. Use additive alternative.
- Expect MAI/RAC collinearity. Run `validation.collinearity_check` once real data exists; consider RAC_time-only contingency if VIF remains high.
- Do not use raw OSM driving speeds for motorcycle Network D. Implement literature-derived speed multipliers.
- Do not depend on Google TWO_WHEELER API for Vietnam bulk routing. Manual consumer-app spot checks only unless official coverage is verified.
- Keep single-site scope: Vinhomes Ocean Park only.

## Workflow Selection

- **Data acquisition / VinBus / OSM:** read `references/osm-vinbus-workflow.md`; use `scripts/vinbus_overpass_query.py` to generate/check the Overpass query.
- **Formula or analysis code:** read `references/methodology-cheatsheet.md`; update tests with the same conceptual invariant.
- **Proposal/paper edits:** read `references/methodology-cheatsheet.md`; ensure wording matches code and decision log.
- **New route/network/calibration code:** keep functions in `src/`, scripts thin in `scripts/`, notebooks exploratory only.

## Useful Commands

```powershell
pip install -r requirements.txt
pytest tests/ -v
python .codex\skills\mobility-capability-study\scripts\vinbus_overpass_query.py --bbox 20.85 105.75 21.15 106.05
```

## Output Discipline

When finishing work, report: files changed, tests run, remaining data blockers. If a data claim is current or external, verify it with live sources before relying on it.
