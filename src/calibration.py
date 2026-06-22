"""
Motorcycle speed calibration for Network D.

Network D must not use raw OSM car/default driving speeds directly. This module
keeps the calibration explicit: each edge receives a motorcycle speed and travel
time based on highway-class priors plus configurable multipliers.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, MutableMapping

import networkx as nx
import pandas as pd


DEFAULT_BASE_SPEED_KPH: dict[str, float] = {
    "motorway": 55.0,
    "trunk": 50.0,
    "primary": 40.0,
    "secondary": 35.0,
    "tertiary": 30.0,
    "residential": 24.0,
    "unclassified": 24.0,
    "service": 16.0,
    "living_street": 12.0,
    "default": 24.0,
}

DEFAULT_SPEED_MULTIPLIERS: dict[str, float] = {
    "motorway": 0.90,
    "trunk": 0.95,
    "primary": 1.00,
    "secondary": 1.05,
    "tertiary": 1.10,
    "residential": 1.15,
    "unclassified": 1.10,
    "service": 1.00,
    "living_street": 0.90,
    "default": 1.00,
}


@dataclass(frozen=True)
class MotorcycleCalibration:
    """Highway-class speed priors and multipliers used for Network D."""

    base_speed_kph: Mapping[str, float]
    multipliers: Mapping[str, float]
    source_note: str = "Initial literature-calibration priors; replace with cited Hanoi/Vietnam values when available."

    @classmethod
    def defaults(cls) -> "MotorcycleCalibration":
        return cls(DEFAULT_BASE_SPEED_KPH, DEFAULT_SPEED_MULTIPLIERS)


def load_motorcycle_calibration(csv_path: str | Path | None = None) -> MotorcycleCalibration:
    """
    Load calibration from CSV or return explicit defaults.

    CSV columns: `highway`, `base_speed_kph`, `multiplier`. A `default` row is
    recommended so unknown highway classes remain deterministic.
    """
    if csv_path is None:
        return MotorcycleCalibration.defaults()

    table = pd.read_csv(csv_path)
    required = {"highway", "base_speed_kph", "multiplier"}
    missing = required - set(table.columns)
    if missing:
        raise ValueError(f"Calibration CSV missing columns: {sorted(missing)}")

    base = dict(zip(table["highway"], table["base_speed_kph"]))
    mult = dict(zip(table["highway"], table["multiplier"]))
    base.setdefault("default", DEFAULT_BASE_SPEED_KPH["default"])
    mult.setdefault("default", DEFAULT_SPEED_MULTIPLIERS["default"])
    return MotorcycleCalibration(base, mult, f"Loaded from {csv_path}")


def normalize_highway(value) -> str:
    """Return the first OSM highway class when tags are list-like."""
    if isinstance(value, (list, tuple)):
        return str(value[0]) if value else "default"
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "default"
    return str(value)


def calibrated_speed_for_highway(highway, calibration: MotorcycleCalibration) -> float:
    cls = normalize_highway(highway)
    base = float(calibration.base_speed_kph.get(cls, calibration.base_speed_kph["default"]))
    mult = float(calibration.multipliers.get(cls, calibration.multipliers["default"]))
    return base * mult


def apply_motorcycle_calibration(
    graph: nx.MultiDiGraph,
    calibration: MotorcycleCalibration | None = None,
) -> nx.MultiDiGraph:
    """Copy `graph`, attach motorcycle speeds, and compute seconds per edge."""
    calibration = calibration or MotorcycleCalibration.defaults()
    calibrated = graph.copy()

    for _, _, _, data in calibrated.edges(keys=True, data=True):
        speed_kph = calibrated_speed_for_highway(data.get("highway"), calibration)
        length_m = float(data.get("length", 0.0))
        data["motorcycle_speed_kph"] = speed_kph
        data["motorcycle_travel_time_s"] = length_m / (speed_kph * 1000 / 3600) if speed_kph > 0 else float("inf")
        data["calibration_source"] = calibration.source_note

    return calibrated


def calibration_table(calibration: MotorcycleCalibration | None = None) -> pd.DataFrame:
    """Human-readable calibration table for reports and supervisor review."""
    calibration = calibration or MotorcycleCalibration.defaults()
    rows: list[MutableMapping[str, float | str]] = []
    for highway in sorted(set(calibration.base_speed_kph) | set(calibration.multipliers)):
        base = float(calibration.base_speed_kph.get(highway, calibration.base_speed_kph["default"]))
        mult = float(calibration.multipliers.get(highway, calibration.multipliers["default"]))
        rows.append({
            "highway": highway,
            "base_speed_kph": base,
            "multiplier": mult,
            "motorcycle_speed_kph": base * mult,
            "source_note": calibration.source_note,
        })
    return pd.DataFrame(rows)
