"""Bruno-style supplementary neighborhood-access diagnostics."""
from __future__ import annotations

import numpy as np


def category_completeness(reachable_by_category: np.ndarray) -> np.ndarray:
    """Share of categories with at least one reachable destination per cell."""
    values = np.asarray(reachable_by_category, dtype=float)
    if values.ndim != 2 or values.shape[1] == 0:
        raise ValueError("reachable_by_category must be a non-empty 2D array")
    return (values > 0).mean(axis=1)


def neighborhood_proximity_time(
    times_min: np.ndarray,
    k: int = 1,
    missing_penalty_min: float = 20.0,
    category_slots: int | None = None,
) -> np.ndarray:
    """Mean time to K categories, explicitly penalizing absent categories.

    ``category_slots`` makes a requested K larger than the observed columns
    visible rather than silently reducing K. It is useful when a study's
    category framework has not yet supplied all requested categories.
    """
    values = np.asarray(times_min, dtype=float)
    slots = values.shape[1] if category_slots is None else int(category_slots)
    if values.ndim != 2 or k < 1 or slots < values.shape[1] or k > slots:
        raise ValueError("times_min must be 2D and k must be within category_slots")
    filled = np.where(np.isfinite(values), values, float(missing_penalty_min))
    if slots > values.shape[1]:
        padding = np.full((len(values), slots - values.shape[1]), float(missing_penalty_min))
        filled = np.concatenate([filled, padding], axis=1)
    return np.sort(filled, axis=1)[:, :k].mean(axis=1)


def npt_benefit(npt_min: np.ndarray, missing_penalty_min: float = 20.0) -> np.ndarray:
    """Convert a penalized NPT to a bounded higher-is-better diagnostic."""
    if missing_penalty_min <= 0:
        raise ValueError("missing_penalty_min must be positive")
    return np.clip(1.0 - np.asarray(npt_min, dtype=float) / missing_penalty_min, 0.0, 1.0)


def weighted_quantile(values: np.ndarray, weights: np.ndarray, quantiles: np.ndarray) -> np.ndarray:
    """Return deterministic population-weighted quantiles for non-negative values."""
    x, w = np.asarray(values, dtype=float), np.asarray(weights, dtype=float)
    q = np.asarray(quantiles, dtype=float)
    if x.ndim != 1 or w.shape != x.shape or np.any(w < 0) or not np.isfinite(w).all() or w.sum() <= 0:
        raise ValueError("weights must be finite, non-negative, aligned, and sum positive")
    if np.any(~np.isfinite(x)) or np.any((q < 0) | (q > 1)):
        raise ValueError("values must be finite and quantiles must be in [0, 1]")
    order = np.argsort(x, kind="stable")
    return np.interp(q, np.cumsum(w[order]) / w.sum(), x[order])


def weighted_gini(values: np.ndarray, weights: np.ndarray) -> float:
    """Population-weighted Gini with explicit invalid-weight rejection."""
    x, w = np.asarray(values, dtype=float), np.asarray(weights, dtype=float)
    if x.ndim != 1 or w.shape != x.shape or np.any(w < 0) or not np.isfinite(w).all() or w.sum() <= 0:
        raise ValueError("weights must be finite, non-negative, aligned, and sum positive")
    if np.any(x < 0) or not np.isfinite(x).all():
        raise ValueError("values must be finite and non-negative")
    order = np.argsort(x)
    x, w = x[order], w[order]
    cum_xw = np.cumsum(x * w)
    if cum_xw[-1] == 0:
        return 0.0
    width = w / w.sum()
    area = np.sum(width * (cum_xw / cum_xw[-1] + np.r_[0.0, cum_xw[:-1] / cum_xw[-1]]) / 2)
    return float(1 - 2 * area)
