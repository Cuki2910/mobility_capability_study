"""Write setup-status reports for the west Tay Mo / Smart City site config."""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.site_config import add_site_config_argument, load_site_config, print_resolved_paths


def _path_status(paths: dict[str, Path]) -> pd.DataFrame:
    rows = []
    for key, path in paths.items():
        rows.append({
            "key": key,
            "path": str(path),
            "exists": path.exists(),
            "size_bytes": path.stat().st_size if path.exists() and path.is_file() else None,
        })
    return pd.DataFrame(rows)


def _markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return ""
    cols = list(df.columns)
    lines = [
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join(["---"] * len(cols)) + " |",
    ]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in cols) + " |")
    return "\n".join(lines)


def _write_data_setup_report(config, output: Path) -> None:
    path_keys = [
        "paths.grid",
        "paths.walk_graph",
        "paths.drive_graph",
        "paths.osm_pois",
        "paths.overture_pois",
        "paths.merged_pois",
        "paths.landuse_poi_synthetic",
        "paths.merged_pois_economic",
        "paths.merged_pois_observed",
        "paths.building_footprints",
        "paths.worldpop_csv",
        "paths.accessibility_inputs",
        "paths.metrics",
    ]
    statuses = _path_status({
        key.removeprefix("paths."): config.path_value(key) for key in path_keys
    })
    lines = [
        "# West Tay Mo Data Setup Report",
        "",
        f"Generated UTC: {datetime.now(timezone.utc).isoformat()}",
        f"Site config: `{config.path}`",
        "",
        "## Seed Bbox",
        "",
        f"- Center: {config.get('center.lat')}, {config.get('center.lon')}",
        f"- Half box km: {config.get('center.half_box_km')}",
        f"- Bbox W/S/E/N: {config.bbox()}",
        "",
        "## Data Artifacts",
        "",
        _markdown_table(statuses),
        "",
        "## Gate Reminder",
        "",
        f"- Current opportunity basis: `{config.get('pipeline.default_opportunity_basis')}`.",
        "- `observed_strict` requires no `needs_source` rows in the observed-opportunity audit.",
        "- Boundary labels require Smart City and Tay Mo core boundary layers.",
    ]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _area_km2(path: Path) -> float | None:
    if not path.exists():
        return None
    layer = gpd.read_file(path)
    if layer.empty:
        return None
    return float(layer.to_crs(layer.estimate_utm_crs()).geometry.area.sum() / 1_000_000)


def _label_population_summary(labeled_path: Path, population_path: Path) -> pd.DataFrame:
    if not labeled_path.exists() or not population_path.exists():
        return pd.DataFrame(columns=["label", "cells", "population", "mean_population_per_cell"])
    labels = gpd.read_file(labeled_path)[["cell_id", "west_core_label"]]
    population = pd.read_csv(population_path, usecols=["cell_id", "pop_sum"])
    merged = labels.merge(population, on="cell_id", how="left", validate="one_to_one")
    grouped = merged.groupby("west_core_label", dropna=False)["pop_sum"].agg(["size", "sum", "mean"]).reset_index()
    return grouped.rename(columns={
        "west_core_label": "label", "size": "cells", "sum": "population", "mean": "mean_population_per_cell",
    })


def _write_matching_preflight(config, output: Path) -> None:
    planned_area = _area_km2(config.path_value("paths.smart_city_core_boundary"))
    organic_area = _area_km2(config.path_value("paths.tay_mo_core_boundary"))
    population = _label_population_summary(
        config.path_value("paths.labeled_grid"), config.path_value("paths.worldpop_csv")
    )
    population_rows = _markdown_table(population.round(3)) if not population.empty else "Data not available."
    area_status = "measured from boundary" if planned_area is not None and organic_area is not None else "unresolved boundary measurement"
    matching_path = config.path_value("paths.cbd_matching")
    if matching_path is not None and matching_path.exists():
        matching = pd.read_csv(matching_path)
        matching_rows = _markdown_table(matching[[
            "origin", "drive_distance_km", "ratio_to_ocean_park", "within_15pct_of_ocean_park",
        ]].round(4))
        candidates = matching.loc[matching["origin"].ne("ocean_park")]
        matching_status = (
            "PASS: both west candidate cores are within the preregistered +/-15% tolerance."
            if candidates["within_15pct_of_ocean_park"].all()
            else "MATCHING GATE FAILED: at least one west candidate core is outside the preregistered +/-15% tolerance."
        )
    else:
        matching_rows = "Not measured: a corridor-scale drive graph is required."
        matching_status = "unresolved: no corridor-scale CBD network-distance measurement."
    lines = [
        "# West Tay Mo Matching Preflight",
        "",
        f"Generated UTC: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Measured Local Context",
        "",
        "| Variable | Smart City core | Tay Mo core | Status |",
        "|---|---:|---:|---|",
        f"| Boundary area km2 | {planned_area:.3f} | {organic_area:.3f} | {area_status} |" if planned_area is not None and organic_area is not None else "| Boundary area km2 |  |  | unresolved boundary measurement |",
        f"| Network distance to Hoan Kiem |  |  | {matching_status} |",
        "",
        "## Network-Distance Matching",
        "",
        matching_rows,
        "",
        "## WorldPop by Core Label",
        "",
        population_rows,
        "",
        "## Next Protocol Step",
        "",
        "- Do not promote the current planned/organic pair if the +/-15% M1 gate fails.",
        "- Select a new control core or a pre-specified shifted bbox only with an explicit protocol update; do not tune the analysis results.",
    ]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_transit_supply_check(config, output: Path) -> None:
    gtfs_dir = Path("data/raw/vinbus_pseudo_gtfs_fixed")
    bbox = config.bbox()
    lines = [
        "# West Tay Mo Transit Supply Check",
        "",
        f"Generated UTC: {datetime.now(timezone.utc).isoformat()}",
        f"VinBus pseudo-GTFS dir: `{gtfs_dir}`",
        "",
    ]
    stops_path = gtfs_dir / "stops.txt"
    if not stops_path.exists():
        lines += [
            "Status: BLOCKED",
            "",
            "Reason: `stops.txt` not found in VinBus pseudo-GTFS directory.",
        ]
    else:
        stops = pd.read_csv(stops_path)
        lon_col = "stop_lon"
        lat_col = "stop_lat"
        west, south, east, north = bbox
        in_bbox = stops[
            stops[lon_col].between(west, east) & stops[lat_col].between(south, north)
        ] if {lon_col, lat_col} <= set(stops.columns) else pd.DataFrame()
        status = "PASS_CANDIDATE" if len(in_bbox) > 0 else "BLOCKED"
        lines += [
            f"Status: {status}",
            "",
            f"- Stops in west bbox: {len(in_bbox)}",
            f"- Total VinBus stops: {len(stops)}",
        ]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    add_site_config_argument(parser)
    args = parser.parse_args()
    if args.site_config is None:
        raise ValueError("--site-config is required for this report.")
    config = load_site_config(args.site_config)
    outputs = {
        "data_setup_report": config.path_value("paths.data_setup_report"),
        "matching_preflight": config.path_value("paths.matching_preflight"),
        "transit_supply_check": config.path_value("paths.transit_supply_check"),
    }
    if args.dry_run:
        print_resolved_paths("West setup report dry-run", outputs)
        return 0

    _write_data_setup_report(config, outputs["data_setup_report"])
    _write_matching_preflight(config, outputs["matching_preflight"])
    _write_transit_supply_check(config, outputs["transit_supply_check"])
    for name, path in outputs.items():
        print(f"Wrote {name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
