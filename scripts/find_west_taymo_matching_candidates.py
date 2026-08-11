"""List organic-west grid origins that pass the fixed CBD-distance matching gate."""
from __future__ import annotations

import argparse
from pathlib import Path

import geopandas as gpd
import networkx as nx
import pandas as pd


def matching_bounds(reference_km: float, tolerance: float = 0.15) -> tuple[float, float]:
    """Return the inclusive preregistered CBD-distance acceptance band."""
    return reference_km * (1 - tolerance), reference_km * (1 + tolerance)


def rank_candidates(candidates: pd.DataFrame, reference_km: float) -> pd.DataFrame:
    """Keep and rank candidate origins without designating a replacement core."""
    lower, upper = matching_bounds(reference_km)
    result = candidates.loc[candidates["drive_distance_km"].between(lower, upper)].copy()
    result["ratio_to_ocean_park"] = result["drive_distance_km"] / reference_km
    result["absolute_distance_difference_km"] = (result["drive_distance_km"] - reference_km).abs()
    return result.sort_values(["absolute_distance_difference_km", "cell_id"]).reset_index(drop=True)


def _boundary_centroid(path: Path) -> tuple[float, float]:
    boundary = gpd.read_file(path).to_crs(epsg=4326)
    centroid = boundary.geometry.union_all().centroid
    return float(centroid.y), float(centroid.x)


def _route_distance_km(graph: nx.MultiDiGraph, origin_lat: float, origin_lon: float, cbd_node: int) -> float:
    import osmnx as ox

    origin_node = ox.distance.nearest_nodes(graph, X=origin_lon, Y=origin_lat)
    return float(nx.shortest_path_length(graph, origin_node, cbd_node, weight="length")) / 1000


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--grid", type=Path, default=Path("data/interim/west_taymo_labeled_grid.gpkg"))
    parser.add_argument("--graph", type=Path, default=Path("data/raw/cbd_matching_drive_network.graphml"))
    parser.add_argument("--ocean-park-boundary", type=Path, default=Path("data/interim/ocean_park_1_boundary.geojson"))
    parser.add_argument("--cbd-lat", type=float, default=21.0287)
    parser.add_argument("--cbd-lon", type=float, default=105.8524)
    parser.add_argument("--label", default="organic_west")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--output", type=Path, default=Path("outputs/west_taymo/matching_candidate_shortlist.csv"))
    args = parser.parse_args()
    if not args.graph.exists():
        raise FileNotFoundError(f"CBD matching graph is required: {args.graph}")

    import osmnx as ox

    grid = gpd.read_file(args.grid)
    candidates = grid.loc[grid["west_core_label"].eq(args.label)].copy()
    if candidates.empty:
        raise ValueError(f"No grid cells have west_core_label={args.label!r}")
    graph = ox.load_graphml(args.graph)
    cbd_node = ox.distance.nearest_nodes(graph, X=args.cbd_lon, Y=args.cbd_lat)
    ocean_lat, ocean_lon = _boundary_centroid(args.ocean_park_boundary)
    reference_km = _route_distance_km(graph, ocean_lat, ocean_lon, cbd_node)
    # Derive geometric origins in a local projected CRS before converting to WGS84.
    centroids = candidates.to_crs(epsg=32648).geometry.centroid.to_crs(epsg=4326)
    distances = [
        _route_distance_km(graph, point.y, point.x, cbd_node)
        for point in centroids
    ]
    table = pd.DataFrame(
        {
            "cell_id": candidates["cell_id"].to_numpy(),
            "candidate_lat": centroids.y.to_numpy(),
            "candidate_lon": centroids.x.to_numpy(),
            "drive_distance_km": distances,
        }
    )
    result = rank_candidates(table, reference_km).head(args.limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    lower, upper = matching_bounds(reference_km)
    print(f"Ocean Park reference: {reference_km:.3f} km; accepted band: {lower:.3f}-{upper:.3f} km")
    print(f"Wrote {len(result)} candidate grid origins to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
