# Supervisor Review Package

Last updated: 2026-06-21.

## Purpose

Package the project once Phase 4/5 real pilot outputs exist. Do not present synthetic outputs as pilot findings.

## Required Inputs

- `proposal/proposal_v6.docx`
- `docs/baseline_report.md`
- `docs/data_sources.md`
- `data/processed/pilot_metrics.csv`
- `outputs/pilot_summary.csv`
- `outputs/validation/correlation_matrix.csv`
- `outputs/validation/vif_flags.csv`
- `outputs/validation/robustness_summary.csv`
- `outputs/validation/manual_motorcycle_validation_template.csv`
- `outputs/project_self_audit.md`

## One-Page Memo Structure

1. Research question: whether local walkability translates into integrated sustainable mobility capability when RAC remains low.
2. Data status: VinBus/GTFS/OSM/GHSL decisions, with unresolved blockers named plainly.
3. Pilot result: mean SMCI A/B, mean Delta_SMCI, share improved, typology shifts.
4. Validation: VIF result, RAC_time-only contingency if triggered, additive robustness comparison.
5. Next work: route digitization or full study-area scaling, depending on Phase 1 outcome.

## Commands To Regenerate Tables

```powershell
pytest tests/ -v
python scripts/run_pilot_metrics.py
python scripts/make_validation_report.py
python scripts/make_supervisor_memo.py
python scripts/prepare_manual_checks.py
python scripts/project_self_audit.py
```
