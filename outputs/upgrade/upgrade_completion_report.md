# Upgrade Completion Report

This is an evidence-led status report, not a claim that data-required work is complete.

| Recommendation | Status | Evidence | Remaining blocker |
|---|---|---|---|
| Geometric SMCI migration and legacy product audit | COMPLETED | Cell-level GM, shared-scale deltas, and product audit are regenerated. | - |
| Bruno CCS, NPT, coverage, inequality, and local-access robustness | COMPLETED_WITH_LIMITATION | All requested outputs are generated at 600/800/1000/1200 m. | K=5 uses a declared 20-minute missing-category penalty because only four observed POI categories exist. |
| Interactive map correctness, controls, layers, and browser smoke test | COMPLETED_WITH_LIMITATION | One embedded dataset, shared A/B bounds, selected-cell comparison, and responsive controls pass tests. | Map is an analytical interface, not external field validation. |
| Shifted-square and equal-area hexagon grid robustness | COMPLETED | All four alternate grids were recomputed and compared. | - |
| Sensitivity consolidation and scenario uncertainty envelope | COMPLETED | 22 cell-level GM specifications are included. | Envelope is not a confidence interval. |
| Data-quality grades | COMPLETED_WITH_LIMITATION | Provenance-based grade layer is generated. | Grades are an audit layer, not an SMCI component. |
| Reliability, generalized-cost, and mixed-traffic RAC contracts | CODE_COMPLETE_DATA_REQUIRED | Schemas refuse to run without required observed inputs. | Observed reliability, cost, and friction data are absent. |
| External validation contract | COMPLETED_WITH_LIMITATION | Ten manually audited Android motorcycle OD pairs are recomputed on the production Network D graph. | The 10-pair consumer-app check validates Network D travel times only; it is not overall external validation. |
| West Tay Mo comparison-site readiness | REJECTED_BY_METHOD_DECISION | Strict metrics, observed-opportunity audit, and reproducible CBD distances are generated. | Current Tay Mo core is 18.6% closer to Hoan Kiem than Ocean Park, exceeding the preregistered +/-15% gate. |
| Publication, paper tables/figures, and semantic consistency | COMPLETED | Current manuscript numbers and boundary/dasymetric reports were regenerated on the GM scale. | Historical decision-log values remain dated context only. |
| Final tests and integration gate | NOT_IMPLEMENTED_WITH_REASON | 161 tests, graph health, ownership, and document consistency pass. | Canonical outputs are intentionally locked on this feature branch; integration branch or authorized override is required. |
