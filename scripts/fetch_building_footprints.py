"""
Fetch building footprints for the pilot study area.

Source: VIDA Source Cooperative — merged Google Open Buildings V3,
Microsoft GlobalML Footprints, OSM (GeoParquet/FlatGeobuf).
URL: s3://us-west-2.opendata.source.coop/vida/google-microsoft-osm-open-buildings/

Extracts bbox from pilot_grid.gpkg and clips to study area.
Filters to confidence >= 0.70 (Google Open Buildings V3 threshold).
Requires internet access — fails gracefully if unavailable.

Run (on a machine with internet access):
  pip install pyarrow fsspec s3fs
  python scripts/fetch_building_footprints.py

Output:
  data/raw/building_footprints.gpkg
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import box


VIDA_S3_BASE = (
    "s3://us-west-2.opendata.source.coop/vida/google-microsoft-osm-open-buildings"
    "/geoparquet/by_country/country_iso=VNM/"
)
MIN_CONFIDENCE = 0.70
FETCH_INSTRUCTIONS = """
To fetch building footprints manually:
  1. Install: pip install pyarrow fsspec s3fs
  2. Run this script on a machine with internet access.
  3. Alternative: download via VIDA Source Cooperative UI at
     https://source.coop/repositories/vida/google-microsoft-osm-open-buildings/
     Filter country=VNM, clip to bbox below, save as GeoParquet or GeoPackage.
"""


def get_study_bbox(grid_path: Path) -> tuple[float, float, float, float]:
    grid = gpd.read_file(grid_path)
    grid_wgs84 = grid.to_crs("EPSG:4326")
    bounds = grid_wgs84.total_bounds  # minx, miny, maxx, maxy
    # Add 500m buffer in degrees (~0.005°)
    return (
        round(bounds[0] - 0.005, 6),
        round(bounds[1] - 0.005, 6),
        round(bounds[2] + 0.005, 6),
        round(bounds[3] + 0.005, 6),
    )


def fetch_vida_buildings(
    bbox: tuple[float, float, float, float],
    output_path: Path,
    min_confidence: float = MIN_CONFIDENCE,
) -> gpd.GeoDataFrame:
    try:
        import pyarrow.dataset as ds
        import pyarrow.compute as pc
        import s3fs
        from shapely import wkb as shapely_wkb
    except ImportError:
        print("Missing dependencies. Install with:  pip install pyarrow s3fs")
        print(FETCH_INSTRUCTIONS)
        sys.exit(1)

    minx, miny, maxx, maxy = bbox
    # Strip s3:// prefix — s3fs expects bucket-path form
    s3_key = VIDA_S3_BASE.removeprefix("s3://") + "VNM.parquet"
    print(f"Fetching buildings for bbox: {bbox}")
    print(f"Source: s3://{s3_key}  (7.8 GB — using pyarrow bbox predicate pushdown)")

    try:
        import pyarrow.parquet as pq
        fs = s3fs.S3FileSystem(anon=True)
        with fs.open(s3_key, "rb") as fobj:
            pf = pq.ParquetFile(fobj)
            n_groups = pf.metadata.num_row_groups
            schema_names = pf.schema_arrow.names
            cols = [c for c in ["geometry", "confidence", "bf_source", "area_in_meters", "bbox"]
                    if c in schema_names]
            print(f"  Schema: {len(schema_names)} columns, {n_groups} row groups")
            print(f"  Scanning {n_groups} row groups for bbox {bbox} ...")

            chunks = []
            for i in range(n_groups):
                rg_meta = pf.metadata.row_group(i)
                stats = {}
                for col_idx in range(rg_meta.num_columns):
                    col = rg_meta.column(col_idx)
                    if col.statistics and col.statistics.has_min_max:
                        stats[col.path_in_schema] = (col.statistics.min, col.statistics.max)

                # Fast row-group skip using bbox statistics before downloading rows.
                if {"bbox.xmin", "bbox.xmax", "bbox.ymin", "bbox.ymax"}.issubset(stats):
                    xmin_min, _ = stats["bbox.xmin"]
                    _, xmax_max = stats["bbox.xmax"]
                    ymin_min, _ = stats["bbox.ymin"]
                    _, ymax_max = stats["bbox.ymax"]
                    if xmin_min > maxx or xmax_max < minx or ymin_min > maxy or ymax_max < miny:
                        if (i + 1) % 1000 == 0:
                            found = sum(len(c) for c in chunks)
                            print(f"  ... {i+1}/{n_groups} row groups scanned, {found} hits so far")
                        continue

                rg_df = pf.read_row_group(i, columns=cols).to_pandas()
                if "bbox" in rg_df.columns:
                    bbox_df = rg_df["bbox"].apply(pd.Series)
                    rg_df = rg_df[
                        (bbox_df.get("xmin", pd.Series([minx] * len(rg_df))).fillna(minx) <= maxx) &
                        (bbox_df.get("xmax", pd.Series([maxx] * len(rg_df))).fillna(maxx) >= minx) &
                        (bbox_df.get("ymin", pd.Series([miny] * len(rg_df))).fillna(miny) <= maxy) &
                        (bbox_df.get("ymax", pd.Series([maxy] * len(rg_df))).fillna(maxy) >= miny)
                    ]
                if "confidence" in rg_df.columns:
                    rg_df = rg_df[rg_df["confidence"] >= min_confidence]
                if len(rg_df) > 0:
                    chunks.append(rg_df)
                if (i + 1) % 1000 == 0 or len(rg_df) > 0:
                    found = sum(len(c) for c in chunks)
                    print(f"  ... {i+1}/{n_groups} row groups scanned, {found} hits so far")

        if not chunks:
            print("No buildings found within study area bbox.")
            return gpd.GeoDataFrame(columns=["geometry", "confidence"], crs="EPSG:4326")

        df = pd.concat(chunks, ignore_index=True)
        print(f"  Total {len(df)} buildings found")

    except Exception as exc:
        print(f"Fetch failed: {exc}")
        print(FETCH_INSTRUCTIONS)
        print(f"Study area bbox (WGS84): minx={minx}, miny={miny}, maxx={maxx}, maxy={maxy}")
        sys.exit(1)

    if len(df) == 0:
        print("No buildings found within study area bbox.")
        return gpd.GeoDataFrame(columns=["geometry", "confidence"], crs="EPSG:4326")

    def _parse_geom(g):
        if g is None:
            return None
        if isinstance(g, (bytes, bytearray)):
            try:
                return shapely_wkb.loads(bytes(g))
            except Exception:
                return None
        return g

    df["geometry"] = df["geometry"].apply(_parse_geom)
    buildings = gpd.GeoDataFrame(
        df, geometry="geometry", crs="EPSG:4326"
    ).dropna(subset=["geometry"])

    # Filter by confidence if column exists
    if "confidence" in buildings.columns:
        before = len(buildings)
        buildings = buildings[buildings["confidence"] >= min_confidence].copy()
        print(f"Confidence filter (>={min_confidence}): {before} → {len(buildings)} buildings")
    elif "confidence_score" in buildings.columns:
        before = len(buildings)
        buildings = buildings[buildings["confidence_score"] >= min_confidence].copy()
        print(f"Confidence filter (>={min_confidence}): {before} → {len(buildings)} buildings")

    # Standardise columns
    keep_cols = [c for c in ["geometry", "source", "confidence", "confidence_score", "full_plus_code"] if c in buildings.columns]
    buildings = buildings[keep_cols].copy()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    buildings.to_file(output_path, driver="GPKG")
    print(f"Wrote {len(buildings)} buildings to {output_path}")
    return buildings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--grid",       type=Path, default=Path("data/interim/pilot_grid.gpkg"))
    parser.add_argument("--output",     type=Path, default=Path("data/raw/building_footprints.gpkg"))
    parser.add_argument("--confidence", type=float, default=MIN_CONFIDENCE)
    args = parser.parse_args()

    if not args.grid.exists():
        raise FileNotFoundError(f"Grid not found: {args.grid}")

    bbox = get_study_bbox(args.grid)
    print(f"Study area bbox (WGS84, +500m buffer): {bbox}")
    fetch_vida_buildings(bbox, args.output, args.confidence)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
