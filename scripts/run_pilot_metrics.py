"""Compute pilot Scenario A/B metrics from an accessibility-ready cell table."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.pilot import compute_pilot_metrics, pilot_summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/interim/pilot_accessibility_inputs.csv"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/pilot_metrics.csv"))
    parser.add_argument("--summary", type=Path, default=Path("outputs/pilot_summary.csv"))
    args = parser.parse_args()

    if not args.input.exists():
        raise FileNotFoundError(
            f"Missing {args.input}. Build raw network/accessibility inputs before Phase 4."
        )

    inputs = pd.read_csv(args.input)
    metrics = compute_pilot_metrics(inputs)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(args.output, index=False)
    pilot_summary(metrics).to_frame("value").to_csv(args.summary)
    print(f"Wrote {args.output} and {args.summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
