"""Compute pilot Scenario A/B metrics from an accessibility-ready cell table."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.site_config import add_site_config_argument, apply_site_config, print_resolved_paths
from src.pilot import compute_pilot_metrics, pilot_summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    add_site_config_argument(parser)
    parser.add_argument("--input", type=Path, default=Path("data/interim/pilot_accessibility_inputs.csv"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/pilot_metrics.csv"))
    parser.add_argument("--summary", type=Path, default=Path("outputs/pilot_summary.csv"))
    args = parser.parse_args()
    config = apply_site_config(args, parser, {
        "input": "paths.accessibility_inputs",
        "output": "paths.metrics",
        "summary": "paths.summary",
    })

    if args.dry_run:
        print_resolved_paths("Metrics run dry-run", {
            "site_id": config.site_id if config else "pilot",
            "input": args.input,
            "output": args.output,
            "summary": args.summary,
        })
        return 0

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
