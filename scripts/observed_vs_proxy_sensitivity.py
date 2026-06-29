"""Compare proxy, hybrid observed, and strict observed MAI specifications."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.accessibility_inputs import build_network_accessibility_inputs
from src.pilot import compute_pilot_metrics, typology_kappa
from src.validation import collinearity_check

def _scenario_b_vif(metrics: pd.DataFrame) -> pd.Series:
    return collinearity_check(
        metrics.rename(columns={"MAI_B": "MAI", "RAC_B": "RAC"})[["NAI", "MAI", "RAC"]]
    )

def _build_common(args) -> dict:
    return dict(
        grid_path=args.grid,
        pois_path=args.pois,
        walk_graphml=args.walk_graph,
        drive_graphml=args.drive_graph,
        vinbus_geometry_json=args.vinbus_geometry if args.vinbus_geometry.exists() else None,
        gtfs_zip=args.gtfs if args.gtfs.exists() else None,
        gtfs_status=args.gtfs_status,
        walk_cutoff_min=args.walking_threshold_m / 80.0,
        motorcycle_cutoff_min=args.motorcycle_threshold_m / 250.0,
        speed_factor_csv=args.speed_factor_csv if args.speed_factor_csv.exists() else None,
        vinbus_gtfs_dir=args.vinbus_gtfs_dir if (args.vinbus_gtfs_dir / "stops.txt").exists() else None,
        buildings_path=args.buildings if args.buildings.exists() else None,
        pop_weighting=not args.no_pop_weighting,
        worldpop_csv=args.worldpop_csv if args.worldpop_csv.exists() else None,
    )

def run_comparison(args) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    common = _build_common(args)
    inputs = {
        basis: build_network_accessibility_inputs(**common, opportunity_basis=basis)
        for basis in ("proxy", "observed", "observed_strict")
    }
    metrics = {basis: compute_pilot_metrics(df) for basis, df in inputs.items()}
    return inputs["observed_strict"], metrics

def _rows(metrics: dict[str, pd.DataFrame]) -> list[dict]:
    proxy = metrics["proxy"]
    vif_proxy = _scenario_b_vif(proxy)
    rows = []
    for metric_name in [
        "mean_SMCI_B",
        "share_improved",
        "typology_kappa",
        "cells_relabelled",
        "spearman_SMCI_B",
        "spearman_p_value",
        "VIF_MAI",
        "VIF_RAC",
    ]:
        row = {"metric": metric_name}
        for basis, candidate in metrics.items():
            if metric_name == "mean_SMCI_B":
                value = float(candidate["SMCI_B"].mean())
            elif metric_name == "share_improved":
                value = float((candidate["Delta_SMCI"] > 0).mean())
            elif metric_name == "typology_kappa":
                value = 1.0 if basis == "proxy" else float(
                    typology_kappa(proxy["typology_B"].to_numpy(), candidate["typology_B"].to_numpy())
                )
            elif metric_name == "cells_relabelled":
                value = 0.0 if basis == "proxy" else float((proxy["typology_B"] != candidate["typology_B"]).sum())
            elif metric_name == "spearman_SMCI_B":
                value = 1.0 if basis == "proxy" else float(spearmanr(proxy["SMCI_B"], candidate["SMCI_B"])[0])
            elif metric_name == "spearman_p_value":
                value = 0.0 if basis == "proxy" else float(spearmanr(proxy["SMCI_B"], candidate["SMCI_B"])[1])
            else:
                vif = vif_proxy if basis == "proxy" else _scenario_b_vif(candidate)
                value = float(vif["MAI"] if metric_name == "VIF_MAI" else vif["RAC"])
            row[basis] = value
        rows.append(row)
    return rows

def write_report(strict_inputs: pd.DataFrame, metrics: dict[str, pd.DataFrame], output: Path) -> pd.DataFrame:
    rows = _rows(metrics)
    summary = pd.DataFrame(rows)

    output.parent.mkdir(parents=True, exist_ok=True)
    summary_csv = output.with_suffix(".csv")
    summary.to_csv(summary_csv, index=False)

    coverage_cols = [c for c in strict_inputs.columns if c.startswith("obs_coverage_")]
    coverage = {col: float(strict_inputs[col].iloc[0]) for col in coverage_cols}

    lines = [
        "# Observed-vs-Proxy MAI Sensitivity",
        "",
        "Decision #21 compares proxy opportunity weights, the hybrid observed hierarchy, "
        "and the strict source-backed observed magnitude specification.",
        "",
        "## Summary",
        "",
        "| Metric | Proxy | Hybrid observed | Strict observed |",
        "|---|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['metric']} | {row['proxy']:.4f} | "
            f"{row['observed']:.4f} | {row['observed_strict']:.4f} |"
        )
    lines.extend(["", "## Strict Observed Coverage", "", "| Coverage column | Share |", "|---|---:|"])
    for col, value in sorted(coverage.items()):
        lines.append(f"| {col} | {value:.1%} |")
    lines.extend([
        "",
        "## Interpretation",
        "",
        "Strict observed mode has no tag-only proxy fallback. Excluded POIs carry explicit audit reasons; "
        "proxy mode remains the regression baseline for sensitivity comparison.",
    ])
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return summary

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--grid", type=Path, default=Path("data/interim/pilot_grid.gpkg"))
    parser.add_argument("--pois", type=Path, default=Path("data/interim/merged_pois_observed.gpkg"))
    parser.add_argument("--walk-graph", type=Path, default=Path("data/raw/pilot_walk_network.graphml"))
    parser.add_argument("--drive-graph", type=Path, default=Path("data/raw/pilot_drive_network.graphml"))
    parser.add_argument("--vinbus-geometry", type=Path, default=Path("data/raw/vinbus_overpass_relations_geom.json"))
    parser.add_argument("--vinbus-gtfs-dir", type=Path, default=Path("data/raw/vinbus_pseudo_gtfs_fixed"))
    parser.add_argument("--speed-factor-csv", type=Path, default=Path("data/raw/motorcycle_speed_calibration.csv"))
    parser.add_argument("--gtfs", type=Path, default=Path("data/raw/hanoi_gtfs.zip"))
    parser.add_argument("--gtfs-status", default="baseline_limited")
    parser.add_argument("--walking-threshold-m", type=float, default=800.0)
    parser.add_argument("--motorcycle-threshold-m", type=float, default=3000.0)
    parser.add_argument("--buildings", type=Path, default=Path("data/raw/building_footprints.gpkg"))
    parser.add_argument("--worldpop-csv", type=Path, default=Path("data/interim/grid_worldpop.csv"))
    parser.add_argument("--no-pop-weighting", action="store_true")
    parser.add_argument("--output", type=Path, default=Path("outputs/validation/observed_vs_proxy_sensitivity.md"))
    args = parser.parse_args()

    strict_inputs, metrics = run_comparison(args)
    summary = write_report(strict_inputs, metrics, args.output)
    print(f"Wrote {args.output} and {args.output.with_suffix('.csv')}")
    print(summary.to_string(index=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
