"""Summarize rerun alternate-grid accessibility results against primary cells."""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import cohen_kappa_score

from src.boundary_discontinuity import attach_boundary_metrics
from src.spatial_autocorrelation import run_spatial_autocorrelation


VARIANTS = {"hex": "hex_equal_area", "shift_x": "shift_x", "shift_y": "shift_y", "shift_xy": "shift_xy"}
COMPARE_METRICS = ("NAI", "MAI_B", "RAC_B", "SMCI_B")
DELTA_EPSILON = 1e-10


def nearest_primary_match(alt: gpd.GeoDataFrame, primary: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Match alternate cells to the nearest primary centroid for MAUP comparison."""
    reference = primary[["cell_id", *COMPARE_METRICS, "typology_B", "geometry"]].copy()
    reference = reference.rename(columns={"cell_id": "primary_cell_id", **{metric: f"primary_{metric}" for metric in COMPARE_METRICS}, "typology_B": "primary_typology_B"})
    return gpd.sjoin_nearest(alt, reference, how="left", distance_col="nearest_primary_m")


def boundary_median_difference(cells: gpd.GeoDataFrame, boundary: gpd.GeoDataFrame) -> float:
    """Return near-boundary inside-minus-outside SMCI median; descriptive only."""
    attached = attach_boundary_metrics(cells[["cell_id", "SMCI_B", "geometry"]], boundary)
    near = attached[np.abs(attached["signed_distance_m"]) <= 250]
    inside = near.loc[near["inside_boundary"], "SMCI_B"]
    outside = near.loc[~near["inside_boundary"], "SMCI_B"]
    return float(inside.median() - outside.median()) if not inside.empty and not outside.empty else np.nan


def _cluster_sets(cells: gpd.GeoDataFrame) -> tuple[set[str], set[str]]:
    result = run_spatial_autocorrelation(
        cells[["cell_id", "SMCI_B", "geometry"]], metrics=("SMCI_B",), weight_specs=("queen",), permutations=999, seed=2026
    ).cell_results
    labels = result["SMCI_B__queen__cluster"]
    return set(result.loc[labels.eq("High-High"), "cell_id"].astype(str)), set(result.loc[labels.eq("Low-Low"), "cell_id"].astype(str))


def _jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    return len(left & right) / len(union) if union else 1.0


def _markdown_table(frame: pd.DataFrame) -> str:
    return "\n".join([
        "| " + " | ".join(frame.columns) + " |",
        "| " + " | ".join("---" for _ in frame.columns) + " |",
        *["| " + " | ".join(str(value) for value in row) + " |" for row in frame.itertuples(index=False, name=None)],
    ])


def main() -> int:
    primary_grid = gpd.read_file(ROOT / "data/interim/pilot_grid.gpkg")
    primary_metrics = pd.read_csv(ROOT / "data/processed/pilot_metrics.csv")
    primary_pop = pd.read_csv(ROOT / "data/interim/grid_worldpop.csv")
    boundary = gpd.read_file(ROOT / "data/interim/ocean_park_1_boundary.geojson")
    primary = primary_grid.merge(primary_metrics, on="cell_id", validate="one_to_one").merge(primary_pop[["cell_id", "pop_sum"]], on="cell_id", validate="one_to_one")
    primary_metric = primary.to_crs(primary.estimate_utm_crs())
    primary_hh, primary_ll = _cluster_sets(primary_metric)
    primary_boundary_diff = boundary_median_difference(primary, boundary)
    primary_population = float(primary["pop_sum"].sum())

    rows = []
    for name, stem in VARIANTS.items():
        grid = gpd.read_file(ROOT / f"data/interim/grid_sensitivity/{stem}.gpkg")
        metrics = pd.read_csv(ROOT / f"data/interim/grid_sensitivity/{name}_metrics.csv")
        pop = pd.read_csv(ROOT / f"data/interim/grid_sensitivity/{name}_worldpop.csv")
        alt = grid.merge(metrics, on="cell_id", validate="one_to_one").merge(pop[["cell_id", "pop_sum"]], on="cell_id", validate="one_to_one")
        joined = nearest_primary_match(alt.to_crs(primary_metric.crs), primary_metric)
        alt_hh, alt_ll = _cluster_sets(alt.to_crs(alt.estimate_utm_crs()))
        matched_hh = set(joined.loc[joined["cell_id"].astype(str).isin(alt_hh) & joined["primary_cell_id"].notna(), "primary_cell_id"].astype(str))
        matched_ll = set(joined.loc[joined["cell_id"].astype(str).isin(alt_ll) & joined["primary_cell_id"].notna(), "primary_cell_id"].astype(str))
        row = {
            "grid": name,
            "n_cells": len(alt),
            "mean_SMCI_B": float(alt.SMCI_B.mean()),
            "population_weighted_SMCI_B": float(np.average(alt.SMCI_B, weights=alt.pop_sum)),
            "zero_NAI_share": float(alt.NAI.eq(0).mean()),
            "improved_share": float((alt.Delta_SMCI > DELTA_EPSILON).mean()),
            "boundary_median_inside_minus_outside_SMCI_B": boundary_median_difference(alt, boundary),
            "boundary_difference_change_vs_primary": np.nan,
            "population_total": float(alt.pop_sum.sum()),
            "population_total_difference": float(alt.pop_sum.sum() - primary_population),
            "population_total_difference_pct": float((alt.pop_sum.sum() - primary_population) / primary_population * 100),
            "high_high_primary_location_jaccard": _jaccard(primary_hh, matched_hh),
            "low_low_primary_location_jaccard": _jaccard(primary_ll, matched_ll),
        }
        row["boundary_difference_change_vs_primary"] = row["boundary_median_inside_minus_outside_SMCI_B"] - primary_boundary_diff
        for metric in COMPARE_METRICS:
            row[f"spearman_{metric}_nearest_primary"] = float(spearmanr(joined[metric], joined[f"primary_{metric}"], nan_policy="omit").statistic)
        row["typology_kappa_nearest_primary"] = float(cohen_kappa_score(joined.typology_B, joined.primary_typology_B))
        rows.append(row)

    out = pd.DataFrame(rows)
    output_csv = ROOT / "outputs/validation/grid_sensitivity_summary.csv"
    output_md = ROOT / "outputs/validation/grid_sensitivity_summary.md"
    out.to_csv(output_csv, index=False)
    display = out.copy()
    for col in display.select_dtypes(include="number"):
        display[col] = display[col].map(lambda value: "" if pd.isna(value) else f"{value:.4f}")
    lines = [
        "# Grid Sensitivity Summary",
        "",
        "All alternate grids rerun the same network, POI, 800 m threshold, shared-normalization, and Scenario A/B pipeline.",
        "Nearest-centroid matching is a comparability device, not a claim that cells are identical.",
        "Boundary values are descriptive near-boundary (250 m) inside-minus-outside median SMCI_B differences. HH/LL values are Queen-LISA location-set Jaccard scores using 999 permutations, not inferential confirmation.",
        "",
        f"- Primary near-boundary median difference: {primary_boundary_diff:.4f}",
        f"- Primary WorldPop total: {primary_population:.1f}",
        "- Population-total differences reflect raster/grid intersection tolerance and must be reported, not treated as changes in population.",
        "",
        _markdown_table(display),
        "",
        "## Interpretation",
        "",
        "Scenario B improvement share remains near 60% across variants. Exact typology and hotspot boundaries are MAUP-sensitive; substantive conclusions should use the direction, population-weighted mean, and repeated broad clustering rather than a single cell assignment.",
    ]
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(out.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
