"""Validate external observations without substituting cell-level proxies for OD data."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

REQUIRED = ("cell_id", "observed_outcome", "outcome_unit", "observation_date", "source")
MOTORCYCLE_OD_REQUIRED = (
    "sample_id",
    "origin_lat",
    "origin_lon",
    "destination_lat",
    "destination_lon",
    "google_maps_android_minutes",
    "android_lookup_date",
    "android_check_status",
)


def completed_android_motorcycle_observations(frame: pd.DataFrame) -> pd.DataFrame:
    """Return complete Android motorcycle OD records, rejecting incomplete evidence."""
    missing = [column for column in MOTORCYCLE_OD_REQUIRED if column not in frame]
    if missing:
        raise ValueError(f"Android motorcycle OD schema missing columns: {missing}")
    completed = frame.loc[
        frame["android_check_status"].fillna("").str.strip().str.casefold().eq("done")
    ].copy()
    if completed.empty:
        raise ValueError("No Android motorcycle OD observations have android_check_status=done")
    required_values = [column for column in MOTORCYCLE_OD_REQUIRED if column != "android_check_status"]
    if completed[required_values].isna().any().any():
        raise ValueError("Completed Android motorcycle OD observations have missing required values")
    for column in ("origin_lat", "origin_lon", "destination_lat", "destination_lon", "google_maps_android_minutes"):
        completed[column] = pd.to_numeric(completed[column], errors="coerce")
    if completed[["origin_lat", "origin_lon", "destination_lat", "destination_lon", "google_maps_android_minutes"]].isna().any().any():
        raise ValueError("Completed Android motorcycle OD observations have non-numeric coordinates or times")
    if (completed["google_maps_android_minutes"] <= 0).any():
        raise ValueError("Observed Android motorcycle travel times must be positive")
    return completed


def motorcycle_error_metrics(frame: pd.DataFrame) -> dict[str, float | int]:
    """Calculate the predeclared OD travel-time error statistics."""
    observed = pd.to_numeric(frame["google_maps_android_minutes"], errors="raise")
    modelled = pd.to_numeric(frame["model_motorcycle_minutes"], errors="raise")
    error = modelled - observed
    return {
        "n": int(len(frame)),
        "mae_min": round(float(error.abs().mean()), 5),
        "mape_pct": round(float((error.abs() / observed * 100).mean()), 5),
        "mbe_min": round(float(error.mean()), 5),
        "rmse_min": round(float(np.sqrt((error**2).mean())), 5),
    }


def exact_network_motorcycle_minutes(frame: pd.DataFrame, drive_graph: Path, calibration: Path) -> list[float]:
    """Recompute each observed OD pair on the production Network D graph."""
    import networkx as nx
    import osmnx as ox

    from src.networks import build_motorcycle_network

    graph = build_motorcycle_network(drive_graph, speed_factor_csv=calibration)
    minutes: list[float] = []
    for row in frame.itertuples(index=False):
        origin = ox.distance.nearest_nodes(graph, float(row.origin_lon), float(row.origin_lat))
        destination = ox.distance.nearest_nodes(graph, float(row.destination_lon), float(row.destination_lat))
        seconds = nx.shortest_path_length(graph, origin, destination, weight="motorcycle_travel_time_s")
        minutes.append(float(seconds) / 60.0)
    return minutes


def write_manual_status(status: Path, details: Path, drive_graph: Path, calibration: Path, metrics: dict[str, float | int]) -> None:
    """Record a narrowly scoped, reproducible Network D OD plausibility result."""
    calibration_sha256 = hashlib.sha256(calibration.read_bytes()).hexdigest()
    status.parent.mkdir(parents=True, exist_ok=True)
    status.write_text(
        "# External Validation Status\n\n"
        "Status: `COMPLETED_WITH_LIMITATION`\n\n"
        "## Network D Travel-Time Plausibility Check\n\n"
        f"- Audited Android Google Maps motorcycle OD pairs: {metrics['n']}\n"
        f"- Mean absolute error (MAE): {metrics['mae_min']:.2f} min\n"
        f"- Mean absolute percentage error (MAPE): {metrics['mape_pct']:.2f}%\n"
        f"- Mean bias error (MBE): {metrics['mbe_min']:+.2f} min\n"
        f"- Root mean squared error (RMSE): {metrics['rmse_min']:.2f} min\n"
        f"- Exact OD results: `{details}`\n"
        f"- Production drive graph: `{drive_graph}`\n"
        f"- Motorcycle calibration SHA-256: `{calibration_sha256}`\n\n"
        "This validates only the Network D modeled motorcycle travel-time layer against a small, "
        "manually audited consumer-app sample. It does not externally validate SMCI, typologies, "
        "POI opportunity magnitudes, or a causal Scenario B claim.\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--observations", type=Path, default=Path("data/raw/external_validation_template.csv"))
    parser.add_argument("--manual-motorcycle-od", type=Path)
    parser.add_argument("--drive-graph", type=Path, default=Path("data/raw/pilot_drive_network.graphml"))
    parser.add_argument("--calibration", type=Path, default=Path("data/raw/motorcycle_speed_calibration.csv"))
    parser.add_argument("--details", type=Path, default=Path("outputs/validation/external_validation_motorcycle_od.csv"))
    parser.add_argument("--status", type=Path, default=Path("outputs/validation/external_validation_status.md"))
    args = parser.parse_args()

    if args.manual_motorcycle_od:
        if not args.drive_graph.exists() or not args.calibration.exists():
            raise FileNotFoundError("Production drive graph and calibration CSV are required for exact OD validation")
        observations = completed_android_motorcycle_observations(pd.read_csv(args.manual_motorcycle_od))
        observations["model_motorcycle_minutes"] = exact_network_motorcycle_minutes(
            observations, args.drive_graph, args.calibration
        )
        observations["abs_error_minutes"] = (
            observations["model_motorcycle_minutes"] - observations["google_maps_android_minutes"]
        ).abs()
        observations["bias_error_minutes"] = (
            observations["model_motorcycle_minutes"] - observations["google_maps_android_minutes"]
        )
        observations["pct_error"] = observations["abs_error_minutes"] / observations["google_maps_android_minutes"] * 100
        args.details.parent.mkdir(parents=True, exist_ok=True)
        observations.to_csv(args.details, index=False)
        metrics = motorcycle_error_metrics(observations)
        write_manual_status(args.status, args.details, args.drive_graph, args.calibration, metrics)
        print(f"COMPLETED_WITH_LIMITATION: {metrics['n']} Network D OD pairs; MAE={metrics['mae_min']:.2f} min")
        return 0

    frame = pd.read_csv(args.observations)
    missing = [column for column in REQUIRED if column not in frame]
    if missing:
        raise ValueError(f"External validation schema missing columns: {missing}")
    args.status.parent.mkdir(parents=True, exist_ok=True)
    if frame.empty:
        args.status.write_text(
            "# External Validation Status\n\nStatus: `NOT_RUN_DATA_REQUIRED`\n\n"
            "No observational outcomes are available. The template is intentionally not treated as evidence.\n",
            encoding="utf-8",
        )
        print("NOT_RUN_DATA_REQUIRED")
        return 0
    if frame[list(REQUIRED)].isna().any().any():
        raise ValueError("External validation observations have missing required values")
    args.status.write_text(
        f"# External Validation Status\n\nStatus: `READY_TO_RUN`\n\nValidated {len(frame)} observational rows.\n",
        encoding="utf-8",
    )
    print(f"READY_TO_RUN: {len(frame)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
