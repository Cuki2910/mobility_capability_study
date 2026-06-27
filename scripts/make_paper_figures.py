"""Create paper-facing composite figures from pilot map and validation outputs."""
from __future__ import annotations

import argparse
import html
from pathlib import Path
import sys

import geopandas as gpd
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.make_pilot_maps import NUMERIC_COLORS, TYPOLOGY_COLORS, _geom_paths, _numeric_bins, _numeric_color, _project_point, build_map_layer
from src.routing import vinbus_corridor_from_overpass, vinbus_stops_from_overpass


def _svg_header(width: int, height: int) -> list[str]:
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">', '<rect width="100%" height="100%" fill="#ffffff"/>']


def _map_group(gdf: gpd.GeoDataFrame, column: str, x: int, y: int, width: int, height: int, typology: bool = False) -> str:
    local = gdf.to_crs(epsg=3857)
    bounds = tuple(local.total_bounds)
    parts = [f'<g transform="translate({x},{y})">', f'<text x="0" y="24" font-family="Arial" font-size="24" font-weight="700">{html.escape(column)}</text>']
    if typology:
        for _, row in local.iterrows():
            color = TYPOLOGY_COLORS.get(str(row[column]), "#cccccc")
            for d in _geom_paths(row.geometry, bounds, width, height, 12):
                parts.append(f'<path d="{d}" fill="{color}" stroke="#ffffff" stroke-width="0.7"/>')
    else:
        _, bins = _numeric_bins(local[column])
        for idx, row in local.iterrows():
            color = _numeric_color(int(bins.loc[idx]))
            for d in _geom_paths(row.geometry, bounds, width, height, 12):
                parts.append(f'<path d="{d}" fill="{color}" stroke="#ffffff" stroke-width="0.7"/>')
    parts.append("</g>")
    return "".join(parts)


def _line_path(line, bounds, width: int, height: int, pad: int = 24) -> str:
    coords = [_project_point(x, y, bounds, width, height, pad) for x, y in line.coords]
    return "M " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in coords)


def figure1_study_area(grid_path: Path, vinbus_json: Path, output: Path) -> None:
    width, height = 1200, 900
    grid = gpd.read_file(grid_path).to_crs(epsg=3857)
    corridor = vinbus_corridor_from_overpass(vinbus_json).to_crs(epsg=3857)
    stops = vinbus_stops_from_overpass(vinbus_json).to_crs(epsg=3857)
    minx, miny, maxx, maxy = grid.total_bounds
    # include nearby route context while keeping Ocean Park grid readable
    bounds = (minx - 1200, miny - 1200, maxx + 1200, maxy + 1200)
    parts = _svg_header(width, height)
    parts.append('<text x="42" y="48" font-family="Arial" font-size="30" font-weight="700">Figure 1. Study area, grid, VinBus routes and stops</text>')
    for _, row in grid.iterrows():
        for d in _geom_paths(row.geometry, bounds, width, height, 32):
            parts.append(f'<path d="{d}" fill="#f7f7f7" stroke="#d0d0d0" stroke-width="0.55"/>')
    for _, row in corridor.iterrows():
        geom = row.geometry
        lines = list(geom.geoms) if geom.geom_type == "MultiLineString" else [geom]
        for line in lines:
            parts.append(f'<path d="{_line_path(line, bounds, width, height, 32)}" fill="none" stroke="#d95f02" stroke-width="2.2" stroke-linecap="round" opacity="0.75"/>')
    for _, row in stops.iterrows():
        px, py = _project_point(row.geometry.x, row.geometry.y, bounds, width, height, 32)
        parts.append(f'<circle cx="{px:.2f}" cy="{py:.2f}" r="3.2" fill="#1b9e77" stroke="#ffffff" stroke-width="0.7"/>')
    parts.append('<rect x="42" y="790" width="310" height="72" fill="#ffffff" stroke="#bbbbbb"/>')
    parts.append('<line x1="62" y1="817" x2="112" y2="817" stroke="#d95f02" stroke-width="3"/><text x="126" y="823" font-size="18" font-family="Arial">VinBus route geometry</text>')
    parts.append('<circle cx="87" cy="847" r="5" fill="#1b9e77"/><text x="126" y="853" font-size="18" font-family="Arial">VinBus stop/platform</text>')
    parts.append("</svg>")
    output.write_text("\n".join(parts), encoding="utf-8")


def figure2_components(gdf: gpd.GeoDataFrame, output: Path) -> None:
    width, height = 1400, 1050
    parts = _svg_header(width, height)
    parts.append('<text x="42" y="48" font-family="Arial" font-size="30" font-weight="700">Figure 2. Accessibility components</text>')
    panels = [("NAI", 40, 70), ("MAI_B", 720, 70), ("RAC_B", 40, 560), ("SMCI_B", 720, 560)]
    for col, x, y in panels:
        parts.append(_map_group(gdf, col, x, y, 620, 440))
    parts.append("</svg>")
    output.write_text("\n".join(parts), encoding="utf-8")


def figure3_typology_delta(gdf: gpd.GeoDataFrame, output: Path) -> None:
    width, height = 1400, 720
    parts = _svg_header(width, height)
    parts.append('<text x="42" y="48" font-family="Arial" font-size="30" font-weight="700">Figure 3. Typology and Delta SMCI</text>')
    parts.append(_map_group(gdf, "typology_B", 40, 72, 620, 580, typology=True))
    parts.append(_map_group(gdf, "Delta_SMCI", 730, 72, 620, 580))
    y = 130
    for label, color in TYPOLOGY_COLORS.items():
        parts.append(f'<rect x="1050" y="{y}" width="20" height="16" fill="{color}"/><text x="1080" y="{y+14}" font-size="16" font-family="Arial">{html.escape(label)}</text>')
        y += 26
    parts.append("</svg>")
    output.write_text("\n".join(parts), encoding="utf-8")


def _bars(values: pd.Series, x: int, y: int, width: int, height: int, title: str) -> list[str]:
    max_v = float(values.max()) or 1.0
    parts = [f'<text x="{x}" y="{y}" font-family="Arial" font-size="24" font-weight="700">{html.escape(title)}</text>']
    bar_w = width / len(values)
    for i, (label, value) in enumerate(values.items()):
        h = float(value) / max_v * (height - 70)
        bx = x + i * bar_w + 10
        by = y + height - h - 30
        parts.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bar_w-20:.1f}" height="{h:.1f}" fill="#2171b5"/>')
        parts.append(f'<text x="{bx:.1f}" y="{y+height-8}" font-size="13" font-family="Arial" transform="rotate(0 {bx:.1f},{y+height-8})">{html.escape(str(label))}</text>')
        parts.append(f'<text x="{bx:.1f}" y="{by-6:.1f}" font-size="13" font-family="Arial">{float(value):.2f}</text>')
    return parts


def figure4_distribution(metrics_path: Path, population_path: Path, output: Path) -> None:
    width, height = 1400, 760
    metrics = pd.read_csv(metrics_path)
    parts = _svg_header(width, height)
    parts.append('<text x="42" y="48" font-family="Arial" font-size="30" font-weight="700">Figure 4. Distribution and population exposure</text>')
    hist = pd.cut(metrics["SMCI_B"], bins=np.linspace(0, max(metrics["SMCI_B"].max(), 0.001), 11), include_lowest=True).value_counts().sort_index()
    hist.index = [f"{iv.left:.2f}" for iv in hist.index]
    parts.extend(_bars(hist, 50, 95, 600, 270, "SMCI_B distribution"))
    counts = metrics["typology_B"].value_counts().reindex(TYPOLOGIES_FOR_FIG := list(TYPOLOGY_COLORS.keys()), fill_value=0)
    parts.extend(_bars(counts / len(metrics), 740, 95, 600, 270, "Cell share by typology"))
    if population_path.exists():
        pop = pd.read_csv(population_path)
        merged = metrics[["cell_id", "typology_B"]].merge(pop, on="cell_id", how="left")
        pop_col = "population" if "population" in merged.columns else "pop_sum"
        if pop_col in merged.columns and merged[pop_col].sum() > 0:
            shares = merged.groupby("typology_B")[pop_col].sum().reindex(TYPOLOGIES_FOR_FIG, fill_value=0) / merged[pop_col].sum()
            parts.extend(_bars(shares, 390, 430, 620, 250, "Population share by typology"))
    parts.append("</svg>")
    output.write_text("\n".join(parts), encoding="utf-8")


def write_captions(output: Path) -> None:
    captions = [
        "# Paper Figure Captions",
        "",
        "**Figure 1. Study area, analysis grid, and VinBus route/stop data.** The figure shows the 250 m Ocean Park grid, OSM VinBus route geometry, and extracted stop/platform nodes used in Network C.",
        "",
        "**Figure 2. Accessibility components.** NAI captures neighborhood walking access; MAI_B captures Scenario B metropolitan opportunity access; RAC_B captures walk/transit competitiveness relative to motorcycle; SMCI_B combines all three normalized components.",
        "",
        "**Figure 3. Scenario B typology and Delta SMCI.** Typology maps local accessibility against metropolitan competitiveness; Delta SMCI shows the Scenario B improvement over the pre-VinBus baseline under shared normalization bounds.",
        "",
        "**Figure 4. Distribution and population exposure.** The figure reports SMCI_B distribution, cell share by typology, and population share by typology using WorldPop aggregation.",
        "",
    ]
    output.write_text("\n".join(captions), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--grid", type=Path, default=Path("data/interim/pilot_grid.gpkg"))
    parser.add_argument("--metrics", type=Path, default=Path("data/processed/pilot_metrics.csv"))
    parser.add_argument("--vinbus", type=Path, default=Path("data/raw/vinbus_overpass_relations_geom.json"))
    parser.add_argument("--population", type=Path, default=Path("data/interim/grid_worldpop.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/figures"))
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    maps = build_map_layer(args.grid, args.metrics)
    figure1_study_area(args.grid, args.vinbus, args.output_dir / "figure1_study_area_routes_stops.svg")
    figure2_components(maps, args.output_dir / "figure2_accessibility_components.svg")
    figure3_typology_delta(maps, args.output_dir / "figure3_typology_delta.svg")
    figure4_distribution(args.metrics, args.population, args.output_dir / "figure4_distribution_population.svg")
    write_captions(args.output_dir / "figure_captions.md")
    print(f"Wrote paper figures to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
