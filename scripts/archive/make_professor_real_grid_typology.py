"""Create professor-facing real-data grid typology figure for Ocean Park."""
from __future__ import annotations

import html
from pathlib import Path
import sys

import geopandas as gpd
import osmnx as ox
import pandas as pd
from shapely.geometry import LineString, box

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.make_pilot_maps import TYPOLOGY_COLORS, _geom_paths, _project_point
from src.routing import vinbus_corridor_from_overpass, vinbus_stops_from_overpass


WIDTH = 980
HEIGHT = 620
PAD = 46


def _line_path(line: LineString, bounds: tuple[float, float, float, float]) -> str:
    coords = [_project_point(x, y, bounds, WIDTH, HEIGHT, PAD) for x, y in line.coords]
    return "M " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in coords)


def _lines(geom):
    if geom.is_empty:
        return []
    if geom.geom_type == "LineString":
        return [geom]
    if geom.geom_type == "MultiLineString":
        return list(geom.geoms)
    return []


def build_svg(
    grid_path: Path,
    metrics_path: Path,
    drive_graph_path: Path,
    vinbus_path: Path,
) -> str:
    grid = gpd.read_file(grid_path).merge(pd.read_csv(metrics_path), on="cell_id", how="left").to_crs(epsg=3857)
    minx, miny, maxx, maxy = grid.total_bounds
    bounds = (minx - 650, miny - 650, maxx + 650, maxy + 650)
    extent = box(*bounds)

    graph = ox.load_graphml(drive_graph_path)
    _, edges = ox.graph_to_gdfs(graph)
    roads = edges.to_crs(epsg=3857)
    roads = roads[roads.geometry.intersects(extent)]

    corridor = vinbus_corridor_from_overpass(vinbus_path).to_crs(epsg=3857)
    corridor = corridor[corridor.geometry.intersects(extent)]
    stops = vinbus_stops_from_overpass(vinbus_path).to_crs(epsg=3857)
    stops = stops[stops.geometry.intersects(extent)]

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
        '<rect width="100%" height="100%" fill="#f8fafc"/>',
        '<text x="40" y="38" font-family="Arial" font-size="25" font-weight="700" fill="#111827">Figure A. Ocean Park: lưới 250 m, đường thật và typology</text>',
        '<text x="40" y="66" font-family="Arial" font-size="14" fill="#4b5563">Nền đường lấy từ OSM pilot road network; tuyến và điểm dừng VinBus lấy từ Overpass; màu ô là typology Scenario B.</text>',
    ]

    parts.append("<g>")
    for _, row in roads.iterrows():
        for line in _lines(row.geometry):
            try:
                parts.append(
                    f'<path d="{_line_path(line, bounds)}" fill="none" stroke="#cbd5e1" stroke-width="1.15" stroke-linecap="round" opacity="0.85"/>'
                )
            except (ValueError, AttributeError):
                continue
    parts.append("</g>")

    parts.append("<g>")
    for _, row in grid.iterrows():
        color = TYPOLOGY_COLORS.get(str(row["typology_B"]), "#cccccc")
        title = f"cell {row['cell_id']}: {row['typology_B']}"
        for d in _geom_paths(row.geometry, bounds, WIDTH, HEIGHT, PAD):
            parts.append(
                f'<path d="{d}" fill="{color}" fill-opacity="0.68" stroke="#ffffff" stroke-width="0.75"><title>{html.escape(title)}</title></path>'
            )
    parts.append("</g>")

    parts.append("<g>")
    for _, row in corridor.iterrows():
        for line in _lines(row.geometry):
            parts.append(f'<path d="{_line_path(line, bounds)}" fill="none" stroke="#ffffff" stroke-width="5.8" stroke-linecap="round" opacity="0.9"/>')
            parts.append(f'<path d="{_line_path(line, bounds)}" fill="none" stroke="#0284c7" stroke-width="3.2" stroke-linecap="round" opacity="0.92"/>')
    for _, row in stops.iterrows():
        px, py = _project_point(row.geometry.x, row.geometry.y, bounds, WIDTH, HEIGHT, PAD)
        parts.append(f'<circle cx="{px:.2f}" cy="{py:.2f}" r="3.2" fill="#f97316" stroke="#ffffff" stroke-width="1.1"/>')
    parts.append("</g>")

    # Labels/callouts anchored on real geometry area, intentionally schematic in wording.
    parts.extend(
        [
            '<rect x="54" y="84" width="204" height="32" rx="4" fill="#ffffff" stroke="#94a3b8" opacity="0.96"/>',
            '<text x="68" y="105" font-family="Arial" font-size="13" font-weight="700" fill="#111827">Vinhomes Ocean Park grid</text>',
            '<rect x="54" y="124" width="204" height="72" rx="4" fill="#ffffff" stroke="#cbd5e1" opacity="0.96"/>',
            '<text x="68" y="148" font-family="Arial" font-size="13" font-weight="700" fill="#111827">How to read</text>',
            '<text x="68" y="169" font-family="Arial" font-size="12" fill="#374151">Color = mobility typology</text>',
            '<text x="68" y="187" font-family="Arial" font-size="12" fill="#374151">Blue = VinBus route; orange = stop</text>',
        ]
    )

    legend_x = 710
    legend_y = 98
    parts.extend(
        [
            f'<rect x="{legend_x}" y="{legend_y}" width="230" height="268" rx="8" fill="#ffffff" stroke="#cbd5e1" opacity="0.97"/>',
            f'<text x="{legend_x + 16}" y="{legend_y + 28}" font-family="Arial" font-size="17" font-weight="700" fill="#111827">Legend</text>',
        ]
    )
    y = legend_y + 55
    for label, color in TYPOLOGY_COLORS.items():
        parts.append(f'<rect x="{legend_x + 16}" y="{y - 15}" width="20" height="20" fill="{color}" fill-opacity="0.75"/>')
        parts.append(f'<text x="{legend_x + 46}" y="{y}" font-family="Arial" font-size="13" fill="#111827">{html.escape(label)}</text>')
        y += 31
    parts.extend(
        [
            f'<line x1="{legend_x + 16}" y1="{y + 10}" x2="{legend_x + 70}" y2="{y + 10}" stroke="#0284c7" stroke-width="3.5"/>',
            f'<text x="{legend_x + 86}" y="{y + 15}" font-family="Arial" font-size="13" fill="#111827">VinBus route</text>',
            f'<circle cx="{legend_x + 43}" cy="{y + 40}" r="5" fill="#f97316" stroke="#ffffff" stroke-width="1"/>',
            f'<text x="{legend_x + 86}" y="{y + 45}" font-family="Arial" font-size="13" fill="#111827">VinBus stop</text>',
            f'<line x1="{legend_x + 16}" y1="{y + 70}" x2="{legend_x + 70}" y2="{y + 70}" stroke="#94a3b8" stroke-width="2"/>',
            f'<text x="{legend_x + 86}" y="{y + 75}" font-family="Arial" font-size="13" fill="#111827">Road network</text>',
        ]
    )

    parts.extend(
        [
            '<rect x="704" y="402" width="236" height="82" rx="8" fill="#ffffff" stroke="#cbd5e1" opacity="0.97"/>',
            '<text x="720" y="428" font-family="Arial" font-size="13" font-weight="700" fill="#111827">Logic</text>',
            '<text x="720" y="450" font-family="Arial" font-size="12" fill="#374151">NAI high/low + MCS high/low</text>',
            '<text x="720" y="469" font-family="Arial" font-size="12" fill="#374151">MCS = sqrt(MAI × RAC)</text>',
            '<text x="40" y="596" font-family="Arial" font-size="11" fill="#64748b">Sources: OSM road graph, Overpass VinBus route geometry/stops, pilot 250 m grid.</text>',
            "</svg>",
        ]
    )
    return "\n".join(parts)


def main() -> int:
    output = Path("outputs/figures/professor_schematic_1_grid_typology.svg")
    svg = build_svg(
        Path("data/interim/pilot_grid.gpkg"),
        Path("data/processed/pilot_metrics.csv"),
        Path("data/raw/pilot_drive_network.graphml"),
        Path("data/raw/vinbus_overpass_relations_geom.json"),
    )
    output.write_text(svg, encoding="utf-8")
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
