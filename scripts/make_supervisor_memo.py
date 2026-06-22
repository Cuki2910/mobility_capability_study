"""Generate supervisor memo from real pilot outputs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"status": "missing", "path": str(path)}


def build_memo(metrics_path: Path, summary_path: Path, output_path: Path) -> str:
    if not metrics_path.exists():
        raise FileNotFoundError(f"Missing {metrics_path}; run scripts/run_pilot_metrics.py first")
    if not summary_path.exists():
        raise FileNotFoundError(f"Missing {summary_path}; run scripts/run_pilot_metrics.py first")

    metrics = pd.read_csv(metrics_path)
    summary = pd.read_csv(summary_path, index_col=0)["value"].to_dict()
    gtfs = _read_json(Path("data/interim/hanoi_gtfs_status.json"))
    pop = _read_json(Path("data/interim/population_proxy_resolution.json"))
    manifest = _read_json(Path("data/interim/pilot_data_manifest.json"))
    vinbus_geom = Path("data/raw/vinbus_overpass_relations_geom.json")
    poi_spot = Path("data/interim/poi_spot_check.csv")
    checked_pois = 0
    if poi_spot.exists():
        spot = pd.read_csv(poi_spot)
        if "spot_check_status" in spot.columns:
            checked_pois = int((spot["spot_check_status"].fillna("unchecked") != "unchecked").sum())

    typology_counts = metrics["typology_B"].value_counts().to_dict() if "typology_B" in metrics else {}
    pop_source = f"raster {pop.get('raster')}" if pop.get("raster") else "manual/parameter resolution input, not a downloaded raster"
    confirmed = [
        f"OSM pilot graph/POI/grid manifest present: {bool(manifest.get('counts'))}.",
        f"VinBus Ocean Park geometry file present: {vinbus_geom.exists()}.",
        f"Processed pilot metrics rows: {len(metrics)}.",
    ]
    if pop.get("resolution_source") == "raster_metadata":
        confirmed.append(f"WorldPop/GHSL raster metadata verified: {pop_source}, ~{float(pop.get('resolution_m', 0.0)):.2f}m resolution.")
    inferred = [
        "Transit accessibility is network-v1/proxy where timetable and stop-access detail is incomplete.",
        f"Network B GTFS status: {gtfs.get('status', 'missing')}.",
        f"Population proxy decision: {pop.get('decision', 'missing')} ({pop_source}).",
    ]
    caveats = [
        f"Network B GTFS status: {gtfs.get('status', 'missing')}.",
        "Population raster is verified but not yet integrated into MAI magnitude weighting.",
        f"POI manual spot-check records completed: {checked_pois}; target >= 20.",
        "Motorcycle validation remains manual consumer-app spot checks; no Google TWO_WHEELER bulk API.",
    ]

    lines = [
        "# Supervisor Memo: Ocean Park Pilot",
        "",
        "## Result Snapshot",
        f"- Grid cells: {int(float(summary.get('n_cells', len(metrics))))}",
        f"- Mean SMCI Scenario A: {float(summary.get('mean_SMCI_A', 0.0)):.4f}",
        f"- Mean SMCI Scenario B: {float(summary.get('mean_SMCI_B', 0.0)):.4f}",
        f"- Mean Delta_SMCI: {float(summary.get('mean_Delta_SMCI', 0.0)):.4f}",
        f"- Share improved: {float(summary.get('share_improved', 0.0)):.2%}",
        "",
        "## Typology Counts, Scenario B",
    ]
    lines += [f"- {label}: {count}" for label, count in typology_counts.items()]
    lines += ["", "## Confirmed Real Data"] + [f"- {item}" for item in confirmed]
    lines += ["", "## Inferred / Proxy Metrics"] + [f"- {item}" for item in inferred]
    lines += ["", "## Unresolved Caveats"] + [f"- {caveat}" for caveat in caveats]
    lines += ["", "## Next Decisions", "- Confirm Network B currency or keep it explicitly baseline-limited.", "- Complete manual Google Maps motorcycle spot-check template."]
    memo = "\n".join(lines) + "\n"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(memo, encoding="utf-8")
    return memo


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metrics", type=Path, default=Path("data/processed/pilot_metrics.csv"))
    parser.add_argument("--summary", type=Path, default=Path("outputs/pilot_summary.csv"))
    parser.add_argument("--output", type=Path, default=Path("outputs/supervisor_memo.md"))
    args = parser.parse_args()
    build_memo(args.metrics, args.summary, args.output)
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
