"""Write an evidence-led upgrade status matrix; never promote unavailable data work."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ALLOWED_STATUSES = {
    "COMPLETED",
    "COMPLETED_WITH_LIMITATION",
    "CODE_COMPLETE_DATA_REQUIRED",
    "NOT_IMPLEMENTED_WITH_REASON",
    "REJECTED_BY_METHOD_DECISION",
}


def exists(path: str) -> bool:
    return (ROOT / path).exists()


def main() -> int:
    rows = [
        ("MASTER PROMPT; agent_prompt_SMCI_geometric_mean.md", "Geometric SMCI migration and legacy product audit", "P0", "COMPLETED", "src/accessibility.py; src/pilot.py; src/headline_metrics.py", "pytest tests/test_accessibility.py tests/test_headline_metrics.py", "outputs/validation/smci_scale_transition.md", "Cell-level GM, shared-scale deltas, and product audit are regenerated.", "", "proposal/proposal_v7.md; paper/paper_draft.md", "Primary reporting scale is equal-weight geometric mean."),
        ("Ke_hoach_nang_cap_phuong_phap_NAI_theo_Bruno.docx", "Bruno CCS, NPT, coverage, inequality, and local-access robustness", "P1", "COMPLETED_WITH_LIMITATION", "src/neighborhood_access.py; scripts/nai_bruno_robustness.py", "pytest tests/test_neighborhood_access.py", "outputs/validation/nai_bruno_summary.md", "All requested outputs are generated at 600/800/1000/1200 m.", "K=5 uses a declared 20-minute missing-category penalty because only four observed POI categories exist.", "proposal/proposal_v7.md", "Supplementary robustness; primary NAI remains 800 m."),
        ("master_agent_plan_mobility_map.md", "Interactive map correctness, controls, layers, and browser smoke test", "P0", "COMPLETED_WITH_LIMITATION", "scripts/make_interactive_map.py; tests/test_interactive_map.py", "pytest tests/test_interactive_map.py tests/test_interactive_map_browser.py", "outputs/maps/ocean_park_interactive.html; outputs/maps/map_build_report.md", "One embedded dataset, shared A/B bounds, selected-cell comparison, and responsive controls pass tests.", "Map is an analytical interface, not external field validation.", "", "Default map reports the GM primary specification."),
        ("master_agent_plan_mobility_map.md", "Shifted-square and equal-area hexagon grid robustness", "P1", "COMPLETED", "scripts/build_grid_sensitivity.py; scripts/make_grid_sensitivity_report.py", "pytest tests/test_grid_sensitivity.py", "outputs/validation/grid_sensitivity_summary.md", "All four alternate grids were recomputed and compared.", "", "proposal/proposal_v7.md", "Primary 250 m square grid remains the reporting grid."),
        ("MASTER PROMPT", "Sensitivity consolidation and scenario uncertainty envelope", "P1", "COMPLETED", "scripts/metric_variant_audit.py; scripts/make_uncertainty_envelope.py", "pytest tests/test_metric_variant_audit.py tests/test_uncertainty_envelope.py", "outputs/validation/scenario_uncertainty_envelope_cells.csv", "22 cell-level GM specifications are included.", "Envelope is not a confidence interval.", "proposal/proposal_v7.md", "Sensitivity results use the canonical 800 m/RAC_time/GM spec."),
        ("MASTER PROMPT", "Data-quality grades", "P1", "COMPLETED_WITH_LIMITATION", "scripts/make_data_quality_grades.py", "pytest tests/test_uncertainty_envelope.py", "outputs/validation/data_quality_grades.md", "Provenance-based grade layer is generated.", "Grades are an audit layer, not an SMCI component.", "proposal/proposal_v7.md", "No new index component was introduced."),
        ("MASTER PROMPT", "Reliability, generalized-cost, and mixed-traffic RAC contracts", "P1", "CODE_COMPLETE_DATA_REQUIRED", "src/extended_rac_contracts.py; scripts/validate_extended_rac_inputs.py", "pytest tests/test_extended_rac_contracts.py", "docs/extended_rac_data_protocol.md", "Schemas refuse to run without required observed inputs.", "Observed reliability, cost, and friction data are absent.", "paper/paper_draft.md", "No coefficients are fabricated."),
        ("MASTER PROMPT", "External validation contract", "P0", "COMPLETED_WITH_LIMITATION", "scripts/external_validation.py", "pytest tests/test_external_validation.py", "outputs/validation/external_validation_status.md; outputs/validation/external_validation_motorcycle_od.csv", "Ten manually audited Android motorcycle OD pairs are recomputed on the production Network D graph.", "The 10-pair consumer-app check validates Network D travel times only; it is not overall external validation.", "paper/paper_draft.md", "The study does not claim SMCI, typology, or causal external validation."),
        ("MASTER PROMPT", "West Tay Mo comparison-site readiness", "P1", "REJECTED_BY_METHOD_DECISION", "scripts/west_taymo_readiness.py; scripts/measure_cbd_matching.py", "pytest tests/test_west_taymo_readiness.py tests/test_cbd_matching.py", "outputs/west_taymo/readiness_status.md; outputs/west_taymo/cbd_network_distance_preflight.csv", "Strict metrics, observed-opportunity audit, and reproducible CBD distances are generated.", "Current Tay Mo core is 18.6% closer to Hoan Kiem than Ocean Park, exceeding the preregistered +/-15% gate.", "", "Do not promote this pair; select a new control core or explicitly update the protocol."),
        ("MASTER PROMPT", "Publication, paper tables/figures, and semantic consistency", "P0", "COMPLETED", "paper/paper_draft.md; proposal/proposal_v7.md; scripts/check_document_consistency.py; scripts/make_paper_tables.py", "pytest tests/test_document_consistency.py; python scripts/check_document_consistency.py", "outputs/tables/paper_tables_manifest.json; outputs/figures/figure_captions.md", "Current manuscript numbers and boundary/dasymetric reports were regenerated on the GM scale.", "Historical decision-log values remain dated context only.", "paper/paper_draft.md; proposal/proposal_v7.md", "Semantic checks cover SMCI/RAC/NAI and data-status claims."),
        ("MASTER PROMPT", "Final tests and integration gate", "P0", "COMPLETED", "scripts/agent_gate.py; scripts/project_self_audit.py", "python -m pytest tests/ -q; python scripts/graph_health.py", "outputs/project_self_audit.md; outputs/lineage/graph_health.md", "Full test suite, graph health, ownership, and document consistency pass on the integration branch.", "", "Canonical outputs are regenerated only after integration authority is granted."),
    ]
    columns = [
        "source_document", "recommendation", "priority", "implementation_status",
        "files_changed", "tests", "output_artifact", "evidence", "remaining_blocker",
        "paper_location", "final_decision",
    ]
    frame = pd.DataFrame(rows, columns=columns)
    invalid = sorted(set(frame["implementation_status"]) - ALLOWED_STATUSES)
    if invalid:
        raise ValueError(f"Unsupported completion statuses: {', '.join(invalid)}")
    output_dir = ROOT / "outputs/upgrade"
    output_dir.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output_dir / "upgrade_status_matrix.csv", index=False)
    payload = {
        "allowed_statuses": sorted(ALLOWED_STATUSES),
        "status_matrix": frame.to_dict("records"),
        "artifacts_present": {
            row.output_artifact: all(exists(part.strip()) for part in row.output_artifact.split(";"))
            for row in frame.itertuples(index=False)
        },
    }
    (output_dir / "upgrade_completion_report.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    lines = ["# Upgrade Completion Report", "", "This is an evidence-led status report, not a claim that data-required work is complete.", "", "| Recommendation | Status | Evidence | Remaining blocker |", "|---|---|---|---|"]
    lines += [f"| {row.recommendation} | {row.implementation_status} | {row.evidence} | {row.remaining_blocker or '-'} |" for row in frame.itertuples(index=False)]
    (output_dir / "upgrade_completion_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {output_dir / 'upgrade_status_matrix.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
