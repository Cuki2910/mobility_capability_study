"""
RAC scaling sensitivity: compare min-max vs log-then-min-max normalization.

Produces:
  outputs/validation/rac_scaling_sensitivity.csv   — per-cell comparison
  outputs/validation/rac_scaling_summary.md        — kappa, typology shift table, narrative

Run:
  python scripts/rac_scaling_sensitivity.py
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def _minmax(x: np.ndarray) -> np.ndarray:
    lo, hi = x.min(), x.max()
    if hi == lo:
        return np.zeros_like(x, dtype=float)
    return (x - lo) / (hi - lo)


def _log_then_minmax(x: np.ndarray) -> np.ndarray:
    """
    log(1+x) → min-max.  log(1+x) is safe for x>=0 and preserves the
    zero floor (log(1+0)=0). Compresses the long right tail without
    requiring the analyst to choose a reference shift.
    """
    return _minmax(np.log1p(x.astype(float)))


def _sqrt_then_minmax(x: np.ndarray) -> np.ndarray:
    """sqrt → min-max: lighter compression than log, included as intermediate."""
    return _minmax(np.sqrt(x.astype(float)))


def _compute_rac_with_scaler(rac_time_raw: np.ndarray, rac_opp_raw: np.ndarray,
                              scaler) -> np.ndarray:
    rt = scaler(rac_time_raw)
    ro = scaler(rac_opp_raw)
    return np.sqrt(rt * ro)


def _compute_rac_shared_with_scaler(
    rac_time_a: np.ndarray, rac_opp_a: np.ndarray,
    rac_time_b: np.ndarray, rac_opp_b: np.ndarray,
    scaler,
) -> tuple[np.ndarray, np.ndarray]:
    """Shared-bounds scaling across Scenario A+B, then apply scaler."""
    combined_time = np.concatenate([rac_time_a, rac_time_b])
    combined_opp = np.concatenate([rac_opp_a, rac_opp_b])

    lo_t, hi_t = combined_time.min(), combined_time.max()
    lo_o, hi_o = combined_opp.min(), combined_opp.max()

    # Shift both pools to [0, range] before the non-linear transform so the
    # same relative positions feed the scaler — avoids the scaler seeing
    # different absolute offsets for A vs B.
    def _scale_pool(vals, lo, hi):
        shifted = vals - lo           # now starts at 0
        return scaler(shifted) if (hi > lo) else np.zeros_like(vals, dtype=float)

    rt_a = _scale_pool(rac_time_a, lo_t, hi_t)
    rt_b = _scale_pool(rac_time_b, lo_t, hi_t)
    ro_a = _scale_pool(rac_opp_a,  lo_o, hi_o)
    ro_b = _scale_pool(rac_opp_b,  lo_o, hi_o)

    # Re-normalise to [0,1] on combined A+B after transform so scale is shared.
    def _shared_norm(a, b):
        lo = min(a.min(), b.min())
        hi = max(a.max(), b.max())
        if hi == lo:
            return np.zeros_like(a), np.zeros_like(b)
        return (a - lo) / (hi - lo), (b - lo) / (hi - lo)

    rt_a, rt_b = _shared_norm(rt_a, rt_b)
    ro_a, ro_b = _shared_norm(ro_a, ro_b)

    return np.sqrt(rt_a * ro_a), np.sqrt(rt_b * ro_b)


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
    """Simple Cohen's kappa between two label arrays."""
    classes = np.unique(np.concatenate([a, b]))
    n = len(a)
    p_o = float((a == b).mean())
    p_e = sum(((a == c).mean() * (b == c).mean()) for c in classes)
    if p_e >= 1.0:
        return 1.0
    return (p_o - p_e) / (1.0 - p_e)


SCALERS = {
    "minmax":       _minmax,
    "log_minmax":   _log_then_minmax,
    "sqrt_minmax":  _sqrt_then_minmax,
}


# -------------------------------------------------------------------
# Main analysis
# -------------------------------------------------------------------

def run_sensitivity(metrics: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    nai   = metrics["NAI"].to_numpy(dtype=float)
    mai_a = metrics["MAI_A"].to_numpy(dtype=float)
    mai_b = metrics["MAI_B"].to_numpy(dtype=float)

    rac_time_a = metrics["RAC_time_A_raw"].to_numpy(dtype=float)
    rac_time_b = metrics["RAC_time_B_raw"].to_numpy(dtype=float)
    rac_opp_a  = metrics["RAC_opp_A_raw"].to_numpy(dtype=float)
    rac_opp_b  = metrics["RAC_opp_B_raw"].to_numpy(dtype=float)

    nai_norm_base = _minmax(nai)

    # Shared MAI bounds (same for all scalers — MAI is not the subject of this test)
    combined_mai = np.concatenate([mai_a, mai_b])
    mai_lo, mai_hi = combined_mai.min(), combined_mai.max()
    mai_a_norm = (mai_a - mai_lo) / (mai_hi - mai_lo) if mai_hi > mai_lo else np.zeros_like(mai_a)
    mai_b_norm = (mai_b - mai_lo) / (mai_hi - mai_lo) if mai_hi > mai_lo else np.zeros_like(mai_b)

    results = {}
    for name, scaler in SCALERS.items():
        rac_a_norm, rac_b_norm = _compute_rac_shared_with_scaler(
            rac_time_a, rac_opp_a, rac_time_b, rac_opp_b, scaler
        )
        rac_lo = min(rac_a_norm.min(), rac_b_norm.min())
        rac_hi = max(rac_a_norm.max(), rac_b_norm.max())
        if rac_hi > rac_lo:
            rac_a_norm = (rac_a_norm - rac_lo) / (rac_hi - rac_lo)
            rac_b_norm = (rac_b_norm - rac_lo) / (rac_hi - rac_lo)

        mcs_b  = np.sqrt(mai_b_norm * rac_b_norm)
        smci_b = nai_norm_base * mai_b_norm * rac_b_norm
        typology_b = _theory_first_typology(nai, mcs_b)

        results[name] = {
            "rac_b_norm":   rac_b_norm,
            "smci_b":       smci_b,
            "typology_b":   typology_b,
            "rac_mean":     float(rac_b_norm.mean()),
            "rac_p99":      float(np.quantile(rac_b_norm, 0.99)),
            "rac_max":      float(rac_b_norm.max()),
            "rac_max_p99_ratio": float(rac_b_norm.max() / np.quantile(rac_b_norm, 0.99))
                                 if np.quantile(rac_b_norm, 0.99) > 0 else np.inf,
            "smci_mean":    float(smci_b.mean()),
            "smci_p50":     float(np.median(smci_b)),
        }

    # Per-cell comparison dataframe
    cell_df = pd.DataFrame({"cell_id": metrics["cell_id"].to_numpy()})
    for name, r in results.items():
        cell_df[f"RAC_B_norm_{name}"]  = r["rac_b_norm"]
        cell_df[f"SMCI_B_{name}"]      = r["smci_b"]
        cell_df[f"typology_B_{name}"]  = r["typology_b"]

    # Kappa matrix + Spearman rho matrix
    scalers_list = list(SCALERS.keys())
    kappa_rows = []
    rho_rows   = []
    for i, s1 in enumerate(scalers_list):
        for s2 in scalers_list[i+1:]:
            kappa = _cohens_kappa(results[s1]["typology_b"], results[s2]["typology_b"])
            rho, _ = spearmanr(results[s1]["smci_b"], results[s2]["smci_b"])
            kappa_rows.append({"comparison": f"{s1} vs {s2}", "cohens_kappa": round(kappa, 4)})
            rho_rows.append(  {"comparison": f"{s1} vs {s2}", "spearman_rho_smci": round(rho, 4)})

    # Typology shift table: how many cells change label minmax→log_minmax?
    base_typ  = results["minmax"]["typology_b"]
    log_typ   = results["log_minmax"]["typology_b"]
    typologies = ["Integrated Capability", "Fragmented Capability",
                  "Transit-Dependent", "Motorcycle Lock-in"]
    shift_rows = []
    for t_from in typologies:
        for t_to in typologies:
            count = int(((base_typ == t_from) & (log_typ == t_to)).sum())
            if count > 0 or t_from == t_to:
                shift_rows.append({
                    "from_minmax": t_from,
                    "to_log_minmax": t_to,
                    "n_cells": count,
                })
    shift_df = pd.DataFrame(shift_rows)

    # Markdown narrative
    md_lines = [
        "# RAC Scaling Sensitivity",
        "",
        "Primary specification: min-max normalization on raw RAC subcomponents.",
        "Sensitivity variants: log(1+x)→min-max (log_minmax) and sqrt→min-max (sqrt_minmax).",
        "All variants use shared Scenario A+B bounds for Delta_SMCI comparability.",
        "",
        "## RAC_B Normalized — Distribution Summary",
        "",
        "| Scaler | mean | p99 | max | max/p99 |",
        "|---|---|---|---|---|",
    ]
    for name, r in results.items():
        md_lines.append(
            f"| {name} | {r['rac_mean']:.4f} | {r['rac_p99']:.4f} | {r['rac_max']:.4f} | {r['rac_max_p99_ratio']:.2f}x |"
        )

    md_lines += [
        "",
        "## SMCI_B Summary",
        "",
        "| Scaler | mean SMCI_B | median SMCI_B |",
        "|---|---|---|",
    ]
    for name, r in results.items():
        md_lines.append(f"| {name} | {r['smci_mean']:.6f} | {r['smci_p50']:.6f} |")

    md_lines += ["", "## Typology Agreement (Cohen's Kappa)", ""]
    for row in kappa_rows:
        interp = ("near-perfect" if row["cohens_kappa"] >= 0.80
                  else "substantial" if row["cohens_kappa"] >= 0.60
                  else "moderate" if row["cohens_kappa"] >= 0.40
                  else "fair")
        md_lines.append(
            f"- **{row['comparison']}**: κ = {row['cohens_kappa']} ({interp})"
        )

    md_lines += ["", "## SMCI Rank Agreement (Spearman ρ)", ""]
    for row in rho_rows:
        md_lines.append(
            f"- **{row['comparison']}**: ρ = {row['spearman_rho_smci']}"
        )

    md_lines += [
        "",
        "## Typology Shift: minmax → log_minmax",
        "",
        "Rows = primary (minmax) label; columns = log_minmax label.",
        "Diagonal = cells that did not change.",
        "",
    ]
    pivot = shift_df.pivot(index="from_minmax", columns="to_log_minmax", values="n_cells").fillna(0).astype(int)
    pivot.index.name = None
    pivot.columns.name = None
    md_lines.append("| From \\ To | " + " | ".join(typologies) + " |")
    md_lines.append("|---|" + "---|" * len(typologies))
    for t_from in typologies:
        row_vals = [str(pivot.loc[t_from, t_to]) if t_to in pivot.columns and t_from in pivot.index else "0"
                    for t_to in typologies]
        md_lines.append(f"| {t_from} | " + " | ".join(row_vals) + " |")

    md_lines += [
        "",
        "## Interpretation",
        "",
        "If κ ≥ 0.70 between minmax and log_minmax, typology findings are robust to the",
        "choice of RAC scaling. If κ < 0.70, the Discussion should acknowledge that",
        "log-transform re-ranks a meaningful fraction of cells and consider it as",
        "a co-equal specification rather than just a robustness check.",
        "",
        "The SMCI mean under log_minmax will be higher than under minmax because the",
        "long right tail of RAC_raw is compressed — this does not invalidate the primary",
        "specification but should be disclosed when reporting headline means.",
    ]

    return cell_df, shift_df, kappa_rows, rho_rows, "\n".join(md_lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metrics",    type=Path, default=Path("data/processed/pilot_metrics.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/validation"))
    args = parser.parse_args()

    if not args.metrics.exists():
        raise FileNotFoundError(f"Missing {args.metrics}; run scripts/run_pilot_metrics.py first")

    metrics = pd.read_csv(args.metrics)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    cell_df, shift_df, kappa_rows, rho_rows, md = run_sensitivity(metrics)

    cell_df.to_csv(args.output_dir / "rac_scaling_sensitivity.csv", index=False)
    shift_df.to_csv(args.output_dir / "rac_scaling_typology_shift.csv", index=False)
    pd.DataFrame(kappa_rows).to_csv(args.output_dir / "rac_scaling_kappa.csv", index=False)
    pd.DataFrame(rho_rows).to_csv(args.output_dir / "rac_scaling_spearman.csv", index=False)
    (args.output_dir / "rac_scaling_summary.md").write_text(md, encoding="utf-8")

    print(f"Wrote RAC scaling sensitivity to {args.output_dir}")
    for r in kappa_rows:
        print(f"  Cohen's kappa {r['comparison']}: {r['cohens_kappa']}")
    for r in rho_rows:
        print(f"  Spearman rho SMCI {r['comparison']}: {r['spearman_rho_smci']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
