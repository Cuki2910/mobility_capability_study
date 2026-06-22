"""Generate validation and robustness tables from processed pilot metrics."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.validation import (
    collinearity_check,
    correlation_matrix,
    network_validation_sample,
    robustness_summary,
    vif_flags,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metrics", type=Path, default=Path("data/processed/pilot_metrics.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/validation"))
    args = parser.parse_args()

    if not args.metrics.exists():
        raise FileNotFoundError(f"Missing {args.metrics}. Run scripts/run_pilot_metrics.py first.")

    metrics = pd.read_csv(args.metrics)
    scenario_b = metrics.rename(columns={"MAI_B": "MAI", "RAC_B": "RAC"})[["NAI", "MAI", "RAC"]]
    args.output_dir.mkdir(parents=True, exist_ok=True)

    vif = collinearity_check(scenario_b)
    correlation_matrix(scenario_b).to_csv(args.output_dir / "correlation_matrix.csv")
    vif_flags(vif).to_csv(args.output_dir / "vif_flags.csv", index=False)
    robustness_summary(metrics["SMCI_B"].to_numpy(), metrics["SMCI_additive_B"].to_numpy()).to_frame("value").to_csv(
        args.output_dir / "robustness_summary.csv"
    )
    template_path = args.output_dir / "manual_motorcycle_validation_template.csv"
    if not template_path.exists():
        network_validation_sample().to_csv(template_path, index=False)
    print(f"Wrote validation tables to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
