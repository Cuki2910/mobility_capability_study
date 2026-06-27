"""Run threshold and quantile robustness checks for theory-first typology."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

TYPOLOGIES = [
    "Integrated Capability",
    "Fragmented Capability",
    "Transit-Dependent",
    "Motorcycle Lock-in",
]


def labels_from_thresholds(nai: pd.Series, mcs: pd.Series, nai_threshold: float, mcs_threshold: float) -> np.ndarray:
    nai_hi = nai.to_numpy(dtype=float) >= nai_threshold
    mcs_hi = mcs.to_numpy(dtype=float) >= mcs_threshold
    labels = np.empty(len(nai), dtype=object)
    labels[nai_hi & mcs_hi] = "Integrated Capability"
    labels[nai_hi & ~mcs_hi] = "Fragmented Capability"
    labels[~nai_hi & mcs_hi] = "Transit-Dependent"
    labels[~nai_hi & ~mcs_hi] = "Motorcycle Lock-in"
    return labels


def summarize_variant(metrics: pd.DataFrame, name: str, labels: np.ndarray) -> dict:
    from sklearn.metrics import cohen_kappa_score

    primary = metrics["typology_B"].to_numpy(dtype=object)
    counts = pd.Series(labels).value_counts().reindex(TYPOLOGIES, fill_value=0)
    return {
        "variant": name,
        "kappa_vs_primary": float(cohen_kappa_score(primary, labels)),
        "relabelled_cells": int((primary != labels).sum()),
        "relabelled_share": float((primary != labels).mean()),
        **{f"count_{t}": int(counts[t]) for t in TYPOLOGIES},
    }


def run_robustness(metrics: pd.DataFrame) -> pd.DataFrame:
    rows = []
    rows.append(summarize_variant(
        metrics,
        "absolute_norm_0.50",
        labels_from_thresholds(metrics["NAI_norm"], metrics["MCS_B"], 0.50, 0.50),
    ))
    for q in [0.40, 0.45, 0.55, 0.60]:
        rows.append(summarize_variant(
            metrics,
            f"quantile_{q:.2f}",
            labels_from_thresholds(metrics["NAI"], metrics["MCS_B"], metrics["NAI"].quantile(q), metrics["MCS_B"].quantile(q)),
        ))
    return pd.DataFrame(rows)


def render_markdown(summary: pd.DataFrame) -> str:
    lines = [
        "# Typology Robustness",
        "",
        "Purpose: test whether the four-cell typology is only an artefact of the rank-based median split.",
        "",
        "## Variants",
        "",
        "- `absolute_norm_0.50`: high NAI and high MCS require normalized scores >= 0.50.",
        "- `quantile_*`: high/low thresholds are moved away from the median to 40%, 45%, 55%, and 60% cut points.",
        "",
        "## Agreement With Primary Typology",
        "",
        "| Variant | Kappa | Relabelled | Integrated | Fragmented | Transit-Dependent | Motorcycle Lock-in |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"| {row['variant']} | {row['kappa_vs_primary']:.3f} | "
            f"{int(row['relabelled_cells'])} ({row['relabelled_share']:.1%}) | "
            f"{int(row['count_Integrated Capability'])} | "
            f"{int(row['count_Fragmented Capability'])} | "
            f"{int(row['count_Transit-Dependent'])} | "
            f"{int(row['count_Motorcycle Lock-in'])} |"
        )
    min_kappa = float(summary["kappa_vs_primary"].min())
    max_shift = int(summary["relabelled_cells"].max())
    lines.extend([
        "",
        "## Interpretation",
        "",
        f"Across variants, minimum kappa is {min_kappa:.3f}; maximum relabelled cells is {max_shift}/462.",
        "The exact 169/169/62/62 primary balance is therefore a property of the median split, but the broad spatial ordering can be checked against non-median and absolute thresholds.",
        "Report this table with the primary typology to pre-empt the by-construction critique.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metrics", type=Path, default=Path("data/processed/pilot_metrics.csv"))
    parser.add_argument("--output-csv", type=Path, default=Path("outputs/validation/typology_robustness.csv"))
    parser.add_argument("--output-md", type=Path, default=Path("outputs/validation/typology_robustness.md"))
    args = parser.parse_args()

    metrics = pd.read_csv(args.metrics)
    summary = run_robustness(metrics)
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.output_csv, index=False)
    args.output_md.write_text(render_markdown(summary), encoding="utf-8")
    print(f"Wrote {args.output_csv} and {args.output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
