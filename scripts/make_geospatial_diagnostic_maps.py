"""Render LISA and boundary-permeability maps from generated diagnostics."""
from __future__ import annotations

import argparse
from pathlib import Path

import geopandas as gpd

COLORS = {
    "High-High": "#b2182b",
    "Low-Low": "#2166ac",
    "High-Low": "#ef8a62",
    "Low-High": "#67a9cf",
    "Not Significant": "#d9d9d9",
}


def _project(point, bounds, width, height, padding):
    min_x, min_y, max_x, max_y = bounds
    scale = min((width - 2 * padding) / (max_x - min_x), (height - 2 * padding) / (max_y - min_y))
    return padding + (point[0] - min_x) * scale, height - padding - (point[1] - min_y) * scale


def _rings(geometry):
    if geometry.geom_type == "Polygon":
        return [geometry.exterior]
    if geometry.geom_type == "MultiPolygon":
        return [part.exterior for part in geometry.geoms]
    if geometry.geom_type == "LineString":
        return [geometry]
    if geometry.geom_type == "MultiLineString":
        return list(geometry.geoms)
    return []


def _svg_path(geometry, bounds, width, height, padding):
    paths = []
    for ring in _rings(geometry):
        points = [_project(point, bounds, width, height, padding) for point in ring.coords]
        paths.append("M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in points))
    return " ".join(paths)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lisa", type=Path, default=Path("outputs/results/spatial_autocorrelation_cells.gpkg"))
    parser.add_argument("--crossings", type=Path, default=Path("outputs/results/boundary_permeability_crossings.gpkg"))
    parser.add_argument("--boundary", type=Path, default=Path("data/interim/ocean_park_1_boundary.geojson"))
    parser.add_argument("--output", type=Path, default=Path("outputs/figures/geospatial_diagnostics.svg"))
    args = parser.parse_args()
    cells = gpd.read_file(args.lisa).to_crs("EPSG:4326")
    crossings = gpd.read_file(args.crossings).to_crs(cells.crs)
    boundary = gpd.read_file(args.boundary).to_crs(cells.crs)
    cluster_column = "SMCI_B__queen__cluster"
    if cluster_column not in cells:
        raise ValueError(f"missing LISA cluster column: {cluster_column}")
    width, height, padding = 1400, 760, 24
    bounds = tuple(cells.total_bounds)
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#faf8f2"/>',
        '<text x="32" y="46" font-family="Georgia" font-size="28" font-weight="700">Ocean Park Spatial Diagnostics</text>',
        '<text x="32" y="75" font-family="Georgia" font-size="17">LISA identifies statistically significant spatial association; crossings show modeled network topology.</text>',
        '<text x="32" y="112" font-family="Georgia" font-size="21" font-weight="700">SMCI_B LISA (Queen, FDR corrected)</text>',
        '<text x="742" y="112" font-family="Georgia" font-size="21" font-weight="700">Mapped boundary crossings</text>',
    ]
    for _, row in cells.iterrows():
        path = _svg_path(row.geometry, bounds, 620, 560, padding)
        color = COLORS.get(row[cluster_column], COLORS["Not Significant"])
        lines.append(f'<path d="{path}" transform="translate(8,130)" fill="{color}" stroke="#ffffff" stroke-width="0.3"/>')
    for geometry in boundary.geometry:
        path = _svg_path(geometry.boundary, bounds, 620, 560, padding)
        lines.append(f'<path d="{path}" transform="translate(8,130)" fill="none" stroke="#111111" stroke-width="1.2"/>')
    for _, row in crossings.iterrows():
        path = _svg_path(row.geometry, bounds, 620, 560, padding)
        color = "#238b45" if row["mode"] == "walking" else "#756bb1"
        lines.append(f'<path d="{path}" transform="translate(718,130)" fill="none" stroke="{color}" stroke-width="1.2" opacity="0.8"/>')
    for geometry in boundary.geometry:
        path = _svg_path(geometry.boundary, bounds, 620, 560, padding)
        lines.append(f'<path d="{path}" transform="translate(718,130)" fill="none" stroke="#111111" stroke-width="1.2"/>')
    legend = [("High-High", COLORS["High-High"]), ("Low-Low", COLORS["Low-Low"]), ("Not Significant", COLORS["Not Significant"]), ("Walking", "#238b45"), ("Motorcycle", "#756bb1")]
    for index, (label, color) in enumerate(legend):
        x = 34 + index * 180
        lines.extend([f'<rect x="{x}" y="718" width="18" height="12" fill="{color}"/>',
                      f'<text x="{x + 24}" y="729" font-family="Georgia" font-size="14">{label}</text>'])
    lines.append("</svg>")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
