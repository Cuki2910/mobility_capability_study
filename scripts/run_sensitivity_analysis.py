"""Run sensitivity analysis for weights and time decay parameters."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.accessibility_inputs import build_network_accessibility_inputs
from src.pilot import compute_pilot_metrics
from src.accessibility import MAI_DOMAIN_WEIGHTS, theory_first_typology


def get_kappa(labels_a: np.ndarray, labels_b: np.ndarray) -> float:
    from sklearn.metrics import cohen_kappa_score
    return float(cohen_kappa_score(labels_a, labels_b))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--grid", type=Path, default=Path("data/interim/pilot_grid.gpkg"))
    parser.add_argument("--pois", type=Path, default=Path("data/interim/merged_pois.gpkg"))
    parser.add_argument("--walk-graph", type=Path, default=Path("data/raw/pilot_walk_network.graphml"))
    parser.add_argument("--drive-graph", type=Path, default=Path("data/raw/pilot_drive_network.graphml"))
    parser.add_argument("--vinbus-geometry", type=Path, default=Path("data/raw/vinbus_overpass_relations_geom.json"))
    parser.add_argument("--vinbus-gtfs-dir", type=Path, default=Path("data/raw/vinbus_pseudo_gtfs_fixed"))
    parser.add_argument("--speed-factor-csv", type=Path, default=Path("data/raw/motorcycle_speed_calibration.csv"))
    parser.add_argument("--gtfs", type=Path, default=Path("data/raw/hanoi_gtfs.zip"))
    parser.add_argument("--output", type=Path, default=Path("outputs/validation/sensitivity_analysis_report.md"))
    args = parser.parse_args()

    print("Running accessibility sensitivity analysis pipeline...")

    # 1. Rebuild baseline (default weights, 30/60 decay)
    print("Rebuilding baseline model...")
    vinbus_geometry = args.vinbus_geometry if args.vinbus_geometry.exists() else None
    vinbus_gtfs_dir = args.vinbus_gtfs_dir if args.vinbus_gtfs_dir.exists() else None
    speed_csv = args.speed_factor_csv if args.speed_factor_csv.exists() else None

    baseline_inputs = build_network_accessibility_inputs(
        args.grid,
        args.pois,
        args.walk_graph,
        args.drive_graph,
        vinbus_geometry_json=vinbus_geometry,
        gtfs_zip=args.gtfs if args.gtfs.exists() else None,
        gtfs_status="baseline_limited",
        speed_factor_csv=speed_csv,
        vinbus_gtfs_dir=vinbus_gtfs_dir,
        t_full_min=30.0,
        t_zero_min=60.0,
        domain_weights=MAI_DOMAIN_WEIGHTS["default"],
    )
    baseline_metrics = compute_pilot_metrics(baseline_inputs)
    baseline_smci = baseline_metrics["SMCI_B"].to_numpy()
    baseline_typo = baseline_metrics["typology_B"].to_numpy()

    # ── Weight Sensitivity Analysis ──────────────────────────────────────────
    weight_results = []
    for w_name, w_dict in MAI_DOMAIN_WEIGHTS.items():
        print(f"Testing weight set: {w_name}...")
        w_inputs = build_network_accessibility_inputs(
            args.grid,
            args.pois,
            args.walk_graph,
            args.drive_graph,
            vinbus_geometry_json=vinbus_geometry,
            gtfs_zip=args.gtfs if args.gtfs.exists() else None,
            gtfs_status="baseline_limited",
            speed_factor_csv=speed_csv,
            vinbus_gtfs_dir=vinbus_gtfs_dir,
            t_full_min=30.0,
            t_zero_min=60.0,
            domain_weights=w_dict,
        )
        w_metrics = compute_pilot_metrics(w_inputs)
        w_smci = w_metrics["SMCI_B"].to_numpy()
        w_typo = w_metrics["typology_B"].to_numpy()

        kappa = get_kappa(baseline_typo, w_typo)
        rho, _ = spearmanr(baseline_smci, w_smci)
        
        weight_results.append({
            "weight_set": w_name,
            "weights": str(w_dict),
            "spearman_rho": float(rho),
            "cohen_kappa": kappa,
            "mean_smci": float(w_smci.mean()),
            "improved_share": float((w_metrics["Delta_SMCI"] > 0).mean()),
        })

    # ── Decay Threshold Sensitivity Analysis ──────────────────────────────────
    decay_scenarios = [
        {"name": "pessimistic_20_40", "t_full": 20.0, "t_zero": 40.0},
        {"name": "baseline_30_60", "t_full": 30.0, "t_zero": 60.0},
        {"name": "optimistic_45_90", "t_full": 45.0, "t_zero": 90.0},
    ]

    decay_results = []
    for scenario in decay_scenarios:
        print(f"Testing decay scenario: {scenario['name']} ({scenario['t_full']}/{scenario['t_zero']} min)...")
        d_inputs = build_network_accessibility_inputs(
            args.grid,
            args.pois,
            args.walk_graph,
            args.drive_graph,
            vinbus_geometry_json=vinbus_geometry,
            gtfs_zip=args.gtfs if args.gtfs.exists() else None,
            gtfs_status="baseline_limited",
            speed_factor_csv=speed_csv,
            vinbus_gtfs_dir=vinbus_gtfs_dir,
            t_full_min=scenario["t_full"],
            t_zero_min=scenario["t_zero"],
            domain_weights=MAI_DOMAIN_WEIGHTS["default"],
        )
        d_metrics = compute_pilot_metrics(d_inputs)
        d_smci = d_metrics["SMCI_B"].to_numpy()
        d_typo = d_metrics["typology_B"].to_numpy()

        kappa = get_kappa(baseline_typo, d_typo)
        rho, _ = spearmanr(baseline_smci, d_smci)

        decay_results.append({
            "scenario": scenario["name"],
            "t_full": scenario["t_full"],
            "t_zero": scenario["t_zero"],
            "spearman_rho": float(rho),
            "cohen_kappa": kappa,
            "mean_smci": float(d_smci.mean()),
            "improved_share": float((d_metrics["Delta_SMCI"] > 0).mean()),
        })

    # ── Save Markdown Report ──────────────────────────────────────────────────
    lines = [
        "# Sensitivity Analysis Report (MAI and SMCI Parameters)",
        "",
        "Sensitivity analysis evaluating the stability of the Metropolitan Accessibility Index (MAI) ",
        "and Sustainable Mobility Capability Index (SMCI) under different domain weights and time-decay thresholds.",
        "",
        "## 1. Domain Weight Sensitivity",
        "",
        "Comparing different weights across four opportunity domains:",
        "- **default**: Economic (0.40), Education (0.20), Healthcare (0.20), Commerce (0.20)",
        "- **equal**: All domains equal (0.25)",
        "- **job_heavy**: Economic (0.50), Education (0.15), Healthcare (0.15), Commerce (0.20)",
        "",
        "| Weight Scenario | Spearman ρ (vs baseline) | Cohen's Kappa (vs baseline) | Mean SMCI_B | Share Improved |",
        "| --- | --- | --- | --- | --- |",
    ]

    for r in weight_results:
        lines.append(
            f"| **{r['weight_set']}** | {r['spearman_rho']:.4f} | {r['cohen_kappa']:.4f} | "
            f"{r['mean_smci']:.4f} | {r['improved_share']:.2%} |"
        )

    lines.extend([
        "",
        "## 2. Time-Decay Parameter Sensitivity",
        "",
        "Comparing linear decay windows representing accessibility thresholds:",
        "- **pessimistic_20_40**: Full access up to 20 mins, zero access after 40 mins.",
        "- **baseline_30_60**: Full access up to 30 mins, zero access after 60 mins.",
        "- **optimistic_45_90**: Full access up to 45 mins, zero access after 90 mins.",
        "",
        "| Decay Scenario | Spearman ρ (vs baseline) | Cohen's Kappa (vs baseline) | Mean SMCI_B | Share Improved |",
        "| --- | --- | --- | --- | --- |",
    ])

    for r in decay_results:
        lines.append(
            f"| **{r['scenario']}** | {r['spearman_rho']:.4f} | {r['cohen_kappa']:.4f} | "
            f"{r['mean_smci']:.4f} | {r['improved_share']:.2%} |"
        )

    lines.extend([
        "",
        "## 3. Stability Verdict",
        "",
        "A typology Kappa score **>= 0.80** indicates high stability, meaning the classification ",
        "system is robust to minor parameter adjustments. A Spearman rank correlation **>= 0.90** ",
        "indicates that the relative ranking of cells is highly preserved.",
    ])

    # Add verdicts
    weight_stable = all(r["cohen_kappa"] >= 0.80 for r in weight_results)
    decay_stable = all(r["cohen_kappa"] >= 0.80 for r in decay_results if r["scenario"] != "baseline_30_60")

    lines.append("")
    if weight_stable:
        lines.append("🟢 **Weight Stability:** PASS. Typology is robust to alternative domain weights.")
    else:
        lines.append("🟡 **Weight Stability:** WARNING. Alternative weights lead to noticeable typology reclassifications.")

    if decay_stable:
        lines.append("🟢 **Decay Stability:** PASS. Typology is robust to alternative time-decay thresholds.")
    else:
        lines.append("🟡 **Decay Stability:** WARNING. Threshold adjustments lead to noticeable typology reclassifications.")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote sensitivity analysis report to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
