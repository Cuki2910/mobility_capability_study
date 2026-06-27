"""Diagnose pilot metric distributions beyond headline means."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr


METRIC_COLS = [
    "NAI",
    "MAI_A",
    "MAI_B",
    "RAC_A",
    "RAC_B",
    "MCS_B",
    "SMCI_A",
    "SMCI_B",
    "SMCI_additive_B",
    "Delta_SMCI",
]


def norm01(values: pd.Series) -> np.ndarray:
    arr = values.astype(float).to_numpy()
    lo = float(np.nanmin(arr))
    hi = float(np.nanmax(arr))
    if hi == lo:
        return np.zeros_like(arr, dtype=float)
    return (arr - lo) / (hi - lo)


def describe_metrics(metrics: pd.DataFrame) -> pd.DataFrame:
    percentiles = [0.0, 0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]
    return metrics[METRIC_COLS].describe(percentiles=percentiles).T


def zero_shares(metrics: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in METRIC_COLS:
        s = metrics[col].astype(float)
        rows.append(
            {
                "metric": col,
                "share_zero": float((s == 0).mean()),
                "share_near_zero_1e_6": float((s <= 1e-6).mean()),
            }
        )
    return pd.DataFrame(rows)


def delta_groups(metrics: pd.DataFrame, eps: float = 1e-12) -> pd.DataFrame:
    delta = metrics["Delta_SMCI"].astype(float)
    groups = {
        "improved": delta > eps,
        "unchanged": delta.abs() <= eps,
        "declined": delta < -eps,
    }
    return pd.DataFrame(
        [
            {"group": name, "count": int(mask.sum()), "share": float(mask.mean())}
            for name, mask in groups.items()
        ]
    )


def normalized_component_summary(metrics: pd.DataFrame) -> pd.DataFrame:
    rows = []
    norm_cols = {
        "NAI": "NAI_norm",
        "MAI_A": "MAI_A_norm",
        "MAI_B": "MAI_B_norm",
        "RAC_A": "RAC_A_norm",
        "RAC_B": "RAC_B_norm",
    }
    for col in ["NAI", "MAI_A", "MAI_B", "RAC_A", "RAC_B"]:
        raw = metrics[col].astype(float)
        z = metrics[norm_cols[col]].astype(float).to_numpy() if norm_cols[col] in metrics else norm01(raw)
        p99 = float(raw.quantile(0.99))
        rows.append(
            {
                "metric": col,
                "mean_norm": float(np.mean(z)),
                "median_norm": float(np.median(z)),
                "p90_norm": float(np.quantile(z, 0.90)),
                "max_raw": float(raw.max()),
                "p99_raw": p99,
                "max_to_p99": float(raw.max() / p99) if p99 else np.inf,
            }
        )
    return pd.DataFrame(rows)


def typology_sanity(metrics: pd.DataFrame) -> pd.DataFrame:
    n = len(metrics)
    nai_rank = np.argsort(np.argsort(metrics["NAI"].to_numpy(), kind="stable"), kind="stable")
    mcs_rank = np.argsort(np.argsort(metrics["MCS_B"].to_numpy(), kind="stable"), kind="stable")
    nai_hi = nai_rank >= n // 2
    mcs_hi = mcs_rank >= n // 2
    rows = [
        {"check": "NAI high", "count": int(nai_hi.sum())},
        {"check": "NAI low", "count": int((~nai_hi).sum())},
        {"check": "MCS high", "count": int(mcs_hi.sum())},
        {"check": "MCS low", "count": int((~mcs_hi).sum())},
        {"check": "high NAI / high MCS", "count": int((nai_hi & mcs_hi).sum())},
        {"check": "high NAI / low MCS", "count": int((nai_hi & ~mcs_hi).sum())},
        {"check": "low NAI / high MCS", "count": int((~nai_hi & mcs_hi).sum())},
        {"check": "low NAI / low MCS", "count": int((~nai_hi & ~mcs_hi).sum())},
    ]
    return pd.DataFrame(rows)


def correlation_summary(metrics: pd.DataFrame) -> pd.DataFrame:
    pairs = [
        ("NAI", "MCS_B"),
        ("NAI", "MAI_B"),
        ("NAI", "RAC_B"),
        ("MAI_B", "RAC_B"),
        ("SMCI_B", "SMCI_additive_B"),
    ]
    rows = []
    for left, right in pairs:
        rows.append(
            {
                "left": left,
                "right": right,
                "pearson_r": float(pearsonr(metrics[left], metrics[right]).statistic),
                "spearman_rho": float(spearmanr(metrics[left], metrics[right]).statistic),
            }
        )
    return pd.DataFrame(rows)


def write_markdown(metrics: pd.DataFrame, output: Path) -> None:
    z = normalized_component_summary(metrics).set_index("metric")
    zeros = zero_shares(metrics).set_index("metric")
    groups = delta_groups(metrics).set_index("group")
    corr = correlation_summary(metrics)
    typology = typology_sanity(metrics).set_index("check")
    nai_norm = metrics["NAI_norm"].to_numpy() if "NAI_norm" in metrics else norm01(metrics["NAI"])
    mai_b_norm = metrics["MAI_B_norm"].to_numpy() if "MAI_B_norm" in metrics else norm01(metrics["MAI_B"])
    rac_b_norm = metrics["RAC_B_norm"].to_numpy() if "RAC_B_norm" in metrics else norm01(metrics["RAC_B"])
    naive_b = float(nai_norm.mean() * mai_b_norm.mean() * rac_b_norm.mean())

    lines = [
        "# Pilot Distribution Diagnostics",
        "",
        "## Why Mean SMCI Is Small",
        "",
        f"- Mean normalized NAI: {z.loc['NAI', 'mean_norm']:.4f}.",
        f"- Mean normalized MAI_B: {z.loc['MAI_B', 'mean_norm']:.4f}.",
        f"- Mean normalized RAC_B: {z.loc['RAC_B', 'mean_norm']:.4f}.",
        f"- Product of those means: {naive_b:.4f}.",
        f"- Actual mean SMCI_B: {metrics['SMCI_B'].mean():.4f}.",
        "",
        f"The low mean is mainly driven by RAC compression and zero inflation, not by NAI alone. RAC_B has a normalized mean of about {z.loc['RAC_B', 'mean_norm']:.4f} because one extreme cell reaches 1.0 while the 99th percentile is only about {z.loc['RAC_B', 'p99_raw']:.4f}. SMCI_B also equals zero for cells where any component is zero.",
        "",
        "## Zero Inflation",
        "",
        f"- NAI zero share: {zeros.loc['NAI', 'share_zero']:.2%}.",
        f"- MAI_B zero share: {zeros.loc['MAI_B', 'share_zero']:.2%}.",
        f"- RAC_B zero share: {zeros.loc['RAC_B', 'share_zero']:.2%}.",
        f"- SMCI_B zero share: {zeros.loc['SMCI_B', 'share_zero']:.2%}.",
        "",
        "## Delta SMCI Groups",
        "",
        f"- Improved: {int(groups.loc['improved', 'count'])} cells ({groups.loc['improved', 'share']:.2%}).",
        f"- Unchanged: {int(groups.loc['unchanged', 'count'])} cells ({groups.loc['unchanged', 'share']:.2%}).",
        f"- Declined: {int(groups.loc['declined', 'count'])} cells ({groups.loc['declined', 'share']:.2%}).",
        "",
        "## Typology Sanity",
        "",
        f"- NAI high/low margins: {int(typology.loc['NAI high', 'count'])}/{int(typology.loc['NAI low', 'count'])}.",
        f"- MCS high/low margins: {int(typology.loc['MCS high', 'count'])}/{int(typology.loc['MCS low', 'count'])}.",
        f"- NAI-MCS Pearson r: {corr[(corr.left == 'NAI') & (corr.right == 'MCS_B')]['pearson_r'].iloc[0]:.4f}.",
        f"- NAI-MCS Spearman rho: {corr[(corr.left == 'NAI') & (corr.right == 'MCS_B')]['spearman_rho'].iloc[0]:.4f}.",
        "",
        "The symmetric typology counts are produced by rank-based median margins plus weak positive NAI-MCS association. They are not evidence that NAI and MCS are duplicated.",
        "",
        "## Reporting Recommendation",
        "",
        "Report SMCI primarily through maps, percentiles, ranks, and delta groups. Treat absolute mean SMCI as a scale-dependent diagnostic, not as an intuitive welfare magnitude.",
    ]
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metrics", type=Path, default=Path("data/processed/pilot_metrics.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/validation"))
    args = parser.parse_args()

    if not args.metrics.exists():
        raise FileNotFoundError(f"Missing {args.metrics}; run scripts/run_pilot_metrics.py first")

    metrics = pd.read_csv(args.metrics)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    describe_metrics(metrics).to_csv(args.output_dir / "metric_distribution_summary.csv")
    zero_shares(metrics).to_csv(args.output_dir / "zero_inflation_summary.csv", index=False)
    delta_groups(metrics).to_csv(args.output_dir / "delta_smci_groups.csv", index=False)
    normalized_component_summary(metrics).to_csv(args.output_dir / "normalized_component_summary.csv", index=False)
    typology_sanity(metrics).to_csv(args.output_dir / "typology_sanity.csv", index=False)
    correlation_summary(metrics).to_csv(args.output_dir / "distribution_correlation_summary.csv", index=False)
    write_markdown(metrics, args.output_dir / "distribution_diagnostics.md")
    print(f"Wrote distribution diagnostics to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
