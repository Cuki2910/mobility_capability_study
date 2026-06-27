"""Sensitivity: does the economic-domain enrichment change the typology partition?

Compares two POI layers through the full pipeline:
  - base161: the pre-enrichment merged POI layer (161 POIs, economic≈1)
  - econ208: the enriched layer (208 POIs, economic=32, higher_ed=70)

Reports typology Cohen's κ, Spearman ρ of SMCI_B, and cell relabel count, so we
can state whether the conclusions depend on the added economic POIs or are robust.

Run:
  python scripts/economic_inclusion_sensitivity.py

Output:
  outputs/validation/economic_inclusion_sensitivity.md
  outputs/validation/economic_inclusion_sensitivity.csv
"""
from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

BASE_POIS = Path("data/interim/merged_pois_base161.gpkg")
ECON_POIS = Path("data/interim/merged_pois.gpkg")
OUT_MD = Path("outputs/validation/economic_inclusion_sensitivity.md")
OUT_CSV = Path("outputs/validation/economic_inclusion_sensitivity.csv")

GRID = Path("data/interim/pilot_grid.gpkg")
WALK = Path("data/raw/pilot_walk_network.graphml")
DRIVE = Path("data/raw/pilot_drive_network.graphml")
VINBUS_GEOM = Path("data/raw/vinbus_overpass_relations_geom.json")
VINBUS_GTFS = Path("data/raw/vinbus_pseudo_gtfs_fixed")
SPEED_CSV = Path("data/raw/motorcycle_speed_calibration.csv")
GTFS_ZIP = Path("data/raw/hanoi_gtfs.zip")
BUILDINGS = Path("data/raw/building_footprints.gpkg")


def _run_pipeline(pois_path: Path):
    from src.accessibility_inputs import build_network_accessibility_inputs
    from src.pilot import compute_pilot_metrics

    inputs = build_network_accessibility_inputs(
        GRID,
        pois_path,
        WALK,
        DRIVE,
        vinbus_geometry_json=VINBUS_GEOM if VINBUS_GEOM.exists() else None,
        gtfs_zip=GTFS_ZIP if GTFS_ZIP.exists() else None,
        gtfs_status="baseline_limited",
        walk_cutoff_min=800.0 / 80.0,
        motorcycle_cutoff_min=3000.0 / 250.0,
        speed_factor_csv=SPEED_CSV if SPEED_CSV.exists() else None,
        headway_min=15.0,
        vinbus_mode="stops",
        bus_speed_kph=20.0,
        vinbus_gtfs_dir=VINBUS_GTFS if (VINBUS_GTFS / "stops.txt").exists() else None,
        buildings_path=BUILDINGS,
    )
    return compute_pilot_metrics(inputs)


def main() -> int:
    import pandas as pd
    from sklearn.metrics import cohen_kappa_score
    from scipy.stats import spearmanr

    if not BASE_POIS.exists():
        print(f"Error: {BASE_POIS} not found (pre-enrichment base layer). "
              "Reconstruct it from sources osm_only/overture_only/both first.")
        return 1

    print("Running pipeline on base161 (pre-enrichment)...", flush=True)
    base = _run_pipeline(BASE_POIS).sort_values("cell_id").reset_index(drop=True)
    print("Running pipeline on econ208 (enriched)...", flush=True)
    econ = _run_pipeline(ECON_POIS).sort_values("cell_id").reset_index(drop=True)

    kappa = float(cohen_kappa_score(base["typology_B"], econ["typology_B"]))
    rho_smci = float(spearmanr(base["SMCI_B"], econ["SMCI_B"]).correlation)
    rho_mai = float(spearmanr(base["MAI_B"], econ["MAI_B"]).correlation)
    relabelled = int((base["typology_B"].values != econ["typology_B"].values).sum())

    diff = pd.DataFrame({
        "cell_id": base["cell_id"],
        "typology_base161": base["typology_B"],
        "typology_econ208": econ["typology_B"],
        "SMCI_B_base161": base["SMCI_B"].round(5),
        "SMCI_B_econ208": econ["SMCI_B"].round(5),
        "relabelled": base["typology_B"].values != econ["typology_B"].values,
    })
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    diff.to_csv(OUT_CSV, index=False, encoding="utf-8")

    lines = [
        "# Economic-Domain Inclusion Sensitivity",
        "",
        "Does the conclusion depend on the 47 economic POIs added in Decision #18?",
        "Compares the full pipeline on the pre-enrichment 161-POI layer vs the enriched",
        "208-POI layer.",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Typology Cohen's κ (base161 vs econ208) | {kappa:.4f} |",
        f"| Spearman ρ SMCI_B | {rho_smci:.4f} |",
        f"| Spearman ρ MAI_B | {rho_mai:.4f} |",
        f"| Cells relabelled | {relabelled} / {len(base)} ({100*relabelled/len(base):.1f}%) |",
        "",
        "## Typology distribution shift",
        "",
        "| Typology | base161 | econ208 |",
        "|---|---|---|",
    ]
    b_counts = base["typology_B"].value_counts()
    e_counts = econ["typology_B"].value_counts()
    for typ in sorted(set(b_counts.index) | set(e_counts.index)):
        lines.append(f"| {typ} | {int(b_counts.get(typ, 0))} | {int(e_counts.get(typ, 0))} |")

    interp = (
        "Conclusions are **robust** to the economic enrichment: the typology partition is "
        "near-identical (κ close to 1)."
        if kappa >= 0.8 else
        "The economic enrichment **materially shifts** the typology partition (κ < 0.8). "
        "This is expected — it corrects a previously near-empty economic domain — and should "
        "be reported as a methodological improvement, with the enriched layer as primary."
    )
    lines += ["", "## Interpretation", "", interp, ""]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"\nWrote {OUT_MD} and {OUT_CSV}")
    print(f"  kappa={kappa:.4f}  rho(SMCI_B)={rho_smci:.4f}  relabelled={relabelled}/{len(base)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
