"""Write setup-status reports for the west Tay Mo / Smart City site config."""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

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
        "- Run proxy mode first (`pipeline.default_opportunity_basis=proxy`).",
        "- Promote `observed_strict` only after `observed_audit` has `needs_source=0`.",
        "- Boundary labels require Smart City and Tay Mo core boundary layers.",
    ]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_matching_preflight(config, output: Path) -> None:
    lines = [
        "# West Tay Mo Matching Preflight",
        "",
        f"Generated UTC: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Seed Values To Verify",
        "",
        "| Variable | Candidate A | Candidate B | Status |",
        "|---|---:|---:|---|",
        f"| Tay Mo area km2 | {config.get('seeds.tay_mo_area_km2_a')} | {config.get('seeds.tay_mo_area_km2_b')} | unresolved seed conflict |",
        f"| Tay Mo population | {config.get('seeds.tay_mo_population_a')} | {config.get('seeds.tay_mo_population_b')} | unresolved seed conflict |",
        f"| Smart City area ha | {config.get('seeds.smart_city_area_ha')} |  | seed; verify against boundary area |",
        "",
        "## Required Measurements",
        "",
        "- OSM drive-network distance from Smart City centroid to Hoan Kiem.",
        "- OSM drive-network distance from Tay Mo core centroid to Hoan Kiem.",
        "- WorldPop total and density distribution by labeled core.",
        "- Planned/organic boundary separability using `scripts/label_site_cells.py`.",
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
