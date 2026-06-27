"""Generate supervisor memo from real pilot outputs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"status": "missing", "path": str(path)}


def _spot_check_summary(path: Path) -> tuple[int, dict]:
    if not path.exists():
        return 0, {}
    spot = pd.read_csv(path)
    if "spot_check_status" not in spot.columns:
        return 0, {}
    status = spot["spot_check_status"].fillna("unchecked")
    return int((status != "unchecked").sum()), status.value_counts().to_dict()


def _motorcycle_summary(path: Path) -> dict:
    if not path.exists():
        return {"completed": 0}
    df = pd.read_csv(path)
    if "google_maps_android_minutes" not in df.columns:
        return {"completed": 0}
    done = df[df["google_maps_android_minutes"].notna()].copy()
    out = {"completed": len(done), "total": len(df)}
    if not done.empty and "abs_error_minutes" in done.columns:
        errors = pd.to_numeric(done["abs_error_minutes"], errors="coerce").dropna()
        if not errors.empty:
            out["mae_minutes"] = float(errors.abs().mean())
            out["bias_minutes"] = float(errors.mean())
    return out


def _delta_groups(path: Path) -> dict:
    if not path.exists():
        return {}
    df = pd.read_csv(path)
    if not {"group", "count", "share"} <= set(df.columns):
        return {}
    return {
        str(row["group"]): {"count": int(row["count"]), "share": float(row["share"])}
        for _, row in df.iterrows()
    }


def _distribution_note(path: Path) -> str | None:
    if not path.exists():
        return None
    df = pd.read_csv(path)
    if not {"metric", "mean_norm", "p99_raw", "max_raw"} <= set(df.columns):
        return None
    by_metric = df.set_index("metric")
    if "RAC_B" not in by_metric.index:
        return None
    rac = by_metric.loc["RAC_B"]
    return (
        "Mean SMCI is small mainly because RAC_B is compressed by an extreme max "
        f"(mean normalized RAC_B={rac['mean_norm']:.4f}; p99={rac['p99_raw']:.4f}; max={rac['max_raw']:.4f}) "
        "and zero-valued components make multiplicative SMCI exactly zero for many cells."
    )


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
    mobilitydb_candidates = Path("data/interim/mobility_database_hanoi_candidates.csv")
    checked_pois, poi_breakdown = _spot_check_summary(Path("data/interim/poi_spot_check.csv"))
    moto = _motorcycle_summary(Path("outputs/validation/manual_motorcycle_validation_template.csv"))
    delta = _delta_groups(Path("outputs/validation/delta_smci_groups.csv"))
    distribution_note = _distribution_note(Path("outputs/validation/normalized_component_summary.csv"))
    vif_path = Path("outputs/validation/vif_flags.csv")
    built_audit = Path("outputs/validation/built_population_zero_access.md")
    merged_poi_sensitivity = Path("outputs/validation/merged_poi_sensitivity.md")
    gtfs_catalog_check = Path("outputs/validation/gtfs_catalog_check.md")
    maps_dir = Path("outputs/maps")
    figures_dir = Path("outputs/figures")

    typology_counts = metrics["typology_B"].value_counts().to_dict() if "typology_B" in metrics else {}
    pop_source = f"raster {pop.get('raster')}" if pop.get("raster") else "manual/parameter resolution input, not a downloaded raster"
    gtfs_vintage = gtfs.get("gtfs_vintage")
    pre_vinbus = gtfs.get("pre_vinbus_baseline", False)
    gtfs_interp = gtfs.get("network_b_interpretation", gtfs.get("status", "missing"))

    confirmed = [
        f"OSM pilot graph/POI/grid manifest present: {bool(manifest.get('counts'))}.",
        f"VinBus Ocean Park geometry file present: {vinbus_geom.exists()}.",
        f"Processed pilot metrics rows: {len(metrics)}.",
        f"POI spot-check completed: {checked_pois}/20 ({poi_breakdown}).",
        "Android motorcycle validation completed: "
        + f"{moto.get('completed', 0)}/{moto.get('total', 10)}"
        + (f"; MAE={moto['mae_minutes']:.2f} min, bias={moto['bias_minutes']:.2f} min." if "mae_minutes" in moto else "."),
    ]
    if pop.get("resolution_source") == "raster_metadata":
        confirmed.append(f"WorldPop/GHSL raster metadata verified: {pop_source}, ~{float(pop.get('resolution_m', 0.0)):.2f}m resolution.")
    if mobilitydb_candidates.exists():
        try:
            n_candidates = len(pd.read_csv(mobilitydb_candidates))
        except EmptyDataError:
            n_candidates = 0
        confirmed.append(f"MobilityDatabase catalog checked for Hanoi GTFS candidates: {n_candidates} found.")
    if gtfs_catalog_check.exists():
        confirmed.append("TUMI/Datahub GTFS candidates documented as future current-service/time-of-day sensitivity, not baseline replacement.")
    if built_audit.exists():
        confirmed.append("Built/population zero-access audit completed with building footprints and WorldPop.")
    gate_path = Path("outputs/validation/overture_gate_result.md")
    gate_text = gate_path.read_text(encoding="utf-8") if gate_path.exists() else ""
    if "Verdict: **PASS**" in gate_text:
        confirmed.append("Overture POI gate passed; merged OSM+Overture POI layer is now primary.")
    elif merged_poi_sensitivity.exists():
        confirmed.append("Merged OSM+Overture POI sensitivity completed; OSM-only remains primary pending Overture-only spot-check.")
    if maps_dir.exists():
        confirmed.append("Quick-look SVG maps and GIS map layer generated in outputs/maps/.")
    if figures_dir.exists():
        confirmed.append("Paper-facing composite figures and captions generated in outputs/figures/.")

    inferred = [
        "Transit accessibility is network-v1/proxy where timetable and stop-access detail is incomplete.",
        f"Network B GTFS status: {gtfs.get('status', 'missing')}"
        + (f" (vintage {gtfs_vintage}; {gtfs_interp})" if gtfs_vintage else "") + ".",
        f"Population proxy decision: {pop.get('decision', 'missing')} ({pop_source}).",
    ]
    caveats = [
        "Network B uses 2018 GTFS as a pre-VinBus conventional transit baseline; it is not current-service validation.",
        "Population raster is verified but not yet integrated into MAI magnitude weighting.",
        "Transit metrics use stop-level VinBus routing; full timetable routing remains a future upgrade.",
        "Google TWO_WHEELER bulk API remains unavailable/unconfirmed; validation uses manual Android consumer-app checks.",
        "Building footprints and WorldPop are used as audit layers, not yet as primary MAI weights.",
    ]
    if "Verdict: **PASS**" in gate_text:
        caveats.append("Overture POI gate passed; keep the user-confirmed spot-check CSV as audit trail for the merged primary POI layer.")
    else:
        caveats.append("Overture-only POIs remain unchecked; merged POI results are sensitivity only until >=70% are confirmed without systematic category error.")
    if vif_path.exists():
        vif = pd.read_csv(vif_path)
        high = vif[vif.get("flag_high_vif", False) == True]
        if not high.empty:
            parts = [f"{row['variable']}={float(row['VIF']):.2f}" for _, row in high.iterrows()]
            caveats.append("High VIF detected (" + ", ".join(parts) + "); report RAC_time-only sensitivity as robustness evidence.")

    lines = [
        "# Supervisor Memo: Ocean Park Pilot",
        "",
        "## Result Snapshot",
        f"- Grid cells: {int(float(summary.get('n_cells', len(metrics))))}",
        f"- Mean SMCI Scenario A: {float(summary.get('mean_SMCI_A', 0.0)):.4f}",
        f"- Mean SMCI Scenario B: {float(summary.get('mean_SMCI_B', 0.0)):.4f}",
        f"- Mean Delta_SMCI: {float(summary.get('mean_Delta_SMCI', 0.0)):.4f}",
        f"- Share improved: {float(summary.get('share_improved', 0.0)):.2%}",
    ]
    if delta:
        lines.append(
            "- Improved / unchanged / declined cells: "
            f"{delta.get('improved', {}).get('count', 0)} ({delta.get('improved', {}).get('share', 0.0):.2%}) / "
            f"{delta.get('unchanged', {}).get('count', 0)} ({delta.get('unchanged', {}).get('share', 0.0):.2%}) / "
            f"{delta.get('declined', {}).get('count', 0)} ({delta.get('declined', {}).get('share', 0.0):.2%})"
        )
    if distribution_note:
        lines.append(f"- Distribution note: {distribution_note}")
    lines += ["", "## Typology Counts, Scenario B"]
    lines += [f"- {label}: {count}" for label, count in typology_counts.items()]
    lines += ["", "## Confirmed Real Data"] + [f"- {item}" for item in confirmed]
    lines += ["", "## Inferred / Proxy Metrics"] + [f"- {item}" for item in inferred]
    lines += ["", "## Unresolved Caveats"] + [f"- {caveat}" for caveat in caveats]
    lines += [
        "",
        "## Next Decisions",
        "- Spot-check 55 Overture-only POIs and decide whether merged POIs can become primary.",
        "- Decide whether to integrate building/population/employment proxy into MAI weighting or label current MAI as proxy-level.",
        "- Use generated maps for supervisor review; final cartographic styling can come later.",
        "- Prepare supervisor review using pilot results plus explicit proxy limitations.",
    ]
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

