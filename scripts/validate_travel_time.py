"""Calculate travel-time validation error metrics against Google Maps measurements."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from datetime import datetime, timezone
import sys

import networkx as nx
import numpy as np
import osmnx as ox
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.networks import build_motorcycle_network


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--csv",
        type=Path,
        default=Path("outputs/validation/manual_motorcycle_validation_template.csv"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs/validation/travel_time_validation_report.md"),
    )
    parser.add_argument("--drive-graph", type=Path, default=Path("data/raw/pilot_drive_network.graphml"))
    parser.add_argument("--calibration", type=Path, default=Path("data/raw/motorcycle_speed_calibration.csv"))
    args = parser.parse_args()

    if not args.csv.exists():
        print(f"Error: {args.csv} not found.")
        return 1
    if not args.drive_graph.exists() or not args.calibration.exists():
        raise FileNotFoundError("Production drive graph and calibration CSV are required")

    df = pd.read_csv(args.csv)
    graph = build_motorcycle_network(args.drive_graph, speed_factor_csv=args.calibration)
    model_times = []
    for _, row in df.iterrows():
        origin = ox.distance.nearest_nodes(graph, float(row["origin_lon"]), float(row["origin_lat"]))
        destination = ox.distance.nearest_nodes(graph, float(row["destination_lon"]), float(row["destination_lat"]))
        seconds = nx.shortest_path_length(graph, origin, destination, weight="motorcycle_travel_time_s")
        model_times.append(float(seconds) / 60.0)
    df["model_motorcycle_minutes"] = model_times
    df.to_csv(args.csv, index=False)
    
    # Filter only rows with completed checks
    valid = df[df["google_maps_android_minutes"].notna() & (df["google_maps_android_minutes"] > 0)].copy()
    if len(valid) == 0:
        print("No valid manual measurements found in CSV to compute validation metrics.")
        return 1

    # Recalculate error metrics to be absolutely sure
    valid["abs_error_minutes"] = (valid["model_motorcycle_minutes"] - valid["google_maps_android_minutes"]).abs()
    valid["pct_error"] = (valid["abs_error_minutes"] / valid["google_maps_android_minutes"]) * 100.0
    valid["bias_error"] = valid["model_motorcycle_minutes"] - valid["google_maps_android_minutes"]

    mae = float(valid["abs_error_minutes"].mean())
    mape = float(valid["pct_error"].mean())
    mbe = float(valid["bias_error"].mean())
    rmse = float(np.sqrt((valid["bias_error"] ** 2).mean()))

    calibration_sha256 = hashlib.sha256(args.calibration.read_bytes()).hexdigest()
    generated_at = datetime.now(timezone.utc).isoformat()

    # Build validation report
    lines = [
        "# Travel Time Plausibility Report (Motorcycle Mode)",
        "",
        "Comparison against manual Google Maps consumer-app measurements (two-wheeler mode) in Hanoi/Ocean Park.",
        "This is a small-sample plausibility check, not external calibration validation.",
        f"Computed over **{len(valid)}** sample Origin-Destination (OD) pairs.",
        "",
        "## Reproducibility Metadata",
        "",
        f"- Generated UTC: `{generated_at}`",
        f"- Drive graph: `{args.drive_graph}`",
        f"- Calibration CSV: `{args.calibration}`",
        f"- Calibration SHA-256: `{calibration_sha256}`",
        "- Route weight: `motorcycle_travel_time_s`",
        "- Model times: regenerated from production routing during this run",
        "",
        "## Overall Error Statistics",
        "",
        "| Statistic | Value | Interpretation |",
        "| --- | --- | --- |",
        f"| **Mean Absolute Error (MAE)** | {mae:.2f} minutes | Average magnitude of travel time error. |",
        f"| **Mean Absolute Percentage Error (MAPE)** | {mape:.2f}% | Relative error percentage. |",
        f"| **Mean Bias Error (MBE)** | {mbe:+.2f} minutes | Systematic bias (negative = model is optimistic/faster). |",
        f"| **Root Mean Squared Error (RMSE)** | {rmse:.2f} minutes | Standard deviation of residuals (penalizes larger errors). |",
        "",
        "## Sample Pair Performance Details",
        "",
        "| OD ID | Origin | Destination | Model Time (min) | GMaps Time (min) | Abs Error (min) | Bias (min) | Error % |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]

    for idx, row in valid.iterrows():
        orig = str(row.get("origin_name"))[:25]
        dest = str(row.get("destination_name"))[:25]
        lines.append(
            f"| {row['sample_id']} | {orig} | {dest} | "
            f"{row['model_motorcycle_minutes']:.2f} | {row['google_maps_android_minutes']:.2f} | "
            f"{row['abs_error_minutes']:.2f} | {row['bias_error']:+.2f} | {row['pct_error']:.1f}% |"
        )

    lines.append("")
    lines.append("## Project-Defined Screening Flag")
    lines.append("")
    if mae < 3.0:
        lines.append("**Within project screening bound:** MAE is below the internally defined 3.0-minute diagnostic threshold. This threshold is not an external research standard.")
    else:
        lines.append("**Outside project screening bound:** MAE exceeds the internally defined 3.0-minute diagnostic threshold. This threshold is not an external research standard.")

    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote travel time validation report to {args.output}")
    print(f"  MAE:  {mae:.2f} min")
    print(f"  MAPE: {mape:.2f}%")
    print(f"  MBE:  {mbe:+.2f} min (systematic bias)")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
