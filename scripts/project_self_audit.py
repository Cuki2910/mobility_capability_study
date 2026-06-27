"""Generate a self-audit and critique report for the Ocean Park pilot."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _exists(path: str) -> bool:
    return Path(path).exists()


def count_completed_spot_checks(path: Path) -> tuple[int, int, dict]:
    if not path.exists():
        return 0, 0, {}
    df = pd.read_csv(path)
    if "spot_check_status" not in df.columns:
        return len(df), 0, {}
    status = df["spot_check_status"].fillna("unchecked")
    complete = int((status != "unchecked").sum())
    breakdown = status.value_counts().to_dict()
    return len(df), complete, breakdown


def motorcycle_status(path: Path) -> dict:
    if not path.exists():
        return {"rows": 0, "android_completed": 0, "has_android_column": False}
    df = pd.read_csv(path)
    android_cols = [c for c in df.columns if c in {"google_maps_android_minutes", "android_motorcycle_minutes"}]
    if not android_cols:
        return {"rows": len(df), "android_completed": 0, "has_android_column": False}
    col = android_cols[0]
    completed_df = df[df[col].notna()].copy()
    out = {"rows": len(df), "android_completed": len(completed_df), "has_android_column": True}
    if not completed_df.empty and "abs_error_minutes" in completed_df.columns:
        errors = pd.to_numeric(completed_df["abs_error_minutes"], errors="coerce").dropna()
        if not errors.empty:
            out["mae_minutes"] = float(errors.abs().mean())
            out["bias_minutes"] = float(errors.mean())
    return out


def android_emulator_status(path: Path) -> dict:
    if not path.exists():
        return {"status_file": False, "installed": False, "motorcycle_mode_available": None}
    text = path.read_text(encoding="utf-8")
    return {
        "status_file": True,
        "installed": "Emulator boots" in text,
        "motorcycle_mode_available": False if "not currently provide a motorcycle-mode measurement" in text else None,
    }

def distribution_status() -> dict:
    path = Path("outputs/validation/zero_inflation_summary.csv")
    delta_path = Path("outputs/validation/delta_smci_groups.csv")
    out = {}
    if path.exists():
        zeros = pd.read_csv(path).set_index("metric")
        for metric in ["NAI", "SMCI_B"]:
            if metric in zeros.index:
                out[f"{metric}_zero_share"] = float(zeros.loc[metric, "share_zero"])
    if delta_path.exists():
        delta = pd.read_csv(delta_path).set_index("group")
        for group in ["improved", "unchanged", "declined"]:
            if group in delta.index:
                out[f"{group}_share"] = float(delta.loc[group, "share"])
    return out


def build_audit() -> dict:
    gtfs = _read_json(Path("data/interim/hanoi_gtfs_status.json"))
    pop = _read_json(Path("data/interim/population_proxy_resolution.json"))
    manifest = _read_json(Path("data/interim/pilot_data_manifest.json"))
    poi_total, poi_done, poi_breakdown = count_completed_spot_checks(Path("data/interim/poi_spot_check.csv"))
    moto = motorcycle_status(Path("outputs/validation/manual_motorcycle_validation_template.csv"))
    emulator = android_emulator_status(Path("outputs/validation/android_emulator_status.md"))
    dist = distribution_status()

    summary = pd.read_csv("outputs/pilot_summary.csv", index_col=0)["value"].to_dict() if _exists("outputs/pilot_summary.csv") else {}
    vif = pd.read_csv("outputs/validation/vif_flags.csv") if _exists("outputs/validation/vif_flags.csv") else pd.DataFrame()
    high_vif = bool(vif["flag_high_vif"].any()) if not vif.empty and "flag_high_vif" in vif else None
    pre_vinbus = bool(gtfs.get("pre_vinbus_baseline"))

    blockers = []
    warnings = []
    strengths = []

    if manifest.get("counts") and _exists("data/processed/pilot_metrics.csv"):
        strengths.append("End-to-end pilot pipeline has real OSM graph/POI/grid inputs and processed metrics.")
    if pop.get("resolution_source") == "raster_metadata" and pop.get("adequate_for_250m_pilot"):
        strengths.append("WorldPop raster is downloaded and resolution-verified against the 250m grid.")
    if high_vif is False:
        strengths.append("Current NAI/MAI/RAC VIF diagnostics are below threshold 5.")
    elif high_vif is True:
        warnings.append("MAI/RAC VIF diagnostics exceed threshold 5; report RAC_time-only sensitivity before trusting final typology claims.")
    if pre_vinbus:
        strengths.append("2018 Hanoi GTFS is documented as a deliberate pre-VinBus Network B baseline, not missing data.")
    if poi_done >= 20:
        strengths.append(f"POI spot-check completed: {poi_done}/{poi_total} records reviewed ({poi_breakdown}).")
    if moto.get("android_completed", 0) >= 10:
        mae = moto.get("mae_minutes")
        strengths.append(
            "Android motorcycle validation completed: 10/10 OD pairs"
            + (f"; MAE={mae:.2f} minutes." if mae is not None else ".")
        )
    building_ready = Path("data/interim/grid_building_footprints.gpkg").exists()
    overture_ready = Path("data/interim/merged_pois.gpkg").exists() and Path("outputs/poi_merge_summary.md").exists()
    gate_path = Path("outputs/validation/overture_gate_result.md")
    gate_text = gate_path.read_text(encoding="utf-8") if gate_path.exists() else ""
    overture_gate_pass = "Verdict: **PASS**" in gate_text
    if building_ready:
        strengths.append("Building footprints are fetched and aggregated by grid cell for built-cell masking and WorldPop cross-checks.")
    if overture_ready:
        strengths.append("Overture Places are fetched and merged with OSM POIs using source-agreement labels.")
    if Path("outputs/validation/built_population_zero_access.md").exists():
        strengths.append("Built/population zero-access audit is complete; zero inflation is checked against building footprints and WorldPop.")
    if overture_gate_pass:
        strengths.append("Overture POI gate passed; merged OSM+Overture POI layer is primary.")
    elif Path("outputs/validation/merged_poi_sensitivity.md").exists():
        strengths.append("Merged-POI sensitivity is complete and kept separate from the OSM-only primary specification.")
    if Path("outputs/validation/gtfs_catalog_check.md").exists():
        strengths.append("GTFS catalog check documents MobilityDatabase and TUMI/Datahub candidates without replacing the 2018 pre-VinBus baseline.")
    if Path("outputs/maps/README.md").exists():
        strengths.append("Quick-look maps and GIS layers are generated for supervisor review.")
    if Path("outputs/supervisor_package.md").exists():
        strengths.append("Supervisor review package index is available.")

    if gtfs.get("network_b_baseline_limited", True) and not pre_vinbus:
        blockers.append("Network B remains baseline-limited because current GTFS is missing or stale.")
    if poi_done < 20:
        blockers.append(f"POI manual spot-check incomplete: {poi_done}/{max(poi_total, 20)} records checked.")
    if moto.get("android_completed", 0) < 10:
        blockers.append(f"Android motorcycle validation incomplete: {moto.get('android_completed', 0)}/10 OD pairs measured.")
    if pop.get("resolution_source") == "raster_metadata":
        warnings.append("Population raster is verified but not yet integrated into MAI magnitude weighting.")
    if pre_vinbus:
        warnings.append("Network B uses a 2018 pre-VinBus GTFS vintage; report as baseline and sensitivity limitation, not current service.")
    if emulator.get("installed") and emulator.get("motorcycle_mode_available") is False:
        warnings.append("Android emulator lacks motorcycle mode; physical Android measurements are used instead.")
    if dist.get("SMCI_B_zero_share", 0.0) > 0.25:
        warnings.append(
            f"SMCI_B is zero-inflated ({dist['SMCI_B_zero_share']:.2%} zero cells); report percentile/rank maps and delta groups, not only absolute means."
        )
    if not building_ready:
        warnings.append("Building footprints are not yet aggregated; zero-access cells may include unbuilt lake/park/open-space cells and under-mapped built cells.")

    next_actions = [
        "Integrate building/WorldPop/nighttime-light/employment proxy into MAI magnitude weighting or downgrade the claim to proxy-level MAI.",
        "Report Network B as a 2018 pre-VinBus baseline and keep post-2021 GTFS as a sensitivity target if found.",
        "Proceed to supervisor review with pilot results and explicit proxy limitations.",
    ]
    if not building_ready:
        next_actions.insert(0, "Fetch and aggregate building footprints by grid cell; use them as built-cell mask and WorldPop cross-check.")
    if overture_gate_pass:
        next_actions.insert(0, "Preserve Overture gate audit trail and monitor merged POI layer for systematic errors.")
    elif overture_ready:
        next_actions.insert(0, "Spot-check Overture-only POIs before rerunning NAI/MAI with merged POIs.")
    else:
        next_actions.insert(0, "Add Overture Places as a POI supplement and source-agreement confidence layer.")

    return {
        "snapshot": {
            "grid_cells": int(summary.get("n_cells", manifest.get("counts", {}).get("grid_cells", 0)) or 0),
            "mean_SMCI_A": float(summary.get("mean_SMCI_A", 0.0) or 0.0),
            "mean_SMCI_B": float(summary.get("mean_SMCI_B", 0.0) or 0.0),
            "share_improved": float(summary.get("share_improved", 0.0) or 0.0),
            "gtfs_status": gtfs.get("status", "missing"),
            "pre_vinbus_baseline": pre_vinbus,
            "poi_spot_checks": {"total": poi_total, "completed": poi_done, "breakdown": poi_breakdown},
            "motorcycle_android_checks": moto,
            "android_emulator": emulator,
            "population_resolution": pop,
            "distribution_diagnostics": dist,
            "high_vif": high_vif,
            "built_population_zero_access_audit": Path("outputs/validation/built_population_zero_access.md").exists(),
            "merged_poi_sensitivity": Path("outputs/validation/merged_poi_sensitivity.md").exists(),
            "gtfs_catalog_check": Path("outputs/validation/gtfs_catalog_check.md").exists(),
        },
        "strengths": strengths,
        "blockers": blockers,
        "warnings": warnings,
        "next_actions": next_actions,
    }


def write_markdown(audit: dict, output: Path) -> None:
    lines = ["# Project Self-Audit", "", "## Snapshot", ""]
    for key, value in audit["snapshot"].items():
        lines.append(f"- {key}: {value}")
    for section in ("strengths", "blockers", "warnings", "next_actions"):
        title = section.replace("_", " ").title()
        lines += ["", f"## {title}", ""]
        lines += [f"- {item}" for item in audit[section]] or ["- None"]
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, default=Path("outputs/project_self_audit.json"))
    parser.add_argument("--md", type=Path, default=Path("outputs/project_self_audit.md"))
    args = parser.parse_args()

    audit = build_audit()
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(audit, args.md)
    print(json.dumps(audit, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
