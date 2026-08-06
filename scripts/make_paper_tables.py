"""Generate publication tables from canonical machine-readable artifacts."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_table(frame: pd.DataFrame, stem: Path, title: str) -> None:
    stem.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(stem.with_suffix(".csv"), index=False)
    values = frame.fillna("").astype(str)
    lines = [
        f"# {title}", "",
        "| " + " | ".join(values.columns) + " |",
        "| " + " | ".join("---" for _ in values.columns) + " |",
        *["| " + " | ".join(row) + " |" for row in values.itertuples(index=False, name=None)],
        "",
    ]
    stem.with_suffix(".md").write_text("\n".join(lines), encoding="utf-8")


def _headline_rows(snapshot: dict) -> pd.DataFrame:
    return pd.DataFrame([
        ("Grid cells", snapshot["n_cells"], "cells"),
        ("Mean SMCI A", snapshot["smci"]["mean_A"], "index"),
        ("Mean SMCI B", snapshot["smci"]["mean_B"], "index"),
        ("Mean Delta_SMCI", snapshot["smci"]["mean_delta"], "index"),
        ("Improved", snapshot["delta_groups"]["improved"], "cells"),
        ("Unchanged", snapshot["delta_groups"]["unchanged"], "cells"),
        ("Declined", snapshot["delta_groups"]["declined"], "cells"),
        ("Zero NAI", snapshot["zero_access"]["zero_nai_cells"], "cells"),
        ("Built zero NAI", snapshot["zero_access"]["built_zero_nai_cells"], "cells"),
        ("Population exposed to zero NAI", snapshot["zero_access"]["population_exposed_share"], "share"),
    ], columns=["metric", "value", "unit"])


def _typology_rows(snapshot: dict) -> pd.DataFrame:
    labels = sorted(snapshot["typology_A"])
    total = snapshot["n_cells"]
    return pd.DataFrame([{
        "typology": label,
        "scenario_A_cells": snapshot["typology_A"][label],
        "scenario_B_cells": snapshot["typology_B"][label],
        "scenario_B_share": snapshot["typology_B"][label] / total,
        "scenario_B_population_share": snapshot["population_weighted"]["typology_B_share"][label],
    } for label in labels])


def _robustness_rows(snapshot: dict) -> pd.DataFrame:
    rows = []
    for family, key in (("Motorcycle speed", "motorcycle_speed"), ("Transit impedance", "transit_impedance")):
        for item in snapshot["sensitivities"][key]:
            if item["scenario"] != "baseline":
                rows.append((family, item["scenario"], item["mean_SMCI_B"], item["typology_kappa_vs_baseline"], item["cells_relabelled_vs_baseline"]))
    for item in snapshot["sensitivities"]["nai_threshold"]:
        rows.append(("NAI threshold", f"{item['threshold_m']:.0f} m", item["mean_SMCI_B"], item["typology_kappa_vs_reference"], ""))
    rows.append(("Legacy full RAC", "RAC_time + RAC_opp", "", snapshot["full_rac_agreement"]["kappa"], snapshot["full_rac_agreement"]["cells_relabelled"]))
    return pd.DataFrame(rows, columns=["family", "scenario", "mean_SMCI_B", "typology_kappa", "cells_relabelled"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=Path("outputs/headline_metrics.json"))
    parser.add_argument("--boundary", type=Path, default=Path("outputs/tables/boundary_discontinuity.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/tables"))
    args = parser.parse_args()
    snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
    if snapshot.get("schema_version") != 2:
        raise ValueError("headline snapshot schema_version must be 2")

    provenance = pd.DataFrame([{
        "source_file": source,
        "exists": (path := Path(source)).exists(),
        "bytes": path.stat().st_size if path.exists() else "",
        "sha256": _sha256(path) if path.is_file() else "directory" if path.is_dir() else "",
    } for source in snapshot["source_files"]])
    if not provenance["exists"].all():
        raise FileNotFoundError("one or more canonical source files are missing")

    _write_table(provenance, args.output_dir / "table1_source_provenance", "Table 1. Canonical source provenance")
    _write_table(_headline_rows(snapshot), args.output_dir / "table2_pilot_headline", "Table 2. Pilot headline results")
    _write_table(_typology_rows(snapshot), args.output_dir / "table3_typology", "Table 3. Typology by scenario")
    _write_table(_robustness_rows(snapshot), args.output_dir / "table4_robustness", "Table 4. Robustness matrix")
    _write_table(pd.read_csv(args.boundary), args.output_dir / "table5_boundary_discontinuity", "Table 5. Boundary-band profile")

    manifest = {
        "schema_version": 1,
        "headline_snapshot": args.snapshot.as_posix(),
        "headline_snapshot_sha256": _sha256(args.snapshot),
        "boundary_input": args.boundary.as_posix(),
        "boundary_input_sha256": _sha256(args.boundary),
        "tables": [f"table{i}_{name}" for i, name in enumerate(("source_provenance", "pilot_headline", "typology", "robustness", "boundary_discontinuity"), 1)],
    }
    (args.output_dir / "paper_tables_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote publication tables to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
