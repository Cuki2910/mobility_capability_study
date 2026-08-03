"""Measure walking and motorcycle network permeability across Ocean Park's boundary."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import geopandas as gpd
import osmnx as ox
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.boundary_permeability import run_permeability


def _markdown_table(frame: pd.DataFrame) -> str:
    values = frame.fillna("").astype(str)
    return "\n".join([
        "| " + " | ".join(values.columns) + " |",
        "| " + " | ".join("---" for _ in values.columns) + " |",
        *["| " + " | ".join(row) + " |" for row in values.itertuples(index=False, name=None)],
    ])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--grid", type=Path, default=Path("data/interim/pilot_grid.gpkg"))
    parser.add_argument("--boundary", type=Path, default=Path("data/interim/ocean_park_1_boundary.geojson"))
    parser.add_argument("--walk-graph", type=Path, default=Path("data/raw/pilot_walk_network.graphml"))
    parser.add_argument("--motorcycle-graph", type=Path, default=Path("data/raw/pilot_drive_network.graphml"))
    parser.add_argument("--crossings-output", type=Path, default=Path("outputs/results/boundary_permeability_crossings.gpkg"))
    parser.add_argument("--detours-output", type=Path, default=Path("outputs/results/boundary_permeability_detours.csv"))
    parser.add_argument("--summary-output", type=Path, default=Path("outputs/validation/boundary_permeability_summary.csv"))
    parser.add_argument("--report-output", type=Path, default=Path("outputs/validation/boundary_permeability.md"))
    parser.add_argument("--distance-m", type=float, default=250.0)
    parser.add_argument("--sample-nodes", type=int, default=200)
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()

    grid, boundary = gpd.read_file(args.grid), gpd.read_file(args.boundary)
    results = []
    crossing_layers = []
    detour_layers = []
    for mode, graph_path in (("walking", args.walk_graph), ("motorcycle", args.motorcycle_graph)):
        result = run_permeability(
            ox.load_graphml(graph_path), grid, boundary, mode=mode,
            distance_m=args.distance_m, seed=args.seed, sample_nodes=args.sample_nodes,
        )
        results.append(result.summary)
        crossing_layers.append(result.crossings)
        detour_layers.append(result.detours)
    summary = pd.concat(results, ignore_index=True)
    crossings = pd.concat(crossing_layers, ignore_index=True)
    crossings = gpd.GeoDataFrame(crossings, geometry="geometry", crs=crossing_layers[0].crs)
    detours = pd.concat(detour_layers, ignore_index=True)
    for path in (args.crossings_output, args.detours_output, args.summary_output, args.report_output):
        path.parent.mkdir(parents=True, exist_ok=True)
    crossings.to_file(args.crossings_output, driver="GPKG")
    detours.to_csv(args.detours_output, index=False)
    summary.to_csv(args.summary_output, index=False)
    detour_summary = detours.groupby("mode", as_index=False).agg(
        pairs=("status", "size"), reachable=("status", lambda values: int((values == "reachable").sum())),
        median_detour_ratio=("detour_ratio", "median"), max_detour_ratio=("detour_ratio", "max"),
    )
    lines = [
        "# Boundary Permeability Audit",
        "",
        "> This is a topology and routing diagnostic. It does not identify a causal effect of the Ocean Park boundary.",
        "",
        "## Crossing Supply",
        "",
        _markdown_table(summary.round(6)),
        "",
        "## Near-Boundary Detours",
        "",
        _markdown_table(detour_summary.round(6)),
        "",
        "## Data Interpretation",
        "",
        "Crossings are detected where graph-edge endpoints fall on opposite sides of the declared boundary. Access and barrier tags flag potential restrictions, but absent OSM tags do not prove unrestricted access. Approximate edge betweenness uses a fixed seed and samples graph nodes; it is a structural centrality diagnostic, not observed pedestrian or motorcycle flow.",
    ]
    args.report_output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {args.crossings_output}, {args.detours_output}, {args.summary_output}, {args.report_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
