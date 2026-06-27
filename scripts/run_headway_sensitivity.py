"""
Run VinBus headway sensitivity analysis (3 scenarios: optimistic/baseline/pessimistic).

Network C now uses API-scraped pseudo-GTFS with *observed* per-route headway
(5-48 min from frequencies.txt). The swept scalar therefore only sets the
fallback default for the handful of routes that lack an observed headway; the
purpose of this sweep is to confirm that the fallback assumption does not drive
results now that most routes carry an observed headway.

For each fallback-headway scenario, re-builds accessibility inputs and re-computes
pilot metrics. Reports per-scenario SMCI summary and typology agreement (Cohen's
kappa) against the primary 15-min fallback. Writes:
  outputs/headway_sensitivity_summary.csv
  outputs/headway_sensitivity_typology.csv
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.accessibility_inputs import build_network_accessibility_inputs
from src.pilot import compute_pilot_metrics, pilot_summary, typology_kappa

HEADWAY_SCENARIOS = {
    "optimistic_10min": 10.0,
    "baseline_15min":   15.0,
    "pessimistic_30min": 30.0,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--grid",         type=Path, default=Path("data/interim/pilot_grid.gpkg"))
    parser.add_argument("--pois",         type=Path, default=Path("data/interim/pilot_pois.gpkg"))
    parser.add_argument("--walk-graph",   type=Path, default=Path("data/raw/pilot_walk_network.graphml"))
    parser.add_argument("--drive-graph",  type=Path, default=Path("data/raw/pilot_drive_network.graphml"))
    parser.add_argument("--vinbus",       type=Path, default=Path("data/raw/vinbus_overpass_relations_geom.json"))
    parser.add_argument("--vinbus-gtfs-dir", type=Path, default=Path("data/raw/vinbus_pseudo_gtfs_fixed"))
    parser.add_argument("--gtfs",         type=Path, default=Path("data/raw/hanoi_gtfs.zip"))
    parser.add_argument("--speed-factor-csv", type=Path, default=Path("data/raw/motorcycle_speed_calibration.csv"))
    parser.add_argument("--output-dir",   type=Path, default=Path("outputs"))
    args = parser.parse_args()

    for req in [args.grid, args.pois, args.walk_graph, args.drive_graph]:
        if not req.exists():
            raise FileNotFoundError(f"Missing {req}. Run scripts/fetch_osm_data.py first.")

    vinbus = args.vinbus if args.vinbus.exists() else None
    gtfs   = args.gtfs   if args.gtfs.exists()   else None
    speed  = args.speed_factor_csv if args.speed_factor_csv.exists() else None
    vinbus_gtfs_dir = (
        args.vinbus_gtfs_dir
        if args.vinbus_gtfs_dir is not None and (args.vinbus_gtfs_dir / "stops.txt").exists()
        else None
    )

    results: dict[str, pd.Series] = {}
    typology_frames: dict[str, pd.Series] = {}

    for scenario, headway in HEADWAY_SCENARIOS.items():
        print(f"  Running headway={headway} min ({scenario})...")
        inputs = build_network_accessibility_inputs(
            args.grid, args.pois, args.walk_graph, args.drive_graph,
            vinbus_geometry_json=vinbus,
            gtfs_zip=gtfs,
            gtfs_status="baseline_limited",
            walk_cutoff_min=800.0 / 80.0,
            motorcycle_cutoff_min=3000.0 / 250.0,
            speed_factor_csv=speed,
            headway_min=headway,
            vinbus_gtfs_dir=vinbus_gtfs_dir,
        )
        metrics = compute_pilot_metrics(inputs)
        summary = pilot_summary(metrics)
        summary["headway_min"] = headway
        results[scenario] = summary
        typology_frames[scenario] = metrics["typology_B"]

    summary_df = pd.DataFrame(results).T.reset_index().rename(columns={"index": "scenario"})

    # Cohen's kappa of each scenario vs the primary baseline (15 min)
    baseline_typology = typology_frames["baseline_15min"]
    kappas = {}
    for scenario, typology in typology_frames.items():
        kappas[scenario] = typology_kappa(baseline_typology.to_numpy(), typology.to_numpy())
    summary_df["kappa_vs_baseline"] = summary_df["scenario"].map(kappas)

    # Also compute RAC_time-only typology kappa for the baseline scenario
    baseline_inputs = build_network_accessibility_inputs(
        args.grid, args.pois, args.walk_graph, args.drive_graph,
        vinbus_geometry_json=vinbus,
        gtfs_zip=gtfs,
        gtfs_status="baseline_limited",
        walk_cutoff_min=800.0 / 80.0,
        motorcycle_cutoff_min=3000.0 / 250.0,
        speed_factor_csv=speed,
        headway_min=15.0,
        vinbus_gtfs_dir=vinbus_gtfs_dir,
    )
    baseline_metrics = compute_pilot_metrics(baseline_inputs)
    kappa_time_only = typology_kappa(
        baseline_metrics["typology_B"].to_numpy(),
        baseline_metrics["typology_B_time_only"].to_numpy(),
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = args.output_dir / "headway_sensitivity_summary.csv"
    summary_df.to_csv(summary_path, index=False)

    # Typology count table per scenario
    typology_rows = []
    for scenario, series in typology_frames.items():
        counts = series.value_counts().rename("count").reset_index()
        counts.columns = ["typology", "count"]
        counts["scenario"] = scenario
        typology_rows.append(counts)
    typology_df = pd.concat(typology_rows, ignore_index=True)
    typology_path = args.output_dir / "headway_sensitivity_typology.csv"
    typology_df.to_csv(typology_path, index=False)

    print(f"\nWrote {summary_path} and {typology_path}")
    print(f"\nRAC_time-only typology kappa vs primary (baseline headway): {kappa_time_only:.4f}")
    print("\nHeadway sensitivity summary:")
    print(summary_df[["scenario", "headway_min", "mean_SMCI_B", "share_improved", "kappa_vs_baseline"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
