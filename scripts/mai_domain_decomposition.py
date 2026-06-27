"""Diagnostic: decompose MAI_motorcycle into per-domain contributions.

After Decision #18 the economic domain holds real OSM landuse/office POIs. This
script quantifies how much each opportunity domain (economic, higher_education,
tertiary_healthcare, metro_commercial) actually contributes to the metropolitan
access score, so we can show the economic domain is no longer invisible.

Uses the motorcycle network (the densest reachability) as the decomposition base,
which is also the RAC_opp denominator — the domain that the economic enrichment
most directly feeds.

Run:
  python scripts/mai_domain_decomposition.py

Output:
  outputs/validation/mai_domain_decomposition.md
  outputs/validation/mai_domain_decomposition.csv
"""
from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

GRID = Path("data/interim/pilot_grid.gpkg")
POIS = Path("data/interim/merged_pois.gpkg")
DRIVE = Path("data/raw/pilot_drive_network.graphml")
SPEED_CSV = Path("data/raw/motorcycle_speed_calibration.csv")
OUT_MD = Path("outputs/validation/mai_domain_decomposition.md")
OUT_CSV = Path("outputs/validation/mai_domain_decomposition.csv")


def main() -> int:
    import geopandas as gpd
    import numpy as np
    import pandas as pd
    from src.accessibility_inputs import classify_poi_opportunity_domain
    from src.routing import (
        load_timed_graph, nearest_graph_nodes, composite_mai_from_graph,
    )
    from src.accessibility import MAI_DOMAIN_WEIGHTS

    grid = gpd.read_file(GRID)
    pois = gpd.read_file(POIS)

    # Build POI point layer + classify
    poi_points = pois.geometry.representative_point()
    poi_gdf = gpd.GeoDataFrame(pois.drop(columns="geometry", errors="ignore"),
                               geometry=poi_points, crs="EPSG:4326")
    classifications = [classify_poi_opportunity_domain(r) for _, r in pois.iterrows()]
    poi_domains = [d for d, _ in classifications]
    poi_weights = [w for _, w in classifications]

    grid_points = grid.geometry.representative_point()
    grid_gdf = gpd.GeoDataFrame(grid[["cell_id"]].copy(), geometry=grid_points, crs="EPSG:4326")

    drive_graph, drive_weight = load_timed_graph(DRIVE, "motorcycle",
                                                 speed_factor_csv=SPEED_CSV if SPEED_CSV.exists() else None)
    grid_nodes = nearest_graph_nodes(drive_graph, grid_gdf)
    poi_nodes = nearest_graph_nodes(drive_graph, poi_gdf)

    mai, contribs = composite_mai_from_graph(
        drive_graph, grid_nodes, poi_nodes, poi_domains, poi_weights, drive_weight,
        domain_weights=MAI_DOMAIN_WEIGHTS["default"], return_per_domain=True,
    )

    # Per-cell table
    df = pd.DataFrame({"cell_id": grid["cell_id"].values, "MAI_moto": mai})
    for domain, arr in contribs.items():
        df[f"contrib_{domain}"] = arr
    df.to_csv(OUT_CSV, index=False, encoding="utf-8")

    # Aggregate share of total MAI mass per domain
    total_mass = float(mai.sum()) if mai.sum() > 0 else 1.0
    shares = {d: float(arr.sum()) / total_mass for d, arr in contribs.items()}
    # Cells where each domain is the dominant contributor
    contrib_matrix = np.vstack([contribs[d] for d in contribs]) if contribs else np.zeros((1, len(mai)))
    domain_order = list(contribs.keys())
    dominant = [domain_order[i] for i in contrib_matrix.argmax(axis=0)] if contribs else []
    from collections import Counter
    dominant_counts = Counter(dominant)

    lines = [
        "# MAI Domain Decomposition (motorcycle network)",
        "",
        "How much each opportunity domain contributes to the metropolitan access score,",
        "after the economic-domain enrichment (Decision #18).",
        "",
        "## Share of total MAI mass by domain",
        "",
        "| Domain | Share of MAI mass | Dominant in N cells |",
        "|---|---|---|",
    ]
    for d in sorted(shares, key=lambda x: -shares[x]):
        lines.append(f"| {d} | {100*shares[d]:.1f}% | {dominant_counts.get(d, 0)} |")
    lines += [
        "",
        f"Total cells: {len(mai)}; cells with MAI_moto > 0: {(mai > 0).sum()}.",
        "",
        "## Interpretation",
        "",
        "Before enrichment the economic domain carried ~one POI, so its share of MAI mass",
        "was effectively zero. A non-trivial economic share here confirms the domain now",
        "contributes real signal rather than being a placeholder weight.",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_MD} and {OUT_CSV}")
    print("Domain shares:", {d: round(100*s, 1) for d, s in shares.items()})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
