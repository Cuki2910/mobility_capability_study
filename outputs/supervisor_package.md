# Supervisor Review Package

Generated: 2026-06-23.

## Read First

1. `proposal/proposal_v7.md` - current proposal and method narrative.
2. `outputs/supervisor_memo.md` - compact status memo for review.
3. `outputs/project_self_audit.md` - automated audit of strengths, caveats, and next actions.

## Core Pilot Results

- `outputs/pilot_summary.csv` - primary merged-POI pilot summary.
- `data/processed/pilot_metrics.csv` - primary cell-level metrics.
- `outputs/validation/distribution_diagnostics.md` - zero inflation and delta-group diagnostics.
- `outputs/maps/` - quick-look SVG maps and GIS layers.
- `outputs/figures/` - paper-facing composite SVG figures and captions.

## Validation And Sensitivity

- `outputs/validation/population_weighted_smci.md` - WorldPop population-weighted SMCI.
- `outputs/validation/built_population_zero_access.md` - building/WorldPop zero-access audit.
- `outputs/validation/overture_gate_result.md` - Overture POI gate audit.
- `outputs/validation/typology_robustness.md` - threshold/quantile typology robustness.
- `outputs/validation/rac_time_only_summary.md` - RAC_time-only VIF contingency.
- `outputs/validation/rac_scaling_summary.md` - RAC normalization sensitivity.
- `outputs/headway_sensitivity_summary.csv` - VinBus headway sensitivity.
- `outputs/validation/gtfs_catalog_check.md` - MobilityDatabase/TUMI GTFS catalog check.

## Decision Requests

- Whether the typology robustness table is sufficient to answer the by-construction critique.
- Which paper-facing figures should be included in the manuscript main text versus appendix.
- Whether MAI should remain proxy-level or receive a separate building/WorldPop weighting upgrade.
- Whether TUMI Hanoi GTFS feeds should be processed as a current-service/time-of-day sensitivity.
