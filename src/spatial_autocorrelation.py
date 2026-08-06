"""Reproducible global and local spatial-autocorrelation diagnostics."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import geopandas as gpd
import numpy as np
import pandas as pd
from esda.moran import Moran, Moran_Local
from libpysal.weights import KNN, Queen, Rook, lag_spatial
from statsmodels.stats.multitest import multipletests

DEFAULT_METRICS = ("SMCI_B", "Delta_SMCI", "NAI", "MAI_B", "RAC_B")
DEFAULT_WEIGHT_SPECS = ("queen", "rook", "knn")
QUADRANT_LABELS = {1: "High-High", 2: "Low-High", 3: "Low-Low", 4: "High-Low"}


@dataclass(frozen=True)
class SpatialAutocorrelationResult:
    """Global summaries and per-cell LISA diagnostics for one or more metrics."""

    global_summary: pd.DataFrame
    cell_results: gpd.GeoDataFrame


def _validate_frame(cells: gpd.GeoDataFrame, metrics: Iterable[str]) -> None:
    if cells.crs is None:
        raise ValueError("cells require a defined CRS")
    if cells.empty:
        raise ValueError("cells must not be empty")
    if "cell_id" not in cells or cells["cell_id"].isna().any() or cells["cell_id"].duplicated().any():
        raise ValueError("cells require unique, non-null cell_id values")
    missing = set(metrics) - set(cells.columns)
    if missing:
        raise ValueError(f"cells missing metrics: {sorted(missing)}")
    if cells.geometry.isna().any() or cells.geometry.is_empty.any():
        raise ValueError("cells contain missing or empty geometry")


def build_weights(cells: gpd.GeoDataFrame, specification: str, *, k: int = 8):
    """Build row-standardized Queen, Rook, or k-nearest-neighbour weights."""
    _validate_frame(cells, ())
    ids = cells["cell_id"].tolist()
    if specification == "queen":
        weights = Queen.from_dataframe(cells, ids=ids, use_index=False)
    elif specification == "rook":
        weights = Rook.from_dataframe(cells, ids=ids, use_index=False)
    elif specification == "knn":
        if not 1 <= k < len(cells):
            raise ValueError("k must be between 1 and the number of cells minus one")
        weights = KNN.from_dataframe(cells, k=k, ids=ids, use_index=False)
    else:
        raise ValueError(f"Unsupported weight specification: {specification}")
    weights.transform = "R"
    return weights


def classify_local_quadrants(quadrants: np.ndarray, significant: np.ndarray) -> np.ndarray:
    """Return interpretable LISA labels, leaving non-significant cells unclassified."""
    labels = np.full(len(quadrants), "Not Significant", dtype=object)
    for code, label in QUADRANT_LABELS.items():
        labels[(quadrants == code) & significant] = label
    return labels


def run_spatial_autocorrelation(
    cells: gpd.GeoDataFrame,
    metrics: Iterable[str] = DEFAULT_METRICS,
    weight_specs: Iterable[str] = DEFAULT_WEIGHT_SPECS,
    *,
    permutations: int = 9_999,
    seed: int = 2026,
    alpha: float = 0.05,
    k: int = 8,
) -> SpatialAutocorrelationResult:
    """Run Global Moran's I and FDR-corrected Local Moran's I diagnostics.

    The function preserves row order so each returned result can be joined to
    the input grid by ``cell_id``. Permutation p-values are used because SMCI
    has zero inflation and need not meet a normality assumption.
    """
    metrics = tuple(metrics)
    weight_specs = tuple(weight_specs)
    if permutations < 99:
        raise ValueError("permutations must be at least 99")
    if not 0 < alpha < 1:
        raise ValueError("alpha must be between zero and one")
    _validate_frame(cells, metrics)

    result = cells[["cell_id", "geometry"]].copy()
    global_rows: list[dict[str, object]] = []
    for weight_spec in weight_specs:
        weights = build_weights(cells, weight_spec, k=k)
        for metric in metrics:
            values = pd.to_numeric(cells[metric], errors="raise").to_numpy(dtype=float)
            if not np.isfinite(values).all():
                raise ValueError(f"{metric} contains non-finite values")
            if np.allclose(values, values[0]):
                raise ValueError(f"{metric} is constant; Moran's I is undefined")

            # Moran lacks an explicit seed argument; reset its legacy RNG per run.
            np.random.seed(seed)
            global_moran = Moran(values, weights, permutations=permutations)
            local_moran = Moran_Local(
                values,
                weights,
                permutations=permutations,
                seed=seed,
                n_jobs=1,
                keep_simulations=False,
                alternative="two-sided",
            )
            reject, q_values, _, _ = multipletests(local_moran.p_sim, alpha=alpha, method="fdr_bh")
            labels = classify_local_quadrants(local_moran.q, reject)
            prefix = f"{metric}__{weight_spec}"
            result[f"{prefix}__spatial_lag"] = lag_spatial(weights, values)
            result[f"{prefix}__local_i"] = local_moran.Is
            result[f"{prefix}__p_value"] = local_moran.p_sim
            result[f"{prefix}__q_value"] = q_values
            result[f"{prefix}__cluster"] = labels
            global_rows.append({
                "metric": metric,
                "weight_spec": weight_spec,
                "n_cells": len(cells),
                "permutations": permutations,
                "seed": seed,
                "global_moran_i": float(global_moran.I),
                "global_p_value": float(global_moran.p_sim),
                "global_expected_i": float(global_moran.EI),
                "local_significant_cells": int(reject.sum()),
                "high_high_cells": int((labels == "High-High").sum()),
                "low_low_cells": int((labels == "Low-Low").sum()),
                "high_low_cells": int((labels == "High-Low").sum()),
                "low_high_cells": int((labels == "Low-High").sum()),
            })
    return SpatialAutocorrelationResult(pd.DataFrame(global_rows), result)
