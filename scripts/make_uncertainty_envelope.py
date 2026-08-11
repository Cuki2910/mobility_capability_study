"""Build a guarded, cell-level scenario sensitivity envelope on the GM scale."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


CELL_SOURCES = {
    "motorcycle_speed": (Path("outputs/validation/motorcycle_speed_sensitivity_cells.csv"), "scenario"),
    "transit_impedance": (Path("outputs/validation/transit_impedance_sensitivity_cells.csv"), "scenario"),
    "nai_threshold": (Path("outputs/validation/nai_threshold_sensitivity_cells.csv"), "threshold_m"),
}
METRIC_VARIANT_CELLS = Path("outputs/validation/metric_variant_cells.csv")
REQUIRED_COLUMNS = {"cell_id", "SMCI_A", "SMCI_B", "Delta_SMCI"}


def load_validated_sensitivity_cells(path: Path, variant_column: str, source: str) -> pd.DataFrame:
    """Read a sensitivity artifact only when its raw GM cell values are explicit."""
    if not path.exists():
        raise FileNotFoundError(path)
    frame = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing or variant_column not in frame:
        raise ValueError(f"{source} is not a cell-level GM sensitivity artifact: missing {sorted(missing)}")
    if frame[list(REQUIRED_COLUMNS)].isna().any().any():
        raise ValueError(f"{source} contains missing SMCI values")
    out = frame[["cell_id", "SMCI_A", "SMCI_B", "Delta_SMCI", variant_column]].copy()
    out["specification"] = source + ":" + out[variant_column].astype(str)
    return out.drop(columns=variant_column)


def make_envelope(cells: pd.DataFrame) -> pd.DataFrame:
    """Calculate a sensitivity range, never a statistical confidence interval."""
    rows = []
    for cell_id, group in cells.groupby("cell_id", sort=True):
        row: dict[str, float | int] = {"cell_id": cell_id, "n_specifications": len(group)}
        for metric in ("SMCI_A", "SMCI_B", "Delta_SMCI"):
            values = group[metric].to_numpy(dtype=float)
            row.update({
                f"{metric}_min": float(values.min()),
                f"{metric}_p05": float(np.quantile(values, 0.05)),
                f"{metric}_p25": float(np.quantile(values, 0.25)),
                f"{metric}_median": float(np.median(values)),
                f"{metric}_p75": float(np.quantile(values, 0.75)),
                f"{metric}_p95": float(np.quantile(values, 0.95)),
                f"{metric}_max": float(values.max()),
            })
        rows.append(row)
    return pd.DataFrame(rows)


def load_metric_variant_cells(path: Path) -> pd.DataFrame:
    """Convert the wide metric-variant audit to explicit A/B/delta scenarios."""
    if not path.exists():
        raise FileNotFoundError(path)
    frame = pd.read_csv(path)
    if "cell_id" not in frame:
        raise ValueError("metric variant cells missing cell_id")
    suffix = "_SMCI_B"
    variants = [column[: -len(suffix)] for column in frame.columns if column.endswith(suffix)]
    frames = []
    for variant in variants:
        columns = [f"{variant}_SMCI_A", f"{variant}_SMCI_B", f"{variant}_Delta_SMCI"]
        if not set(columns).issubset(frame.columns):
            continue
        out = frame[["cell_id", *columns]].copy()
        out.columns = ["cell_id", "SMCI_A", "SMCI_B", "Delta_SMCI"]
        out["specification"] = "metric_variant:" + variant
        frames.append(out)
    if not frames:
        raise ValueError("metric variant cells lack complete geometric A/B/delta columns")
    return pd.concat(frames, ignore_index=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("outputs/validation/scenario_uncertainty_envelope_cells.csv"))
    parser.add_argument("--status", type=Path, default=Path("outputs/validation/scenario_uncertainty_envelope_status.md"))
    parser.add_argument("--inventory", type=Path, default=Path("outputs/validation/scenario_uncertainty_envelope_inventory.csv"))
    args = parser.parse_args()
    rows, frames = [], []
    for source, (path, variant_column) in CELL_SOURCES.items():
        try:
            frame = load_validated_sensitivity_cells(path, variant_column, source)
            frames.append(frame)
            rows.append({"source": source, "path": str(path), "status": "GEOMETRIC_CELL_LEVEL", "n_rows": len(frame)})
        except (FileNotFoundError, ValueError) as exc:
            rows.append({"source": source, "path": str(path), "status": "DATA_REQUIRED", "n_rows": 0, "detail": str(exc)})
    try:
        frame = load_metric_variant_cells(METRIC_VARIANT_CELLS)
        frames.append(frame)
        rows.append({"source": "metric_variants", "path": str(METRIC_VARIANT_CELLS), "status": "GEOMETRIC_CELL_LEVEL", "n_rows": len(frame)})
    except (FileNotFoundError, ValueError) as exc:
        rows.append({"source": "metric_variants", "path": str(METRIC_VARIANT_CELLS), "status": "DATA_REQUIRED", "n_rows": 0, "detail": str(exc)})
    inventory = pd.DataFrame(rows)
    args.inventory.parent.mkdir(parents=True, exist_ok=True)
    inventory.to_csv(args.inventory, index=False)
    if not frames:
        args.status.write_text("# Scenario Uncertainty Envelope Status\n\nStatus: `CODE_COMPLETE_DATA_REQUIRED`\n\nNo compatible cell-level geometric sensitivity artifact is available.\n", encoding="utf-8")
        print("CODE_COMPLETE_DATA_REQUIRED")
        return 0
    all_cells = pd.concat(frames, ignore_index=True)
    envelope = make_envelope(all_cells)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    envelope.to_csv(args.output, index=False)
    missing_sources = inventory["status"].ne("GEOMETRIC_CELL_LEVEL").any()
    status = "COMPLETED_WITH_LIMITATION" if missing_sources else "COMPLETED"
    lines = [
        "# Scenario Uncertainty Envelope",
        "",
        f"Status: `{status}`",
        "",
        "This is a per-cell sensitivity envelope, not a confidence interval. It summarizes only rerun geometric-mean specifications with explicit cell-level Scenario A/B values.",
        f"- Cells: {len(envelope)}",
        f"- Included specifications: {all_cells['specification'].nunique()}",
        "- Quantiles: p05, p25, median, p75, p95; plus min/max.",
        "",
        "## Source inventory",
        "",
        "| Source | Status | Rows |",
        "|---|---|---:|",
        *[f"| {row.source} | {row.status} | {row.n_rows} |" for row in inventory.itertuples(index=False)],
    ]
    args.status.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
