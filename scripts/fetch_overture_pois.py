"""
Fetch Overture Maps Places for the pilot study area.

Source: Overture Maps Foundation — Places theme, accessed via DuckDB HTTPFS
from s3://overturemaps-us-west-2/release/<version>/theme=places/

Filters to relevant categories (food, retail, health, education, recreation)
within the study area bbox. Requires internet access and DuckDB with HTTPFS.

Run (on a machine with internet access):
  pip install duckdb geopandas
  python scripts/fetch_overture_pois.py

Output:
  data/raw/overture_pois.gpkg
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.site_config import add_site_config_argument, apply_site_config, print_resolved_paths

import geopandas as gpd
from shapely.geometry import box


# Overture Maps Places release — update version string as newer releases appear
OVERTURE_RELEASE = "2026-09-23.1"
OVERTURE_S3 = (
    f"s3://overturemaps-us-west-2/release/{OVERTURE_RELEASE}/theme=places/type=place/*"
)

# Categories relevant to NAI and MAI in this study
RELEVANT_CATEGORIES = {
    # Neighborhood (NAI) POI types
    "food_and_drink",
    "shopping",
    "health_care",
    "education",
    "sports_and_recreation",
    "community_and_government",
    # Metropolitan (MAI) opportunity types
    "financial_service",
    "professional_service",
    "travel_and_transportation",
}

FETCH_INSTRUCTIONS = """
To fetch Overture Places manually:
  1. Install: pip install duckdb geopandas
  2. Run on a machine with internet access:
       python scripts/fetch_overture_pois.py
  3. Alternative: use Overture's Explorer at https://explore.overturemaps.org/
     Filter to the study area, export as GeoJSON, then convert with geopandas.
"""


def get_study_bbox(grid_path: Path) -> tuple[float, float, float, float]:
    grid = gpd.read_file(grid_path)
    grid_wgs84 = grid.to_crs("EPSG:4326")
    bounds = grid_wgs84.total_bounds
    return (
        round(bounds[0] - 0.005, 6),
        round(bounds[1] - 0.005, 6),
        round(bounds[2] + 0.005, 6),
        round(bounds[3] + 0.005, 6),
    )


def fetch_overture_places(
    bbox: tuple[float, float, float, float],
    output_path: Path,
) -> gpd.GeoDataFrame:
    try:
        import duckdb
    except ImportError:
        print("Missing DuckDB. Install with:  pip install duckdb")
        print(FETCH_INSTRUCTIONS)
        sys.exit(1)

    minx, miny, maxx, maxy = bbox
    cat_filter = ", ".join(f"'{c}'" for c in sorted(RELEVANT_CATEGORIES))

    sql = f"""
    INSTALL httpfs; LOAD httpfs; INSTALL spatial; LOAD spatial;
    SET s3_region='us-west-2';

    SELECT
        id,
        names.primary AS name,
        CASE
            WHEN taxonomy.hierarchy[1] = 'shopping' THEN 'retail'
            WHEN taxonomy.hierarchy[1] = 'food_and_drink' THEN 'food_and_beverage'
            WHEN taxonomy.hierarchy[1] = 'health_care' THEN 'health_and_medical'
            WHEN taxonomy.hierarchy[1] = 'sports_and_recreation' THEN 'recreation'
            WHEN taxonomy.hierarchy[1] = 'community_and_government' THEN 'public_service'
            WHEN taxonomy.hierarchy[1] = 'travel_and_transportation' THEN 'transportation'
            WHEN list_contains(taxonomy.hierarchy, 'financial_service') THEN 'financial_service'
            WHEN list_contains(taxonomy.hierarchy, 'professional_service') THEN 'professional_service'
            ELSE taxonomy.hierarchy[1]
        END AS category,
        taxonomy.primary AS category_detail,
        confidence,
        bbox.xmin AS longitude,
        bbox.ymin AS latitude
    FROM read_parquet('{OVERTURE_S3}', hive_partitioning=1)
    WHERE
        bbox.xmin >= {minx} AND bbox.xmax <= {maxx}
        AND bbox.ymin >= {miny} AND bbox.ymax <= {maxy}
        AND (basic_category IN ({cat_filter}) OR list_has_any(taxonomy.hierarchy, [{cat_filter}]))
        AND confidence >= 0.5
    """

    print(f"Querying Overture Places from {OVERTURE_S3} ...")
    try:
        con = duckdb.connect()
        result = con.execute(sql).df()
    except Exception as exc:
        print(f"DuckDB query failed: {exc}")
        print(FETCH_INSTRUCTIONS)
        print(f"Study area bbox (WGS84): {bbox}")
        sys.exit(1)

    if len(result) == 0:
        print("No Overture Places found within study area.")
        return gpd.GeoDataFrame(columns=["geometry", "name", "category", "confidence"], crs="EPSG:4326")

    gdf = gpd.GeoDataFrame(
        result,
        geometry=gpd.points_from_xy(result["longitude"], result["latitude"]),
        crs="EPSG:4326",
    ).drop(columns=["longitude", "latitude"])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(output_path, driver="GPKG")
    print(f"Wrote {len(gdf)} Overture POIs to {output_path}")
    print(f"  Categories: {result['category'].value_counts().to_dict()}")
    return gdf


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    add_site_config_argument(parser)
    parser.add_argument("--grid",   type=Path, default=Path("data/interim/pilot_grid.gpkg"))
    parser.add_argument("--output", type=Path, default=Path("data/raw/overture_pois.gpkg"))
    parser.add_argument("--release", default=OVERTURE_RELEASE, help="Published Overture release identifier")
    args = parser.parse_args()
    global OVERTURE_S3
    import re
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}\.\d+", args.release):
        parser.error("--release must have the form YYYY-MM-DD.N")
    OVERTURE_S3 = f"s3://overturemaps-us-west-2/release/{args.release}/theme=places/type=place/*"
    config = apply_site_config(args, parser, {
        "grid": "paths.grid",
        "output": "paths.overture_pois",
    })

    if args.dry_run:
        values = {
            "site_id": config.site_id if config else "pilot",
            "grid": args.grid,
            "output": args.output,
        }
        values["bbox_west_south_east_north"] = (
            get_study_bbox(args.grid) if args.grid.exists() else "unavailable until grid exists"
        )
        print_resolved_paths("Overture fetch dry-run", values)
        return 0

    if not args.grid.exists():
        raise FileNotFoundError(f"Grid not found: {args.grid}")

    bbox = get_study_bbox(args.grid)
    print(f"Study area bbox (WGS84, +500m buffer): {bbox}")
    fetch_overture_places(bbox, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
