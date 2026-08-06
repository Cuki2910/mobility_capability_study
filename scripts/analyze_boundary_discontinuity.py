"""Run descriptive boundary-band analysis for the Ocean Park pilot."""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from boundary_discontinuity import attach_boundary_metrics, bootstrap_near_boundary, merge_cell_data, summarize_bands


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _markdown_table(frame: pd.DataFrame) -> str:
    values = frame.fillna("").astype(str)
    header = "| " + " | ".join(values.columns) + " |"
    separator = "| " + " | ".join("---" for _ in values.columns) + " |"
    rows = ["| " + " | ".join(row) + " |" for row in values.itertuples(index=False, name=None)]
    return "\n".join([header, separator, *rows])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--grid", type=Path, default=Path("data/interim/pilot_grid.gpkg"))
    parser.add_argument("--boundary", type=Path, default=Path("data/interim/ocean_park_1_boundary.geojson"))
    parser.add_argument("--metrics", type=Path, default=Path("data/processed/pilot_metrics.csv"))
    parser.add_argument("--population", type=Path, default=Path("data/interim/grid_worldpop.csv"))
    parser.add_argument("--cells-output", type=Path, default=Path("outputs/results/boundary_cell_metrics.csv"))
    parser.add_argument("--table-output", type=Path, default=Path("outputs/tables/boundary_discontinuity.csv"))
    parser.add_argument("--report-output", type=Path, default=Path("outputs/validation/boundary_discontinuity.md"))
    parser.add_argument("--min-cells", type=int, default=5)
    parser.add_argument("--bootstrap-iterations", type=int, default=2000)
    args = parser.parse_args()

    for path in (args.grid, args.boundary, args.metrics, args.population):
        if not path.exists():
            raise FileNotFoundError(path)
    grid = gpd.read_file(args.grid)
    boundary = gpd.read_file(args.boundary)
    cells = attach_boundary_metrics(grid, boundary)
    cells = merge_cell_data(cells, pd.read_csv(args.metrics), pd.read_csv(args.population))
    summary = summarize_bands(cells, min_cells=args.min_cells)
    bootstrap = bootstrap_near_boundary(cells, iterations=args.bootstrap_iterations)

    args.cells_output.parent.mkdir(parents=True, exist_ok=True)
    args.table_output.parent.mkdir(parents=True, exist_ok=True)
    args.report_output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(cells.drop(columns="geometry")).to_csv(args.cells_output, index=False)
    summary.to_csv(args.table_output, index=False)

    sparse = summary[summary["sparse_band"]]
    smci = bootstrap.loc[bootstrap["metric"] == "SMCI_B"].iloc[0]
    direction = "higher" if smci["median_difference_inside_minus_outside"] > 0 else "lower"
    support = (
        "directional descriptive discontinuity"
        if smci["bootstrap_ci_low"] > 0 or smci["bootstrap_ci_high"] < 0
        else "spatial concentration without a stable near-boundary difference"
    )
    lines = [
        "# Boundary Discontinuity Audit",
        "",
        "> Descriptive spatial comparison only. Not a causal regression-discontinuity design.",
        "",
        "## Near-boundary result (0–250 m)",
        "",
        f"- SMCI_B median inside: {smci['inside_median']:.6f}",
        f"- SMCI_B median outside: {smci['outside_median']:.6f}",
        f"- Inside-minus-outside difference: {smci['median_difference_inside_minus_outside']:.6f}",
        f"- Bootstrap 95% CI: [{smci['bootstrap_ci_low']:.6f}, {smci['bootstrap_ci_high']:.6f}]",
        f"- Interpretation: inside median is {direction}; evidence supports **{support}**.",
        "",
        "## Band adequacy",
        "",
        f"- Minimum requested cells per band: {args.min_cells}",
        f"- Sparse bands retained and flagged: {', '.join(sparse['distance_band']) if not sparse.empty else 'none'}",
        "",
        "## Reproducibility",
        "",
        f"- Metric CRS: {cells.crs}",
        f"- Bootstrap iterations: {args.bootstrap_iterations}; seed: 2026",
        f"- Grid SHA-256: `{_sha256(args.grid)}`",
        f"- Boundary SHA-256: `{_sha256(args.boundary)}`",
        f"- Metrics SHA-256: `{_sha256(args.metrics)}`",
        f"- Population SHA-256: `{_sha256(args.population)}`",
        "",
        "## Bootstrap estimates",
        "",
        _markdown_table(bootstrap),
        "",
        "## Band summaries",
        "",
        _markdown_table(summary),
    ]
    args.report_output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {args.cells_output}, {args.table_output}, {args.report_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
