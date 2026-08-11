"""Generate Global Moran's I and FDR-corrected LISA diagnostics for the pilot."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.spatial_autocorrelation import DEFAULT_METRICS, run_spatial_autocorrelation


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
    parser.add_argument("--metrics", type=Path, default=Path("data/processed/pilot_metrics.csv"))
    parser.add_argument("--output-gpkg", type=Path, default=Path("outputs/results/spatial_autocorrelation_cells.gpkg"))
    parser.add_argument("--summary-csv", type=Path, default=Path("outputs/validation/spatial_autocorrelation_global.csv"))
    parser.add_argument("--report", type=Path, default=Path("outputs/validation/spatial_autocorrelation.md"))
    parser.add_argument("--permutations", type=int, default=9_999)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--knn-k", type=int, default=8)
    args = parser.parse_args()

    grid = gpd.read_file(args.grid)
    metrics = pd.read_csv(args.metrics)
    if metrics["cell_id"].duplicated().any():
        raise ValueError("metrics require unique cell_id values")
    cells = grid.merge(metrics[["cell_id", *DEFAULT_METRICS]], on="cell_id", validate="one_to_one")
    if len(cells) != len(grid):
        raise ValueError("metrics do not cover every grid cell")
    result = run_spatial_autocorrelation(
        cells,
        permutations=args.permutations,
        seed=args.seed,
        alpha=args.alpha,
        k=args.knn_k,
    )
    args.output_gpkg.parent.mkdir(parents=True, exist_ok=True)
    args.summary_csv.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    result.cell_results.to_file(args.output_gpkg, driver="GPKG")
    result.global_summary.to_csv(args.summary_csv, index=False)
    lines = [
        "# Spatial Autocorrelation Audit",
        "",
        "> Global Moran's I and Local Moran's I are spatial diagnostics, not causal estimates.",
        "",
        "## Protocol",
        "",
        f"- Permutations: {args.permutations}; seed: {args.seed}; FDR alpha: {args.alpha}",
        "- Primary weights: Queen contiguity. Sensitivities: Rook contiguity and 8-nearest-neighbour.",
        "- Local cluster labels are shown only after Benjamini-Hochberg FDR correction.",
        "",
        "## Global and Local Summary",
        "",
        _markdown_table(result.global_summary.round(6)),
        "",
        "## Interpretation Rule",
        "",
        "A cluster is considered robust only when its substantive pattern appears under Queen weights and at least one sensitivity specification. Zero inflation in SMCI is retained and disclosed; no normality claim is made.",
    ]
    args.report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {args.output_gpkg}, {args.summary_csv}, {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
