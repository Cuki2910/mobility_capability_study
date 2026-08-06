"""Descriptive mobility-capability profiles around a site boundary."""
from __future__ import annotations

from typing import Iterable

import geopandas as gpd
import numpy as np
import pandas as pd

BAND_EDGES_M = (0.0, 250.0, 500.0, 1000.0)
METRICS = ("NAI", "MAI_B", "RAC_B", "SMCI_B", "Delta_SMCI")


def validate_cell_ids(frame: pd.DataFrame, name: str) -> None:
    if "cell_id" not in frame:
        raise ValueError(f"{name} missing cell_id")
    if frame["cell_id"].isna().any() or frame["cell_id"].duplicated().any():
        raise ValueError(f"{name} cell_id must be non-null and unique")


def attach_boundary_metrics(
    grid: gpd.GeoDataFrame,
    boundary: gpd.GeoDataFrame,
    edges_m: tuple[float, ...] = BAND_EDGES_M,
) -> gpd.GeoDataFrame:
    """Return projected cells with overlap, signed centroid distance, and fixed bands."""
    validate_cell_ids(grid, "grid")
    if grid.crs is None or boundary.crs is None:
        raise ValueError("grid and boundary require defined CRS")
    if grid.empty or boundary.empty:
        raise ValueError("grid and boundary must be non-empty")
    if tuple(edges_m) != tuple(sorted(set(edges_m))) or edges_m[0] != 0 or len(edges_m) < 2:
        raise ValueError("band edges must be unique, sorted, and start at zero")

    metric_crs = grid.estimate_utm_crs()
    if metric_crs is None:
        raise ValueError("unable to estimate metric CRS")
    cells = grid.to_crs(metric_crs).copy()
    site = boundary.to_crs(metric_crs).geometry.union_all()
    if site.is_empty:
        raise ValueError("boundary geometry is empty")

    centroids = cells.geometry.centroid
    inside = centroids.apply(site.covers).to_numpy(dtype=bool)
    distance = centroids.distance(site.boundary).to_numpy(dtype=float)
    area = cells.geometry.area.to_numpy(dtype=float)
    overlap = cells.geometry.intersection(site).area.to_numpy(dtype=float)
    cells["inside_boundary"] = inside
    cells["overlap_ratio"] = np.divide(overlap, area, out=np.zeros_like(overlap), where=area > 0)
    cells["signed_distance_m"] = np.where(inside, distance, -distance)

    absolute = np.abs(cells["signed_distance_m"].to_numpy())
    intervals = pd.cut(absolute, bins=list(edges_m), right=True, include_lowest=True)
    cells["distance_band"] = [
        (f"inside_{int(interval.left)}_{int(interval.right)}m" if is_inside else
         f"outside_{int(interval.left)}_{int(interval.right)}m")
        if pd.notna(interval) else "beyond_1000m"
        for interval, is_inside in zip(intervals, inside)
    ]
    return cells


def merge_cell_data(
    cells: gpd.GeoDataFrame,
    metrics: pd.DataFrame,
    population: pd.DataFrame,
) -> gpd.GeoDataFrame:
    validate_cell_ids(cells, "grid")
    validate_cell_ids(metrics, "metrics")
    validate_cell_ids(population, "population")
    required = set(METRICS) | {"typology_B"}
    missing = required - set(metrics.columns)
    if missing:
        raise ValueError(f"metrics missing columns: {sorted(missing)}")
    if "pop_sum" not in population:
        raise ValueError("population missing pop_sum")
    result = cells.merge(metrics[["cell_id", *METRICS, "typology_B"]], on="cell_id", validate="one_to_one")
    result = result.merge(population[["cell_id", "pop_sum"]], on="cell_id", validate="one_to_one")
    if len(result) != len(cells):
        raise ValueError("cell IDs do not match across grid, metrics, and population")
    return result


def _weighted_mean(values: pd.Series, weights: pd.Series) -> float:
    valid = values.notna() & weights.notna() & (weights >= 0)
    total = float(weights[valid].sum())
    return float(np.average(values[valid], weights=weights[valid])) if total > 0 else np.nan


def summarize_bands(cells: pd.DataFrame, min_cells: int = 5) -> pd.DataFrame:
    """Summarize fixed bands; retain sparse bands and flag them instead of merging."""
    rows: list[dict] = []
    for band, group in cells[cells["distance_band"] != "beyond_1000m"].groupby("distance_band", sort=False):
        row = {
            "distance_band": band,
            "side": "inside" if str(band).startswith("inside") else "outside",
            "n_cells": len(group),
            "sparse_band": len(group) < min_cells,
            "population": float(group["pop_sum"].sum()),
            "zero_nai_share": float(group["NAI"].eq(0).mean()),
        }
        for metric in METRICS:
            row[f"{metric}_mean"] = float(group[metric].mean())
            row[f"{metric}_median"] = float(group[metric].median())
            row[f"{metric}_population_weighted"] = _weighted_mean(group[metric], group["pop_sum"])
        shares = group["typology_B"].value_counts(normalize=True)
        for label, share in shares.items():
            row[f"typology_share_{label}"] = float(share)
        rows.append(row)
    return pd.DataFrame(rows)


def bootstrap_near_boundary(
    cells: pd.DataFrame,
    metrics: Iterable[str] = METRICS,
    distance_m: float = 250.0,
    iterations: int = 2000,
    seed: int = 2026,
) -> pd.DataFrame:
    """Bootstrap inside-minus-outside median differences near the boundary."""
    near = cells[np.abs(cells["signed_distance_m"]) <= distance_m]
    inside = near[near["inside_boundary"]]
    outside = near[~near["inside_boundary"]]
    if inside.empty or outside.empty:
        raise ValueError("near-boundary comparison requires cells on both sides")
    rng = np.random.default_rng(seed)
    rows = []
    for metric in metrics:
        a = inside[metric].dropna().to_numpy(dtype=float)
        b = outside[metric].dropna().to_numpy(dtype=float)
        if not len(a) or not len(b):
            raise ValueError(f"{metric} has no valid observations on one side")
        draws = np.empty(iterations)
        for i in range(iterations):
            draws[i] = np.median(rng.choice(a, len(a), replace=True)) - np.median(rng.choice(b, len(b), replace=True))
        rows.append({
            "metric": metric,
            "distance_m": distance_m,
            "inside_n": len(a),
            "outside_n": len(b),
            "inside_median": float(np.median(a)),
            "outside_median": float(np.median(b)),
            "median_difference_inside_minus_outside": float(np.median(a) - np.median(b)),
            "bootstrap_ci_low": float(np.quantile(draws, .025)),
            "bootstrap_ci_high": float(np.quantile(draws, .975)),
            "bootstrap_iterations": iterations,
            "seed": seed,
        })
    return pd.DataFrame(rows)
