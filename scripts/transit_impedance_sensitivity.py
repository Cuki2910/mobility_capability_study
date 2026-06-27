"""Transit impedance sensitivity for Scenario B behavioral realism."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.pilot import compute_pilot_metrics, typology_kappa

SCENARIOS = {
    "baseline": {"wait": 1.0, "access": 1.0, "egress": 1.0, "penalty_min": 0.0},
    "conservative": {"wait": 1.5, "access": 1.2, "egress": 1.2, "penalty_min": 5.0},
    "pessimistic": {"wait": 2.0, "access": 1.4, "egress": 1.4, "penalty_min": 10.0},
}


def apply_transit_impedance(inputs: pd.DataFrame, scenario: str) -> pd.DataFrame:
    """Apply penalties to walk-transit time only; leave MAI/opportunity weights unchanged."""
    if scenario not in SCENARIOS:
        raise ValueError(f"Unknown scenario: {scenario}")
    params = SCENARIOS[scenario]
    out = inputs.copy()
    if scenario == "baseline":
        return out

    required = {
        "moto_mean_opp_time_min",
        "wt_B_mean_opp_time_min",
        "transit_walk_access_min",
        "transit_wait_min",
        "transit_linehaul_min",
        "transit_egress_min",
    }
    missing = required - set(out.columns)
    if missing:
        raise ValueError(f"Transit impedance input missing columns: {sorted(missing)}")

    component_sum = (
        out["transit_walk_access_min"].astype(float) * params["access"]
        + out["transit_wait_min"].astype(float) * params["wait"]
        + out["transit_linehaul_min"].astype(float)
        + out["transit_egress_min"].astype(float) * params["egress"]
        + params["penalty_min"]
    )
    has_components = (
        out[
            [
                "transit_walk_access_min",
                "transit_wait_min",
                "transit_linehaul_min",
                "transit_egress_min",
            ]
        ]
        .astype(float)
        .sum(axis=1)
        > 0
    )
    penalized = np.where(
        has_components.to_numpy(),
        component_sum.to_numpy(),
        out["wt_B_mean_opp_time_min"].astype(float).to_numpy() + params["penalty_min"],
    )
    penalized = np.maximum(penalized, 1e-9)
    out["wt_B_mean_opp_time_min"] = penalized
    out["RAC_time_B_raw"] = out["moto_mean_opp_time_min"].astype(float).to_numpy() / penalized
    suffix = (
        f" transit impedance sensitivity={scenario}: wait x{params['wait']}, "
        f"access/egress x{params['access']}/{params['egress']}, "
        f"+{params['penalty_min']} min reliability/boarding penalty."
    )
    if "accessibility_input_notes" in out.columns:
        out["accessibility_input_notes"] = out["accessibility_input_notes"].astype(str) + suffix
    return out


def scenario_summary(metrics: pd.DataFrame, baseline: pd.DataFrame, scenario: str) -> dict:
    labels = metrics["typology_B"]
    base_labels = baseline["typology_B"]
    return {
        "scenario": scenario,
        "mean_SMCI_B": float(metrics["SMCI_B"].mean()),
        "SMCI_B_shift_vs_baseline": float(metrics["SMCI_B"].mean() - baseline["SMCI_B"].mean()),
        "share_improved": float((metrics["Delta_SMCI"] > 0).mean()),
        "zero_cells_SMCI_B": int((metrics["SMCI_B"] == 0).sum()),
        "unchanged_cells": int((metrics["Delta_SMCI"] == 0).sum()),
        "typology_kappa_vs_baseline": float(typology_kappa(base_labels.to_numpy(), labels.to_numpy())),
        "cells_relabelled_vs_baseline": int((labels.to_numpy() != base_labels.to_numpy()).sum()),
    }


def write_markdown(summary: pd.DataFrame, path: Path) -> None:
    table = summary.to_csv(index=False, lineterminator="\n").strip()
    lines = [
        "# Transit Impedance Sensitivity",
        "",
        "Penalties are applied only to Scenario B walk-transit travel times. MAI opportunity weights are unchanged.",
        "",
        "```csv",
        table,
        "```",
        "",
        "Interpretation: this is a behavioral-realism sensitivity, not observed mode-choice validation.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/interim/pilot_accessibility_inputs.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/validation"))
    args = parser.parse_args()

    inputs = pd.read_csv(args.input)
    baseline_metrics = compute_pilot_metrics(apply_transit_impedance(inputs, "baseline"))
    rows = []
    for scenario in SCENARIOS:
        metrics = compute_pilot_metrics(apply_transit_impedance(inputs, scenario))
        rows.append(scenario_summary(metrics, baseline_metrics, scenario))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary = pd.DataFrame(rows)
    csv_path = args.output_dir / "transit_impedance_sensitivity.csv"
    md_path = args.output_dir / "transit_impedance_sensitivity.md"
    summary.to_csv(csv_path, index=False)
    write_markdown(summary, md_path)
    print(f"Wrote {csv_path} and {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
