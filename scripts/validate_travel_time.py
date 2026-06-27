"""Calculate travel-time validation error metrics against Google Maps measurements."""
from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd
import numpy as np


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
    args = parser.parse_args()

    if not args.csv.exists():
        print(f"Error: {args.csv} not found. Running placeholder setup.")
        return 1

    df = pd.read_csv(args.csv)
    
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

    # Build validation report
    lines = [
        "# Travel Time Validation Report (Motorcycle Mode)",
        "",
        "Validation against manual Google Maps consumer app measurements (two-wheeler mode) in Hanoi/Ocean Park.",
        f"Computed over **{len(valid)}** sample Origin-Destination (OD) pairs.",
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
    lines.append("## Verification Verdict")
    lines.append("")
    if mae < 3.0:
        lines.append("🟢 **PASS:** Mean Absolute Error is below the acceptable research threshold of 3.0 minutes.")
    else:
        lines.append("🔴 **FAIL:** Mean Absolute Error exceeds the acceptable research threshold of 3.0 minutes. Model speed adjustment factors require recalibration.")

    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote travel time validation report to {args.output}")
    print(f"  MAE:  {mae:.2f} min")
    print(f"  MAPE: {mape:.2f}%")
    print(f"  MBE:  {mbe:+.2f} min (systematic bias)")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
