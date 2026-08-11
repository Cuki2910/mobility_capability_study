"""Record immutable inputs and headline values before geospatial extensions."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.provenance import artifact_record, git_state, write_json_atomic

ARTIFACTS = {
    "grid": "data/interim/pilot_grid.gpkg",
    "boundary": "data/interim/ocean_park_1_boundary.geojson",
    "metrics": "data/processed/pilot_metrics.csv",
    "population": "data/interim/grid_worldpop.csv",
    "walk_network_a": "data/raw/pilot_walk_network.graphml",
    "motorcycle_network_d": "data/raw/pilot_drive_network.graphml",
    "headline": "outputs/headline_metrics.json",
}


def build_snapshot(root: Path) -> dict:
    records = {
        name: artifact_record(root / relative, name)
        for name, relative in ARTIFACTS.items()
    }
    metrics = pd.read_csv(root / ARTIFACTS["metrics"])
    return {
        "schema_version": 1,
        "purpose": "Baseline lock for additive geospatial diagnostics",
        "git": git_state(root),
        "artifacts": records,
        "metrics": {
            "n_cells": int(len(metrics)),
            "mean_SMCI_A": float(metrics["SMCI_A"].mean()),
            "mean_SMCI_B": float(metrics["SMCI_B"].mean()),
            "mean_Delta_SMCI": float(metrics["Delta_SMCI"].mean()),
            "typology_B_counts": metrics["typology_B"].value_counts().sort_index().to_dict(),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-output", type=Path, default=Path("outputs/validation/geospatial_extension_baseline.json"))
    parser.add_argument("--report-output", type=Path, default=Path("outputs/validation/geospatial_extension_baseline.md"))
    args = parser.parse_args()
    snapshot = build_snapshot(ROOT)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.report_output.parent.mkdir(parents=True, exist_ok=True)
    write_json_atomic(args.json_output, snapshot)
    lines = [
        "# Geospatial Extension Baseline",
        "",
        "> This snapshot locks the core inputs and headline values before additive spatial diagnostics.",
        "",
        f"- Git commit: `{snapshot['git']['commit']}`",
        f"- Git dirty at capture: `{snapshot['git']['dirty']}`",
        f"- Grid cells: {snapshot['metrics']['n_cells']}",
        f"- Mean SMCI_A: {snapshot['metrics']['mean_SMCI_A']:.6f}",
        f"- Mean SMCI_B: {snapshot['metrics']['mean_SMCI_B']:.6f}",
        f"- Mean Delta_SMCI: {snapshot['metrics']['mean_Delta_SMCI']:.6f}",
        "",
        "## Typology B Counts",
        "",
        *[f"- {name}: {count}" for name, count in snapshot["metrics"]["typology_B_counts"].items()],
        "",
        "## Artifact Checksums",
        "",
        *[f"- `{item['path']}`: `{item['sha256']}`" for item in snapshot["artifacts"].values()],
    ]
    args.report_output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {args.json_output}, {args.report_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
