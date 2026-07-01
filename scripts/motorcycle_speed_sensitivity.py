"""Motorcycle speed-calibration sensitivity for the Ocean Park pilot."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tempfile

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.accessibility_inputs import build_network_accessibility_inputs
from src.pilot import compute_pilot_metrics, typology_kappa

SCENARIOS = ("baseline", "slow_congestion", "fast_lane_splitting")


def adjust_motorcycle_calibration(calibration: pd.DataFrame, scenario: str) -> pd.DataFrame:
    """Return calibration table adjusted for a named motorcycle speed scenario."""
    if scenario not in SCENARIOS:
        raise ValueError(f"Unknown scenario: {scenario}")
    out = calibration.copy()
    highway = out["highway"].astype(str)
    if scenario == "slow_congestion":
        mask = highway.isin(["primary", "secondary", "tertiary", "residential"])
        out.loc[mask, "multiplier"] = out.loc[mask, "multiplier"].astype(float) * 0.80
    elif scenario == "fast_lane_splitting":
        mask = highway.isin(["secondary", "tertiary", "residential"])
        out.loc[mask, "multiplier"] = (
            out.loc[mask, "multiplier"].astype(float) * 1.15
        ).clip(upper=1.35)
    out["motorcycle_speed_kph"] = out["base_speed_kph"].astype(float) * out["multiplier"].astype(float)
    return out


def scenario_summary(metrics: pd.DataFrame, baseline_labels: pd.Series, scenario: str) -> dict:
    labels = metrics["typology_B"]
    return {
        "scenario": scenario,
        "mean_SMCI_B": float(metrics["SMCI_B"].mean()),
        "share_improved": float((metrics["Delta_SMCI"] > 0).mean()),
        "typology_kappa_vs_baseline": float(typology_kappa(baseline_labels.to_numpy(), labels.to_numpy())),
        "cells_relabelled_vs_baseline": int((labels.to_numpy() != baseline_labels.to_numpy()).sum()),
        "mean_moto_opp_time_min": float(metrics["moto_mean_opp_time_min"].mean())
        if "moto_mean_opp_time_min" in metrics
        else float("nan"),
        "mean_RAC_B": float(metrics["RAC_B"].mean()),
    }


def write_markdown(summary: pd.DataFrame, path: Path) -> None:
    table = summary.to_csv(index=False, lineterminator="\n").strip()
    lines = [
        "# Motorcycle Speed Sensitivity",
        "",
        "Scenarios vary only Network D motorcycle speed calibration; transit/POI inputs stay fixed.",
        "",
        "```csv",
        table,
        "```",
        "",
        "Interpretation: this is a robustness check for the motorcycle benchmark, not a new observed-speed validation.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--grid", type=Path, default=Path("data/interim/pilot_grid.gpkg"))
    parser.add_argument("--pois", type=Path, default=Path("data/interim/merged_pois.gpkg"))
    parser.add_argument("--walk-graph", type=Path, default=Path("data/raw/pilot_walk_network.graphml"))
    parser.add_argument("--drive-graph", type=Path, default=Path("data/raw/pilot_drive_network.graphml"))
    parser.add_argument("--vinbus-geometry", type=Path, default=Path("data/raw/vinbus_overpass_relations_geom.json"))
    parser.add_argument("--vinbus-gtfs-dir", type=Path, default=Path("data/raw/vinbus_pseudo_gtfs_fixed"))
    parser.add_argument("--gtfs", type=Path, default=Path("data/raw/hanoi_gtfs.zip"))
    parser.add_argument("--calibration", type=Path, default=Path("data/raw/motorcycle_speed_calibration.csv"))
    parser.add_argument("--walking-threshold-m", type=float, default=800.0)
    parser.add_argument("--motorcycle-threshold-m", type=float, default=3000.0)
    parser.add_argument("--buildings", type=Path, default=Path("data/raw/building_footprints.gpkg"))
    parser.add_argument("--worldpop-csv", type=Path, default=Path("data/interim/grid_worldpop.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/validation"))
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    calibration = pd.read_csv(args.calibration)
    rows = []
    baseline_labels = None
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        for scenario in SCENARIOS:
            scenario_csv = tmpdir / f"{scenario}_motorcycle_speed_calibration.csv"
            adjust_motorcycle_calibration(calibration, scenario).to_csv(scenario_csv, index=False)
            inputs = build_network_accessibility_inputs(
                args.grid,
                args.pois,
                args.walk_graph,
                args.drive_graph,
                vinbus_geometry_json=args.vinbus_geometry if args.vinbus_geometry.exists() else None,
                gtfs_zip=args.gtfs if args.gtfs.exists() else None,
                gtfs_status="baseline_limited",
                walk_cutoff_min=args.walking_threshold_m / 80.0,
                motorcycle_cutoff_min=args.motorcycle_threshold_m / 250.0,
                speed_factor_csv=scenario_csv,
                vinbus_gtfs_dir=args.vinbus_gtfs_dir if (args.vinbus_gtfs_dir / "stops.txt").exists() else None,
                buildings_path=args.buildings if args.buildings.exists() else None,
                worldpop_csv=args.worldpop_csv if args.worldpop_csv.exists() else None,
            )
            metrics = compute_pilot_metrics(inputs)
            if baseline_labels is None:
                baseline_labels = metrics["typology_B"].copy()
            rows.append(scenario_summary(metrics, baseline_labels, scenario))

    summary = pd.DataFrame(rows)
    csv_path = args.output_dir / "motorcycle_speed_sensitivity.csv"
    md_path = args.output_dir / "motorcycle_speed_sensitivity.md"
    summary.to_csv(csv_path, index=False)
    write_markdown(summary, md_path)
    print(f"Wrote {csv_path} and {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
