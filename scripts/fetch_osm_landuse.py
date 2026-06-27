"""Fetch OSM landuse polygons (commercial/retail/industrial/office) for the pilot bbox.

Produces:
  data/raw/osm_landuse_polygons.gpkg   — raw OSM landuse features with area_m2
  data/interim/landuse_poi_synthetic.gpkg — centroids of landuse polygons,
      formatted as synthetic POI rows compatible with the merged_pois schema.

Run on a machine with internet access (Overpass/OSM):
  python scripts/fetch_osm_landuse.py

The synthetic POIs are then merged into the active POI layer via:
  python scripts/merge_economic_features.py
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

RAW_DIR = Path("data/raw")
INTERIM_DIR = Path("data/interim")

ECONOMIC_LANDUSE_TAGS = {
    "commercial": ("economic", 0.7),
    "retail":     ("economic", 0.5),
    "industrial": ("economic", 0.4),
    "office":     ("economic", 1.0),
}

OFFICE_TAGS = {
    # office=* values treated as economic POIs
    "company":      ("economic", 1.0),
    "government":   ("economic", 0.8),
    "ngo":          ("economic", 0.6),
    "educational":  ("higher_education", 0.7),
    "research":     ("economic", 0.8),
    "it":           ("economic", 1.0),
    "financial":    ("economic", 1.0),
    "insurance":    ("economic", 0.7),
    "telecommunication": ("economic", 0.7),
    "yes":          ("economic", 0.6),
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--center-lat", type=float, default=20.9930)
    parser.add_argument("--center-lon", type=float, default=105.9450)
    parser.add_argument("--half-box-km", type=float, default=2.5)
    parser.add_argument("--min-area-m2", type=float, default=500.0,
                        help="Minimum landuse polygon area to include (m²). Filters out tag errors.")
    parser.add_argument("--request-timeout", type=int, default=180)
    args = parser.parse_args()

    import geopandas as gpd
    import osmnx as ox
    import pandas as pd
    import numpy as np

    ox.settings.requests_timeout = args.request_timeout
    ox.settings.use_cache = True

    deg_per_km = 1 / 111
    west  = args.center_lon - args.half_box_km * deg_per_km
    east  = args.center_lon + args.half_box_km * deg_per_km
    south = args.center_lat - args.half_box_km * deg_per_km
    north = args.center_lat + args.half_box_km * deg_per_km

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)

    # --- Hướng B: landuse polygons ---
    print("Fetching landuse polygons (commercial/retail/industrial/office)...", flush=True)
    landuse_tags = {"landuse": list(ECONOMIC_LANDUSE_TAGS.keys())}
    try:
        landuse_gdf = ox.features_from_bbox(
            bbox=(west, south, east, north), tags=landuse_tags
        )
    except Exception as e:
        print(f"  landuse fetch failed: {e}")
        landuse_gdf = gpd.GeoDataFrame()

    # --- Hướng C: office=* nodes/polygons ---
    print("Fetching office=* features...", flush=True)
    office_tags = {"office": True}
    try:
        office_gdf = ox.features_from_bbox(
            bbox=(west, south, east, north), tags=office_tags
        )
    except Exception as e:
        print(f"  office fetch failed: {e}")
        office_gdf = gpd.GeoDataFrame()

    # --- Hướng C: amenity=bank/marketplace/post_office nodes ---
    print("Fetching amenity=bank/marketplace/post_office...", flush=True)
    amenity_econ_tags = {"amenity": ["bank", "marketplace", "post_office"]}
    try:
        amenity_econ_gdf = ox.features_from_bbox(
            bbox=(west, south, east, north), tags=amenity_econ_tags
        )
    except Exception as e:
        print(f"  amenity_econ fetch failed: {e}")
        amenity_econ_gdf = gpd.GeoDataFrame()

    # ---- Process landuse polygons → synthetic POIs ----
    synthetic_rows = []
    utm_crs = None

    if len(landuse_gdf) > 0:
        # Project to UTM for area calculation
        utm_crs = landuse_gdf.estimate_utm_crs()
        landuse_m = landuse_gdf.to_crs(utm_crs)
        # Keep only polygon geometries (not points/lines from OSM)
        poly_mask = landuse_m.geometry.geom_type.isin(["Polygon", "MultiPolygon"])
        landuse_poly = landuse_m[poly_mask].copy()
        landuse_poly["area_m2"] = landuse_poly.geometry.area
        # Filter tiny polygons (tag errors, road medians, etc.)
        landuse_poly = landuse_poly[landuse_poly["area_m2"] >= args.min_area_m2]
        print(f"  landuse polygons after area filter: {len(landuse_poly)}", flush=True)

        # Save raw polygons
        landuse_poly.to_crs("EPSG:4326").to_file(RAW_DIR / "osm_landuse_polygons.gpkg", driver="GPKG")

        for _, row in landuse_poly.iterrows():
            lu = str(row.get("landuse") or "").strip().lower()
            if lu not in ECONOMIC_LANDUSE_TAGS:
                continue
            domain, base_weight = ECONOMIC_LANDUSE_TAGS[lu]
            area = float(row["area_m2"])
            # Weight scales with sqrt(area) bounded to [0.3, 50.0]
            # sqrt dampens very large industrial zones from dominating
            weight = float(np.clip(np.sqrt(area / 1000.0), 0.3, 50.0))
            centroid_4326 = row.geometry.centroid
            # Convert centroid back to WGS84
            import geopandas as _gpd
            pt = _gpd.GeoSeries([centroid_4326], crs=utm_crs).to_crs("EPSG:4326").iloc[0]
            synthetic_rows.append({
                "name": row.get("name") or f"landuse_{lu}",
                "landuse": lu,
                "amenity": None,
                "shop": None,
                "office": None,
                "category": None,
                "source": "osm_landuse",
                "spot_check_priority": "medium",
                "_econ_domain": domain,
                "_econ_weight": weight,
                "building_area_m2": area,
                "geometry": pt,
            })
    else:
        print("  No landuse polygons found.", flush=True)

    # ---- Process office=* features ----
    if len(office_gdf) > 0:
        if utm_crs is None:
            utm_crs = office_gdf.estimate_utm_crs()
        office_m = office_gdf.to_crs(utm_crs)
        office_m["area_m2"] = office_m.geometry.apply(
            lambda g: g.area if g.geom_type in ("Polygon", "MultiPolygon") else 0.0
        )
        print(f"  office features: {len(office_m)}", flush=True)
        for _, row in office_m.iterrows():
            off_val = str(row.get("office") or "yes").strip().lower()
            domain, base_weight = OFFICE_TAGS.get(off_val, ("economic", 0.6))
            area = float(row["area_m2"])
            weight = float(np.clip(area / 1000.0, base_weight, 20.0)) if area > 0 else base_weight
            pt_4326 = gpd.GeoSeries([row.geometry.centroid], crs=utm_crs).to_crs("EPSG:4326").iloc[0]
            synthetic_rows.append({
                "name": row.get("name") or f"office_{off_val}",
                "landuse": None,
                "amenity": None,
                "shop": None,
                "office": off_val,
                "category": None,
                "source": "osm_office",
                "spot_check_priority": "medium",
                "_econ_domain": domain,
                "_econ_weight": weight,
                "building_area_m2": area if area > 0 else None,
                "geometry": pt_4326,
            })
    else:
        print("  No office features found.", flush=True)

    # ---- Process amenity=bank/marketplace ----
    if len(amenity_econ_gdf) > 0:
        if utm_crs is None:
            utm_crs = amenity_econ_gdf.estimate_utm_crs()
        amenity_m = amenity_econ_gdf.to_crs(utm_crs)
        print(f"  amenity economic features: {len(amenity_m)}", flush=True)
        for _, row in amenity_m.iterrows():
            am = str(row.get("amenity") or "").strip().lower()
            weight_map = {"bank": 0.6, "marketplace": 0.8, "post_office": 0.3}
            base_w = weight_map.get(am, 0.4)
            area = float(row.geometry.area) if row.geometry.geom_type in ("Polygon", "MultiPolygon") else 0.0
            weight = float(np.clip(area / 500.0, base_w, 10.0)) if area > 0 else base_w
            pt_4326 = gpd.GeoSeries([row.geometry.centroid], crs=utm_crs).to_crs("EPSG:4326").iloc[0]
            synthetic_rows.append({
                "name": row.get("name") or f"amenity_{am}",
                "landuse": None,
                "amenity": am,
                "shop": None,
                "office": None,
                "category": None,
                "source": "osm_amenity_econ",
                "spot_check_priority": "low",
                "_econ_domain": "economic",
                "_econ_weight": weight,
                "building_area_m2": area if area > 0 else None,
                "geometry": pt_4326,
            })
    else:
        print("  No amenity economic features found.", flush=True)

    if not synthetic_rows:
        print("No economic features found at all. Check bbox or OSM coverage.")
        return 1

    out = gpd.GeoDataFrame(synthetic_rows, geometry="geometry", crs="EPSG:4326")
    out_path = INTERIM_DIR / "landuse_poi_synthetic.gpkg"
    out.to_file(out_path, driver="GPKG")
    print(f"\nWrote {out_path} ({len(out)} synthetic economic POIs)")
    print(f"  domain distribution: {out['_econ_domain'].value_counts().to_dict()}")
    print(f"  source distribution: {out['source'].value_counts().to_dict()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
