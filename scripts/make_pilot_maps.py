"""Create dependency-light pilot map artifacts (SVG + GeoPackage + GeoJSON)."""
from __future__ import annotations

import argparse
import html
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd


NUMERIC_LAYERS = ["NAI", "MAI_B", "RAC_B", "SMCI_B", "Delta_SMCI"]
TYPOLOGY_COLORS = {
    "Integrated Capability": "#1b9e77",
    "Fragmented Capability": "#d95f02",
    "Transit-Dependent": "#7570b3",
    "Motorcycle Lock-in": "#666666",
}
NUMERIC_COLORS = ["#f7fbff", "#c6dbef", "#6baed6", "#2171b5", "#08306b"]
ZERO_COLOR = "#e0e0e0"


def _project_point(x: float, y: float, bounds: tuple[float, float, float, float], width: int, height: int, pad: int) -> tuple[float, float]:
    minx, miny, maxx, maxy = bounds
    sx = (width - 2 * pad) / (maxx - minx)
    sy = (height - 2 * pad) / (maxy - miny)
    scale = min(sx, sy)
    xoff = (width - scale * (maxx - minx)) / 2
    yoff = (height - scale * (maxy - miny)) / 2
    px = xoff + (x - minx) * scale
    py = height - (yoff + (y - miny) * scale)
    return px, py


def _geom_paths(geom, bounds, width: int, height: int, pad: int) -> list[str]:
    geoms = list(geom.geoms) if geom.geom_type == "MultiPolygon" else [geom]
    paths = []
    for poly in geoms:
        coords = [_project_point(x, y, bounds, width, height, pad) for x, y in poly.exterior.coords]
        d = "M " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in coords) + " Z"
        paths.append(d)
    return paths


def _numeric_bins(values: pd.Series) -> tuple[list[float], pd.Series]:
    clean = pd.to_numeric(values, errors="coerce").fillna(0.0)
    bins = pd.Series(-1, index=clean.index, dtype="int64")
    positive = clean[clean > 0.0]
    if positive.empty:
        return [], bins
    if positive.nunique() <= 1:
        bins.loc[positive.index] = 0
        return [float(positive.min()), float(positive.max())], bins
    qs = np.quantile(positive, [0.2, 0.4, 0.6, 0.8])
    qs = np.unique(qs)
    bins.loc[positive.index] = np.searchsorted(qs, positive, side="right")
    bins = bins.clip(-1, len(NUMERIC_COLORS) - 1)
    return [float(q) for q in qs], bins

def _numeric_color(bin_id: int) -> str:
    if bin_id < 0:
        return ZERO_COLOR
    return NUMERIC_COLORS[bin_id]


def write_numeric_svg(gdf: gpd.GeoDataFrame, column: str, output: Path, width: int = 1200, height: int = 900) -> None:
    bounds = tuple(gdf.total_bounds)
    _, bins = _numeric_bins(gdf[column])
    paths = []
    for idx, row in gdf.iterrows():
        color = _numeric_color(int(bins.loc[idx]))
        label = f"cell {row['cell_id']}: {column}={row[column]:.4f}"
        for d in _geom_paths(row.geometry, bounds, width, height, 24):
            paths.append(f'<path d="{d}" fill="{color}" stroke="#ffffff" stroke-width="0.8"><title>{html.escape(label)}</title></path>')
    legend_items = [("Zero access", ZERO_COLOR)] + [(f"positive quantile {i + 1}", c) for i, c in enumerate(NUMERIC_COLORS)]
    legend = "".join(
        f'<rect x="40" y="{80 + i * 28}" width="22" height="18" fill="{c}"/><text x="72" y="{94 + i * 28}" font-size="16">{html.escape(label)}</text>'
        for i, (label, c) in enumerate(legend_items)
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" fill="#ffffff"/>
<g>{''.join(paths)}</g>
<text x="40" y="44" font-family="Arial" font-size="28" font-weight="700">{html.escape(column)}</text>
{legend}
</svg>
'''
    output.write_text(svg, encoding="utf-8")


def write_typology_svg(gdf: gpd.GeoDataFrame, output: Path, width: int = 1200, height: int = 900) -> None:
    bounds = tuple(gdf.total_bounds)
    paths = []
    for _, row in gdf.iterrows():
        label = str(row["typology_B"])
        color = TYPOLOGY_COLORS.get(label, "#cccccc")
        title = f"cell {row['cell_id']}: {label}"
        for d in _geom_paths(row.geometry, bounds, width, height, 24):
            paths.append(f'<path d="{d}" fill="{color}" stroke="#ffffff" stroke-width="0.8"><title>{html.escape(title)}</title></path>')
    legend = "".join(
        f'<rect x="40" y="{80 + i * 30}" width="22" height="18" fill="{color}"/><text x="72" y="{94 + i * 30}" font-size="16">{html.escape(label)}</text>'
        for i, (label, color) in enumerate(TYPOLOGY_COLORS.items())
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" fill="#ffffff"/>
<g>{''.join(paths)}</g>
<text x="40" y="44" font-family="Arial" font-size="28" font-weight="700">typology_B</text>
{legend}
</svg>
'''
    output.write_text(svg, encoding="utf-8")


def build_map_layer(grid_path: Path, metrics_path: Path) -> gpd.GeoDataFrame:
    grid = gpd.read_file(grid_path)
    metrics = pd.read_csv(metrics_path)
    return grid.merge(metrics, on="cell_id", how="left")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--grid", type=Path, default=Path("data/interim/pilot_grid.gpkg"))
    parser.add_argument("--metrics", type=Path, default=Path("data/processed/pilot_metrics.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/maps"))
    args = parser.parse_args()

    maps = build_map_layer(args.grid, args.metrics)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    maps.to_file(args.output_dir / "pilot_metrics_map.gpkg", driver="GPKG")
    maps.to_file(args.output_dir / "pilot_metrics_map.geojson", driver="GeoJSON")
    for column in NUMERIC_LAYERS:
        write_numeric_svg(maps, column, args.output_dir / f"{column}.svg")
    write_typology_svg(maps, args.output_dir / "typology_B.svg")

    lines = [
        "# Pilot Map Outputs",
        "",
        "Primary map layer: `pilot_metrics_map.gpkg` and `pilot_metrics_map.geojson`.",
        "",
        "SVG quick-look maps:",
    ]
    for name in [*NUMERIC_LAYERS, "typology_B"]:
        lines.append(f"- `{name}.svg`")
    (args.output_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote map artifacts to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
