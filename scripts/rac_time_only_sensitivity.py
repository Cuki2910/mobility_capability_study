"""
RAC_time-only sensitivity: contingency for high VIF between MAI and RAC.

Primary MAI/RAC VIF is structural and usually exceeds the threshold of 5.
This is structural (RAC_opp numerator = MAI_transit), not coincidental.
The contingency in decisions.md #3 is to replace RAC = sqrt(RAC_time * RAC_opp)
with RAC_time alone, then recheck typology agreement.

Produces:
  outputs/validation/rac_time_only_sensitivity.csv   — per-cell comparison
  outputs/validation/rac_time_only_summary.md        — kappa, shift table, VIF

Run:
  python scripts/rac_time_only_sensitivity.py
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from statsmodels.stats.outliers_influence import variance_inflation_factor


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def _minmax_shared(a: np.ndarray, b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    lo = min(a.min(), b.min())
    hi = max(a.max(), b.max())
    if hi == lo:
        return np.zeros_like(a), np.zeros_like(b)
    return (a - lo) / (hi - lo), (b - lo) / (hi - lo)


def _minmax(x: np.ndarray) -> np.ndarray:
    lo, hi = x.min(), x.max()
    if hi == lo:
        return np.zeros_like(x, dtype=float)
    return (x - lo) / (hi - lo)


def _theory_first_typology(nai: np.ndarray, mcs: np.ndarray) -> np.ndarray:
    n = len(nai)
    nai_rank = np.argsort(np.argsort(nai, kind="stable"), kind="stable")
    mcs_rank = np.argsort(np.argsort(mcs, kind="stable"), kind="stable")
    nai_hi = nai_rank >= n // 2
    mcs_hi = mcs_rank >= n // 2
    labels = np.empty(n, dtype=object)
    labels[nai_hi &  mcs_hi]  = "Integrated Capability"
    labels[nai_hi & ~mcs_hi]  = "Fragmented Capability"
    labels[~nai_hi &  mcs_hi] = "Transit-Dependent"
    labels[~nai_hi & ~mcs_hi] = "Motorcycle Lock-in"
    return labels


def _cohens_kappa(a: np.ndarray, b: np.ndarray) -> float:
    classes = np.unique(np.concatenate([a, b]))
    p_o = float((a == b).mean())
    p_e = sum((a == c).mean() * (b == c).mean() for c in classes)
    return (p_o - p_e) / (1.0 - p_e) if p_e < 1.0 else 1.0


def _compute_vif(df_norm: pd.DataFrame) -> pd.DataFrame:
    X = df_norm.values.astype(float)
    rows = []
    for i, col in enumerate(df_norm.columns):
        vif = variance_inflation_factor(X, i)
        rows.append({"variable": col, "VIF": round(vif, 4), "flag_high_vif": vif > 5})
    return pd.DataFrame(rows)


TYPOLOGIES = [
    "Integrated Capability",
    "Fragmented Capability",
    "Transit-Dependent",
    "Motorcycle Lock-in",
]


# -------------------------------------------------------------------
# Main analysis
# -------------------------------------------------------------------

def run_sensitivity(metrics: pd.DataFrame) -> str:
    nai        = metrics["NAI"].to_numpy(dtype=float)
    mai_b      = metrics["MAI_B"].to_numpy(dtype=float)
    rac_time_b = metrics["RAC_time_B"].to_numpy(dtype=float)  # already normalized in pilot
    rac_b_norm = metrics["RAC_B_norm"].to_numpy(dtype=float)  # full composite (time+opp)

    nai_norm  = _minmax(nai)
    mai_b_norm = metrics["MAI_B_norm"].to_numpy(dtype=float)

    # ---- Spec A: primary (full RAC = sqrt(time * opp), already in metrics) ----
    mcs_primary   = np.sqrt(mai_b_norm * rac_b_norm)
    smci_primary  = nai_norm * mai_b_norm * rac_b_norm
    typ_primary   = _theory_first_typology(nai, mcs_primary)

    # ---- Spec B: RAC_time-only (shared A+B scale, recompute from raw) ----
    rac_time_a_raw = metrics["RAC_time_A_raw"].to_numpy(dtype=float)
    rac_time_b_raw = metrics["RAC_time_B_raw"].to_numpy(dtype=float)
    rt_a_norm, rt_b_norm = _minmax_shared(rac_time_a_raw, rac_time_b_raw)
    # shared RAC composite scale
    rt_a_final, rt_b_final = _minmax_shared(rt_a_norm, rt_b_norm)

    mcs_timonly  = np.sqrt(mai_b_norm * rt_b_final)
    smci_timonly = nai_norm * mai_b_norm * rt_b_final
    typ_timonly  = _theory_first_typology(nai, mcs_timonly)

    # ---- VIF for each spec ----
    vif_primary = _compute_vif(pd.DataFrame({
        "NAI": nai_norm, "MAI": mai_b_norm, "RAC": rac_b_norm
    }))
    vif_timonly = _compute_vif(pd.DataFrame({
        "NAI": nai_norm, "MAI": mai_b_norm, "RAC_time": rt_b_final
    }))

    # ---- Agreement stats ----
    kappa = _cohens_kappa(typ_primary, typ_timonly)
    rho, _ = spearmanr(smci_primary, smci_timonly)

    # ---- Per-cell CSV ----
    cell_df = pd.DataFrame({
        "cell_id":          metrics["cell_id"].to_numpy(),
        "typology_primary": typ_primary,
        "typology_timonly": typ_timonly,
        "SMCI_B_primary":   smci_primary,
        "SMCI_B_timonly":   smci_timonly,
        "label_changed":    (typ_primary != typ_timonly),
    })

    # ---- Typology shift matrix ----
    shift_rows = []
    for t_from in TYPOLOGIES:
        for t_to in TYPOLOGIES:
            n_cells = int(((typ_primary == t_from) & (typ_timonly == t_to)).sum())
            if n_cells > 0 or t_from == t_to:
                shift_rows.append({"from_primary": t_from, "to_timonly": t_to, "n_cells": n_cells})
    shift_df = pd.DataFrame(shift_rows)

    # ---- Markdown ----
    kappa_interp = (
        "near-perfect" if kappa >= 0.80 else
        "substantial"  if kappa >= 0.60 else
        "moderate"     if kappa >= 0.40 else "fair/poor"
    )

    def _vif_table(vif_df: pd.DataFrame) -> list[str]:
        lines = ["| Variable | VIF | Flag |", "|---|---:|---|"]
        for _, row in vif_df.iterrows():
            flag = "HIGH ⚠" if row["flag_high_vif"] else "OK"
            lines.append(f"| {row['variable']} | {row['VIF']:.2f} | {flag} |")
        return lines

    def _shift_table(df: pd.DataFrame) -> list[str]:
        pivot = df.pivot(index="from_primary", columns="to_timonly", values="n_cells").fillna(0).astype(int)
        header = "| From (primary) \\ To (RAC_time) | " + " | ".join(TYPOLOGIES) + " |"
        sep    = "|---|" + "---|" * len(TYPOLOGIES)
        lines  = [header, sep]
        for t_from in TYPOLOGIES:
            vals = [str(pivot.loc[t_from, t_to]) if t_to in pivot.columns and t_from in pivot.index else "0"
                    for t_to in TYPOLOGIES]
            lines.append(f"| {t_from} | " + " | ".join(vals) + " |")
        return lines

    n_changed = int((typ_primary != typ_timonly).sum())
    primary_vif = vif_primary.set_index("variable")["VIF"]
    md_lines = [
        "# RAC_time-only Sensitivity (VIF Contingency)",
        "",
        f"**Motivation:** VIF(MAI)={primary_vif['MAI']:.2f} and VIF(RAC)={primary_vif['RAC']:.2f} in the pilot both exceed the",
        "threshold of 5. This is structural: RAC_opp numerator = MAI_transit (decisions.md #3).",
        "The contingency is to replace RAC = sqrt(RAC_time × RAC_opp) with RAC_time alone.",
        "",
        "## VIF — Primary Specification (full RAC)",
        "",
        *_vif_table(vif_primary),
        "",
        "## VIF — RAC_time-only Specification",
        "",
        *_vif_table(vif_timonly),
        "",
        "## Typology Agreement",
        "",
        f"- Cohen's κ: **{kappa:.4f}** ({kappa_interp})",
        f"- Spearman ρ (SMCI rank): **{rho:.4f}**",
        f"- Cells that changed label: **{n_changed} / {len(nai)}** ({n_changed/len(nai):.1%})",
        "",
        "## Typology Shift Matrix",
        "",
        "Rows = primary label; columns = RAC_time-only label. Diagonal = no change.",
        "",
        *_shift_table(shift_df),
        "",
        "## Interpretation",
        "",
    ]

    if kappa >= 0.70:
        md_lines += [
            f"κ = {kappa:.4f} ≥ 0.70: typology findings are **robust** to replacing",
            "the full RAC composite with RAC_time alone. Despite high VIF between MAI and",
            "RAC in the primary specification, the classification outcome is not driven by",
            "the shared MAI_transit component in RAC_opp.",
            "",
            "**Recommendation:** report the primary (full RAC) specification as the main",
            "result. Report RAC_time-only as a VIF robustness check in the validation section.",
        ]
    else:
        md_lines += [
            f"κ = {kappa:.4f} < 0.70: typology findings are **sensitive** to the VIF issue.",
            "A meaningful share of cells change label when RAC_opp is removed.",
            "",
            "**Recommendation:** elevate RAC_time-only to a co-primary specification.",
            "Present both typology maps side-by-side and discuss where they diverge.",
            "Do not claim the full-RAC typology is uniquely valid without addressing",
            "the MAI/RAC_opp double-counting concern more explicitly in Methods.",
        ]

    return cell_df, shift_df, vif_primary, vif_timonly, kappa, rho, n_changed, "\n".join(md_lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metrics",    type=Path, default=Path("data/processed/pilot_metrics.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/validation"))
    args = parser.parse_args()

    if not args.metrics.exists():
        raise FileNotFoundError(f"Missing {args.metrics}; run scripts/run_pilot_metrics.py first")

    metrics = pd.read_csv(args.metrics)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    cell_df, shift_df, vif_primary, vif_timonly, kappa, rho, n_changed, md = run_sensitivity(metrics)

    cell_df.to_csv(args.output_dir / "rac_time_only_sensitivity.csv", index=False)
    shift_df.to_csv(args.output_dir / "rac_time_only_shift.csv", index=False)
    vif_primary.to_csv(args.output_dir / "vif_primary.csv", index=False)
    vif_timonly.to_csv(args.output_dir / "vif_timonly.csv", index=False)
    (args.output_dir / "rac_time_only_summary.md").write_text(md, encoding="utf-8")

    print(f"Wrote RAC_time-only sensitivity to {args.output_dir}")
    print(f"  Cohen's kappa:    {kappa:.4f}")
    print(f"  Spearman rho:     {rho:.4f}")
    print(f"  Cells relabelled: {n_changed}/{len(pd.read_csv(args.metrics))} ({n_changed/len(pd.read_csv(args.metrics)):.1%})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
