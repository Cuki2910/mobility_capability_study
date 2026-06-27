"""Evaluate whether Overture-only POIs can be promoted into the primary layer."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

VALID_STATUSES = {
    "unchecked",
    "confirmed",
    "duplicate",
    "misclassified",
    "missing_unverified",
    "out_of_scope",
}
FAIL_STATUSES = {"duplicate", "misclassified", "missing_unverified", "out_of_scope"}


def status_column(df: pd.DataFrame) -> str:
    if "spot_check_status" in df.columns:
        return "spot_check_status"
    if "status" in df.columns:
        return "status"
    raise ValueError("Spot-check CSV must include 'spot_check_status' or 'status'")


def evaluate_gate(df: pd.DataFrame, confirm_threshold: float = 0.70) -> dict:
    status_col = status_column(df)
    statuses = df[status_col].fillna("unchecked").astype(str).str.strip().str.lower().replace("", "unchecked")
    unknown = sorted(set(statuses) - VALID_STATUSES)
    if unknown:
        raise ValueError(f"Unknown spot-check statuses: {unknown}")

    total = int(len(df))
    confirmed = int((statuses == "confirmed").sum())
    required = int((total * confirm_threshold) + 0.999999)
    unchecked = int((statuses == "unchecked").sum())
    failed = statuses.isin(FAIL_STATUSES)
    fail_count = int(failed.sum())

    severe_bias = False
    bias_category = None
    bias_share = 0.0
    if fail_count >= 5 and "category" in df.columns:
        fail_categories = df.loc[failed, "category"].fillna("unknown").astype(str).str.strip().replace("", "unknown")
        counts = fail_categories.value_counts()
        if not counts.empty:
            bias_category = str(counts.index[0])
            bias_share = float(counts.iloc[0] / fail_count)
            severe_bias = bias_share > 0.50

    passed = confirmed >= required and not severe_bias and unchecked == 0
    verdict = "PASS" if passed else ("INCOMPLETE" if unchecked else "FAIL")
    return {
        "total": total,
        "confirmed": confirmed,
        "required": required,
        "confirmed_share": confirmed / total if total else 0.0,
        "unchecked": unchecked,
        "fail_count": fail_count,
        "status_counts": statuses.value_counts().sort_index().to_dict(),
        "severe_category_bias": severe_bias,
        "bias_category": bias_category,
        "bias_share": bias_share,
        "verdict": verdict,
    }


def render_markdown(result: dict, input_path: Path) -> str:
    status_lines = [f"| {status} | {count} |" for status, count in result["status_counts"].items()]
    bias = "no"
    if result["severe_category_bias"]:
        bias = f"yes: {result['bias_category']} ({result['bias_share']:.1%} of failed rows)"
    if result["verdict"] == "PASS":
        recommendation = "Promote `data/interim/merged_pois.gpkg` to primary POI input and rerun primary metrics."
    elif result["verdict"] == "INCOMPLETE":
        recommendation = "Keep OSM-only primary until every Overture-only POI has a human-verified status."
    else:
        recommendation = "Keep OSM-only primary; report merged POIs as sensitivity only."
    return "\n".join([
        "# Overture POI Gate Result",
        "",
        f"Input: `{input_path}`",
        "",
        f"Verdict: **{result['verdict']}**",
        "",
        "## Gate Criteria",
        "",
        f"- Confirmed threshold: {result['required']}/{result['total']} (70%)",
        f"- Confirmed: {result['confirmed']}/{result['total']} ({result['confirmed_share']:.1%})",
        f"- Unchecked: {result['unchecked']}",
        f"- Severe failed-category bias: {bias}",
        "",
        "## Status Counts",
        "",
        "| Status | Count |",
        "|---|---:|",
        *status_lines,
        "",
        "## Recommendation",
        "",
        recommendation,
        "",
    ])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spot-check", type=Path, default=Path("data/interim/overture_only_spot_check.csv"))
    parser.add_argument("--output", type=Path, default=Path("outputs/validation/overture_gate_result.md"))
    args = parser.parse_args()

    df = pd.read_csv(args.spot_check)
    result = evaluate_gate(df)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_markdown(result, args.spot_check), encoding="utf-8")
    print(f"{result['verdict']}: wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
