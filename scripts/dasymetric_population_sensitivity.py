"""Run a building-constrained WorldPop exposure sensitivity without changing SMCI."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.dasymetric_population import redistribute_population_to_buildings


def _exposure_summary(metrics: pd.DataFrame, population: pd.DataFrame, population_column: str) -> dict:
    data = metrics.merge(population[["cell_id", population_column]], on="cell_id", validate="one_to_one")
    total = float(data[population_column].sum())
    return {
        "total_population": total,
        "population_weighted_smci_b": float((data["SMCI_B"] * data[population_column]).sum() / total),
        **{f"typology_share_{label}": float(group[population_column].sum() / total)
           for label, group in data.groupby("typology_B")},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raster", type=Path, default=Path("data/raw/worldpop/vnm_ppp_2020.tif"))
    parser.add_argument("--grid", type=Path, default=Path("data/interim/pilot_grid.gpkg"))
    parser.add_argument("--buildings", type=Path, default=Path("data/raw/building_footprints.gpkg"))
    parser.add_argument("--metrics", type=Path, default=Path("data/processed/pilot_metrics.csv"))
    parser.add_argument("--baseline-population", type=Path, default=Path("data/interim/grid_worldpop.csv"))
    parser.add_argument("--output", type=Path, default=Path("data/interim/grid_worldpop_dasymetric.csv"))
    parser.add_argument("--report", type=Path, default=Path("outputs/validation/dasymetric_population_sensitivity.md"))
    args = parser.parse_args()

    dasymetric = redistribute_population_to_buildings(args.raster, args.grid, args.buildings)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    dasymetric.to_csv(args.output, index=False)
    baseline = pd.read_csv(args.baseline_population)
    metrics = pd.read_csv(args.metrics)
    baseline_summary = _exposure_summary(metrics, baseline, "pop_sum")
    dasymetric_summary = _exposure_summary(metrics, dasymetric, "pop_sum_dasymetric")
    total_difference = dasymetric_summary["total_population"] - baseline_summary["total_population"]
    lines = [
        "# Dasymetric Population Exposure Sensitivity",
        "",
        "> This is a population-exposure sensitivity. NAI, MAI, RAC, SMCI, and typology are unchanged.",
        "",
        "## Population Conservation",
        "",
        f"- Baseline aggregated population: {baseline_summary['total_population']:.4f}",
        f"- Dasymetric allocated population: {dasymetric_summary['total_population']:.4f}",
        f"- Difference: {total_difference:.4f}",
        f"- Footprint-weighted allocation: {dasymetric['building_allocated_population'].iloc[0]:.4f}",
        f"- Area-fallback allocation where a source pixel has no building: {dasymetric['fallback_allocated_population'].iloc[0]:.4f}",
        "",
        "## Exposure Comparison",
        "",
        "| Metric | Baseline WorldPop | Dasymetric sensitivity | Difference |",
        "| --- | ---: | ---: | ---: |",
        f"| Population-weighted SMCI_B | {baseline_summary['population_weighted_smci_b']:.6f} | {dasymetric_summary['population_weighted_smci_b']:.6f} | {dasymetric_summary['population_weighted_smci_b'] - baseline_summary['population_weighted_smci_b']:.6f} |",
        *[f"| Population share: {label} | {baseline_summary.get(f'typology_share_{label}', 0):.4%} | {dasymetric_summary.get(f'typology_share_{label}', 0):.4%} | {dasymetric_summary.get(f'typology_share_{label}', 0) - baseline_summary.get(f'typology_share_{label}', 0):.4%} |"
          for label in sorted(metrics["typology_B"].unique())],
        "",
        "## Limitation",
        "",
        "Building footprints are not dwelling counts, floor area, height, or residential-use labels. This sensitivity reallocates only within WorldPop source pixels and retains an area fallback for pixels without footprints; it must not be interpreted as a building-level population estimate.",
    ]
    args.report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}, {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
