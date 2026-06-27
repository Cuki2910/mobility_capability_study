"""Compare corridor-proxy and stop-level VinBus Network C specifications."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.accessibility_inputs import build_network_accessibility_inputs
from src.pilot import compute_pilot_metrics, pilot_summary, typology_kappa
from src.routing import vinbus_stops_from_overpass


def _summary_row(mode: str, metrics: pd.DataFrame) -> pd.Series:
    row = pilot_summary(metrics)
    row["vinbus_mode"] = mode
    return row


def _finite_metrics(metrics: pd.DataFrame) -> bool:
    numeric = metrics.select_dtypes(include=[np.number])
    return bool(np.isfinite(numeric.to_numpy()).all())


def render_report(
    corridor_metrics: pd.DataFrame,
    stop_metrics: pd.DataFrame,
    stop_count: int,
    output_csv: Path,
) -> str:
    kappa = typology_kappa(corridor_metrics["typology_B"].to_numpy(), stop_metrics["typology_B"].to_numpy())
    smci_rho = float(corridor_metrics["SMCI_B"].corr(stop_metrics["SMCI_B"], method="spearman"))
    rac_rho = float(corridor_metrics["RAC_B"].corr(stop_metrics["RAC_B"], method="spearman"))
    relabelled = int((corridor_metrics["typology_B"] != stop_metrics["typology_B"]).sum())
    n_cells = int(len(stop_metrics))
    stop_valid = stop_count > 0 and n_cells == len(corridor_metrics) and _finite_metrics(stop_metrics)
    verdict = "PROMOTE_STOPS" if stop_valid else "BLOCKED"
    count_table = pd.DataFrame({
        "corridor": corridor_metrics["typology_B"].value_counts(),
        "stops": stop_metrics["typology_B"].value_counts(),
    }).fillna(0).astype(int)
    count_lines = [f"| {idx} | {row['corridor']} | {row['stops']} |" for idx, row in count_table.iterrows()]
    return "\n".join([
        "# VinBus Routing Comparison",
        "",
        f"Verdict: **{verdict}**",
        "",
        "## Inputs",
        "",
        f"- Stop/platform nodes extracted: {stop_count}",
        f"- Cells compared: {n_cells}",
        f"- Per-cell comparison CSV: `{output_csv}`",
        "",
        "## Agreement",
        "",
        f"- Typology kappa, corridor vs stops: {kappa:.3f}",
        f"- Spearman rho, SMCI_B: {smci_rho:.3f}",
        f"- Spearman rho, RAC_B: {rac_rho:.3f}",
        f"- Relabelled cells: {relabelled}/{n_cells} ({relabelled / n_cells:.1%})",
        "",
        "## Typology Counts",
        "",
        "| Typology B | Corridor | Stops |",
        "|---|---:|---:|",
        *count_lines,
        "",
        "## Recommendation",
        "",
        "Use stop-level VinBus routing as the primary Network C specification. Keep corridor routing as a sensitivity/proxy comparison."
        if verdict == "PROMOTE_STOPS"
        else "Do not promote stop-level routing until stop extraction, row counts, and finite metrics are fixed.",
        "",
    ])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--grid", type=Path, default=Path("data/interim/pilot_grid.gpkg"))
    parser.add_argument("--pois", type=Path, default=Path("data/interim/pilot_pois.gpkg"))
    parser.add_argument("--walk-graph", type=Path, default=Path("data/raw/pilot_walk_network.graphml"))
    parser.add_argument("--drive-graph", type=Path, default=Path("data/raw/pilot_drive_network.graphml"))
    parser.add_argument("--vinbus", type=Path, default=Path("data/raw/vinbus_overpass_relations_geom.json"))
    parser.add_argument("--gtfs", type=Path, default=Path("data/raw/hanoi_gtfs.zip"))
    parser.add_argument("--speed-factor-csv", type=Path, default=Path("data/raw/motorcycle_speed_calibration.csv"))
    parser.add_argument("--output", type=Path, default=Path("outputs/validation/vinbus_routing_comparison.md"))
    parser.add_argument("--comparison-csv", type=Path, default=Path("outputs/validation/vinbus_routing_comparison.csv"))
    parser.add_argument("--headway-min", type=float, default=15.0)
    parser.add_argument("--bus-speed-kph", type=float, default=20.0)
    args = parser.parse_args()

    base_kwargs = dict(
        grid_path=args.grid,
        pois_path=args.pois,
        walk_graphml=args.walk_graph,
        drive_graphml=args.drive_graph,
        vinbus_geometry_json=args.vinbus if args.vinbus.exists() else None,
        gtfs_zip=args.gtfs if args.gtfs.exists() else None,
        gtfs_status="baseline_limited",
        walk_cutoff_min=800.0 / 80.0,
        motorcycle_cutoff_min=3000.0 / 250.0,
        speed_factor_csv=args.speed_factor_csv if args.speed_factor_csv.exists() else None,
        headway_min=args.headway_min,
        bus_speed_kph=args.bus_speed_kph,
    )
    corridor_inputs = build_network_accessibility_inputs(**base_kwargs, vinbus_mode="corridor")
    stop_inputs = build_network_accessibility_inputs(**base_kwargs, vinbus_mode="stops")
    corridor_metrics = compute_pilot_metrics(corridor_inputs)
    stop_metrics = compute_pilot_metrics(stop_inputs)

    comparison = pd.DataFrame({
        "cell_id": stop_metrics["cell_id"],
        "SMCI_B_corridor": corridor_metrics["SMCI_B"],
        "SMCI_B_stops": stop_metrics["SMCI_B"],
        "RAC_B_corridor": corridor_metrics["RAC_B"],
        "RAC_B_stops": stop_metrics["RAC_B"],
        "typology_B_corridor": corridor_metrics["typology_B"],
        "typology_B_stops": stop_metrics["typology_B"],
    })
    args.comparison_csv.parent.mkdir(parents=True, exist_ok=True)
    comparison.to_csv(args.comparison_csv, index=False)

    summary = pd.DataFrame([_summary_row("corridor", corridor_metrics), _summary_row("stops", stop_metrics)])
    summary.to_csv(args.comparison_csv.with_name("vinbus_routing_summary.csv"), index=False)

    stop_count = len(vinbus_stops_from_overpass(args.vinbus if args.vinbus.exists() else None))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_report(corridor_metrics, stop_metrics, stop_count, args.comparison_csv), encoding="utf-8")
    print(f"Wrote {args.output} and {args.comparison_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
