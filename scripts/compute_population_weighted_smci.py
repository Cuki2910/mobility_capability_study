"""
Compute population-weighted SMCI statistics and compare with unweighted means.

Uses grid_worldpop.csv (from aggregate_worldpop_by_grid.py) as population weights.
Does NOT change any formula — this is a post-hoc cross-check only.

Produces:
  outputs/validation/population_weighted_smci.md

Run:
  python scripts/compute_population_weighted_smci.py
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr


TYPOLOGIES = [
    "Integrated Capability",
    "Fragmented Capability",
    "Transit-Dependent",
    "Motorcycle Lock-in",
]


def compute_weighted_stats(
    metrics: pd.DataFrame,
    worldpop: pd.DataFrame,
) -> dict:
    df = metrics.merge(worldpop[["cell_id", "pop_sum"]], on="cell_id", how="left")
    df["pop_sum"] = df["pop_sum"].fillna(0.0)

    total_pop = df["pop_sum"].sum()
    if total_pop == 0:
        raise ValueError("Total population is zero — cannot compute population-weighted stats.")

    weights = df["pop_sum"] / total_pop

    def wmean(col: str) -> float:
        return float((df[col] * weights).sum())

    def wshare(mask: pd.Series) -> float:
        return float((mask.astype(float) * weights).sum())

    results = {
        # Unweighted
        "unweighted_mean_SMCI_B":    float(df["SMCI_B"].mean()),
        "unweighted_mean_SMCI_A":    float(df["SMCI_A"].mean()),
        "unweighted_mean_Delta_SMCI": float(df["Delta_SMCI"].mean()),
        "unweighted_share_improved": float((df["Delta_SMCI"] > 0).mean()),
        # Population-weighted
        "popweighted_mean_SMCI_B":    wmean("SMCI_B"),
        "popweighted_mean_SMCI_A":    wmean("SMCI_A"),
        "popweighted_mean_Delta_SMCI": wmean("Delta_SMCI"),
        "popweighted_share_improved":  wshare(df["Delta_SMCI"] > 0),
        # Bias
        "smci_b_bias_pct": 0.0,  # filled below
        # Population totals
        "total_pop": round(total_pop, 1),
        "cells_with_pop": int((df["pop_sum"] > 0).sum()),
        "zero_pop_cells": int((df["pop_sum"] == 0).sum()),
    }
    uw = results["unweighted_mean_SMCI_B"]
    pw = results["popweighted_mean_SMCI_B"]
    results["smci_b_bias_pct"] = round((pw - uw) / uw * 100, 2) if uw > 0 else 0.0

    # SMCI rank correlation: does population cluster in high or low SMCI cells?
    rho, p = spearmanr(df["pop_sum"], df["SMCI_B"])
    results["spearman_rho_pop_smci_b"] = round(float(rho), 4)
    results["spearman_p_value"] = float(p)

    # Typology population shares
    for t in TYPOLOGIES:
        results[f"pop_share_{t.replace(' ', '_')}"] = round(
            wshare(df["typology_B"] == t), 4
        )

    return results, df


def write_markdown(stats: dict, df: pd.DataFrame, output: Path) -> None:
    bias_direction = "higher" if stats["smci_b_bias_pct"] > 0 else "lower"
    rho = stats["spearman_rho_pop_smci_b"]
    rho_interp = ("positive" if rho > 0.1 else "negative" if rho < -0.1 else "near-zero")

    lines = [
        "# Population-Weighted SMCI Cross-Check",
        "",
        "Population weights from WorldPop 2020 (~92.77m raster, aggregated by 250m grid cell).",
        "This is a post-hoc cross-check only — no formula changes.",
        "",
        f"Total estimated population in study area: {stats['total_pop']:,.0f}",
        f"Cells with non-zero population: {stats['cells_with_pop']} / {stats['cells_with_pop'] + stats['zero_pop_cells']}",
        "",
        "## SMCI Mean Comparison",
        "",
        "| Metric | Unweighted | Population-weighted | Bias |",
        "|---|---|---|---|",
        f"| Mean SMCI_B | {stats['unweighted_mean_SMCI_B']:.4f} | {stats['popweighted_mean_SMCI_B']:.4f} | {stats['smci_b_bias_pct']:+.1f}% |",
        f"| Mean SMCI_A | {stats['unweighted_mean_SMCI_A']:.4f} | {stats['popweighted_mean_SMCI_A']:.4f} | — |",
        f"| Mean Delta SMCI | {stats['unweighted_mean_Delta_SMCI']:.4f} | {stats['popweighted_mean_Delta_SMCI']:.4f} | — |",
        f"| Share improved | {stats['unweighted_share_improved']:.2%} | {stats['popweighted_share_improved']:.2%} | — |",
        "",
        f"Population-weighted mean SMCI_B is {bias_direction} than the unweighted mean by "
        f"{abs(stats['smci_b_bias_pct']):.1f}%.",
        "",
        "## Population–SMCI Rank Correlation",
        "",
        f"Spearman ρ(population, SMCI_B) = {stats['spearman_rho_pop_smci_b']} "
        f"(p = {stats['spearman_p_value']:.3e})",
        "",
    ]

    if rho_interp == "positive":
        lines += [
            "Positive correlation: cells with higher population tend to have higher SMCI_B.",
            "The unweighted mean may understate the SMCI experienced by residents.",
        ]
    elif rho_interp == "negative":
        lines += [
            "Negative correlation: cells with higher population tend to have lower SMCI_B.",
            "The unweighted mean may overstate the SMCI experienced by residents.",
            "This is a concern: the most populated cells may be the least sustainably mobile.",
        ]
    else:
        lines += [
            "Near-zero correlation: population is roughly evenly distributed across SMCI levels.",
            "Unweighted and population-weighted means are similar.",
        ]

    lines += [
        "",
        "## Population Share by Typology (Scenario B)",
        "",
        "| Typology | Population share |",
        "|---|---:|",
    ]
    for t in TYPOLOGIES:
        key = f"pop_share_{t.replace(' ', '_')}"
        lines.append(f"| {t} | {stats[key]:.1%} |")

    lines += [
        "",
        "## Interpretation",
        "",
        "If population-weighted and unweighted SMCI means differ substantially (>10%),",
        "the Results section should report both to avoid misrepresenting the experience",
        "of the majority of residents. The typology population shares reveal whether",
        "the largest resident groups are in Integrated Capability or Motorcycle Lock-in cells.",
    ]

    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metrics",  type=Path, default=Path("data/processed/pilot_metrics.csv"))
    parser.add_argument("--worldpop", type=Path, default=Path("data/interim/grid_worldpop.csv"))
    parser.add_argument("--output",   type=Path, default=Path("outputs/validation/population_weighted_smci.md"))
    args = parser.parse_args()

    if not args.metrics.exists():
        raise FileNotFoundError(f"Missing {args.metrics}; run scripts/run_pilot_metrics.py first")
    if not args.worldpop.exists():
        raise FileNotFoundError(
            f"Missing {args.worldpop}; run scripts/aggregate_worldpop_by_grid.py first"
        )

    metrics  = pd.read_csv(args.metrics)
    worldpop = pd.read_csv(args.worldpop)

    stats, df = compute_weighted_stats(metrics, worldpop)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_markdown(stats, df, args.output)
    print(f"Wrote population-weighted SMCI summary to {args.output}")
    print(f"  Unweighted mean SMCI_B:      {stats['unweighted_mean_SMCI_B']:.4f}")
    print(f"  Pop-weighted mean SMCI_B:    {stats['popweighted_mean_SMCI_B']:.4f}")
    print(f"  Bias:                        {stats['smci_b_bias_pct']:+.1f}%")
    print(f"  Spearman rho(pop, SMCI_B):   {stats['spearman_rho_pop_smci_b']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
