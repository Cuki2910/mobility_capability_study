"""Compare Decision #21 observed-opportunity MAI against proxy baseline."""
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


def run_comparison(args) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    common = dict(
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
    proxy_inputs = build_network_accessibility_inputs(**common, opportunity_basis="proxy")
    observed_inputs = build_network_accessibility_inputs(**common, opportunity_basis="observed")
    proxy_metrics = compute_pilot_metrics(proxy_inputs)
    observed_metrics = compute_pilot_metrics(observed_inputs)
    return proxy_inputs, proxy_metrics, observed_metrics


def write_report(proxy_inputs: pd.DataFrame, proxy: pd.DataFrame, observed: pd.DataFrame, output: Path) -> pd.DataFrame:
    rho, p_value = spearmanr(proxy["SMCI_B"], observed["SMCI_B"])
    kappa = typology_kappa(proxy["typology_B"].to_numpy(), observed["typology_B"].to_numpy())
    relabelled = int((proxy["typology_B"] != observed["typology_B"]).sum())
    vif_proxy = _scenario_b_vif(proxy)
    vif_observed = _scenario_b_vif(observed)

    coverage_cols = [c for c in proxy_inputs.columns if c.startswith("obs_coverage_")]
    coverage = {
        col: float(observed[col].iloc[0]) if col in observed.columns else float(proxy_inputs[col].iloc[0])
        for col in coverage_cols
    }
    rows = [
        {
            "metric": "mean_SMCI_B",
            "proxy": float(proxy["SMCI_B"].mean()),
            "observed": float(observed["SMCI_B"].mean()),
        },
        {
            "metric": "share_improved",
            "proxy": float((proxy["Delta_SMCI"] > 0).mean()),
            "observed": float((observed["Delta_SMCI"] > 0).mean()),
        },
        {"metric": "typology_kappa", "proxy": 1.0, "observed": float(kappa)},
        {"metric": "cells_relabelled", "proxy": 0.0, "observed": float(relabelled)},
        {"metric": "spearman_SMCI_B", "proxy": 1.0, "observed": float(rho)},
        {"metric": "spearman_p_value", "proxy": 0.0, "observed": float(p_value)},
        {"metric": "VIF_MAI", "proxy": float(vif_proxy["MAI"]), "observed": float(vif_observed["MAI"])},
        {"metric": "VIF_RAC", "proxy": float(vif_proxy["RAC"]), "observed": float(vif_observed["RAC"])},
    ]
    summary = pd.DataFrame(rows)

    output.parent.mkdir(parents=True, exist_ok=True)
    summary_csv = output.with_suffix(".csv")
    summary.to_csv(summary_csv, index=False)

    lines = [
        "# Observed-vs-Proxy MAI Sensitivity",
        "",
        "Decision #21 compares the current proxy opportunity weights with the observed-where-available hierarchy.",
        "",
        "## Summary",
        "",
        "| Metric | Proxy | Observed |",
        "|---|---:|---:|",
    ]
    for row in rows:
        lines.append(f"| {row['metric']} | {row['proxy']:.4f} | {row['observed']:.4f} |")
    lines.extend(["", "## Observed Coverage", "", "| Coverage column | Share |", "|---|---:|"])
    for col, value in sorted(coverage.items()):
        lines.append(f"| {col} | {value:.1%} |")
    lines.extend([
        "",
        "## Interpretation",
        "",
        "Observed mode is primary only after this report is reviewed. Proxy mode remains the regression baseline.",
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

    proxy_inputs, proxy_metrics, observed_metrics = run_comparison(args)
    summary = write_report(proxy_inputs, proxy_metrics, observed_metrics, args.output)
    print(f"Wrote {args.output} and {args.output.with_suffix('.csv')}")
    print(summary.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
