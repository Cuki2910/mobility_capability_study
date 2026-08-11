"""Audit West Tay Mo comparison readiness without promoting proxy inputs."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def unresolved_observed_opportunities(audit: pd.DataFrame) -> int | None:
    """Support both the legacy counter and the current row-level observed audit schema."""
    if "needs_source" in audit:
        return int(pd.to_numeric(audit["needs_source"], errors="coerce").fillna(1).sum())
    if "obs_audit_status" in audit:
        return int(audit["obs_audit_status"].fillna("needs_source").eq("needs_source").sum())
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metrics", type=Path, default=Path("data/processed/west_taymo_metrics.csv"))
    parser.add_argument("--observed-audit", type=Path, default=Path("outputs/west_taymo/observed_opportunity_gap_audit.csv"))
    parser.add_argument("--preflight", type=Path, default=Path("outputs/west_taymo/matching_preflight.md"))
    parser.add_argument("--output", type=Path, default=Path("outputs/west_taymo/readiness_status.md"))
    args = parser.parse_args()
    blockers = []
    if not args.metrics.exists():
        blockers.append("missing metrics")
    if not args.observed_audit.exists():
        blockers.append("missing observed-opportunity audit")
    else:
        audit = pd.read_csv(args.observed_audit)
        unresolved = unresolved_observed_opportunities(audit)
        if unresolved is None:
            blockers.append("observed-opportunity audit lacks needs_source or obs_audit_status")
        elif unresolved > 0:
            blockers.append("observed opportunity sources remain unresolved")
    preflight_text = args.preflight.read_text(encoding="utf-8").lower() if args.preflight.exists() else ""
    if not args.preflight.exists() or "unresolved" in preflight_text:
        blockers.append("matching preflight has unresolved measurements")
    if "matching gate failed" in preflight_text:
        blockers.append("current Tay Mo core fails the preregistered CBD-distance matching gate")
    if not blockers:
        status = "READY_FOR_SHARED_SCALE_COMPARISON"
    elif "matching gate failed" in preflight_text:
        status = "MATCHING_GATE_FAILED"
    else:
        status = "CODE_COMPLETE_DATA_REQUIRED"
    block_lines = [f"- {blocker}" for blocker in blockers] or ["- none"]
    lines = [
        "# West Tay Mo Comparison Readiness",
        "",
        f"Status: `{status}`",
        "",
        "The comparison must use common metric definitions and pooled/shared normalization. It is descriptive (n=2), not causal.",
        "",
        "## Blocking checks",
        "",
        *block_lines,
        "",
        "Observed-strict site metrics are available only as setup results; they cannot be promoted to a cross-site result until matching gates pass.",
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
