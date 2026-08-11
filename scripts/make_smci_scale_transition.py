"""Report the legacy product-to-geometric SMCI scale transition."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from scipy.stats import spearmanr


def build_report(metrics: pd.DataFrame) -> pd.DataFrame:
    required = {"SMCI_A", "SMCI_B", "SMCI_product_A", "SMCI_product_B", "typology_A", "typology_B"}
    missing = sorted(required - set(metrics.columns))
    if missing:
        raise ValueError(f"Metrics missing scale-transition columns: {missing}")

    rows = []
    for scenario in ("A", "B"):
        geometric = metrics[f"SMCI_{scenario}"]
        product = metrics[f"SMCI_product_{scenario}"]
        rho, _ = spearmanr(product, geometric)
        rows.append({
            "scenario": scenario,
            "mean_product": float(product.mean()),
            "mean_geometric": float(geometric.mean()),
            "median_product": float(product.median()),
            "median_geometric": float(geometric.median()),
            "zero_cells_product": int((product == 0).sum()),
            "zero_cells_geometric": int((geometric == 0).sum()),
            "spearman_product_vs_geometric": float(rho),
            "typology_cells": int(len(metrics)),
        })
    return pd.DataFrame(rows)


def markdown_table(frame: pd.DataFrame) -> str:
    """Render a small report table without adding an optional dependency."""
    columns = list(frame.columns)
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in frame.itertuples(index=False, name=None):
        values = [f"{value:.6f}" if isinstance(value, float) else str(value) for value in row]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metrics", type=Path, default=Path("data/processed/pilot_metrics.csv"))
    parser.add_argument("--csv", type=Path, default=Path("outputs/validation/smci_scale_transition.csv"))
    parser.add_argument("--report", type=Path, default=Path("outputs/validation/smci_scale_transition.md"))
    args = parser.parse_args()

    transition = build_report(pd.read_csv(args.metrics))
    args.csv.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    transition.to_csv(args.csv, index=False)
    lines = [
        "# SMCI Scale Transition",
        "",
        "Canonical SMCI is the per-cell equal-weight geometric mean. Product SMCI is retained as a legacy audit scale, not a robustness alternative.",
        "",
        markdown_table(transition),
    ]
    args.report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {args.csv} and {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
