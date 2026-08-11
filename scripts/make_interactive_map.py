"""
Interactive HTML map — Vinhomes Ocean Park mobility capability study.
Single self-contained HTML (Leaflet.js + embedded GeoJSON).

Fixes applied (v2):
  1. Stops filtered to exact grid bbox (not loose ±0.02 buffer)
  2. Study area boundary drawn from grid union/convex hull
  3. Scale bar (Leaflet built-in) + clean attribution
  4. Continuous legend: mini histogram + metric units/description
"""

import json
import csv
import math
import os
import io
import zipfile
import sys

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import mapping
from shapely.geometry import box
from shapely.ops import unary_union

# ── paths ──────────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
GRID_GPKG    = os.path.join(ROOT, "data", "interim", "pilot_grid.gpkg")
METRICS_CSV  = os.path.join(ROOT, "data", "processed", "pilot_metrics.csv")
STRICT_INPUTS_CSV = os.path.join(ROOT, "data", "interim", "pilot_accessibility_inputs.csv")
POIS_GPKG    = os.path.join(ROOT, "data", "interim", "merged_pois_observed.gpkg")
OCEAN_BOUNDARY = os.path.join(ROOT, "data", "interim", "ocean_park_1_boundary.geojson")
LISA_GPKG    = os.path.join(ROOT, "outputs", "results", "spatial_autocorrelation_cells.gpkg")
CROSSINGS_GPKG = os.path.join(ROOT, "outputs", "results", "boundary_permeability_crossings.gpkg")
PERMEABILITY_SUMMARY_CSV = os.path.join(ROOT, "outputs", "validation", "boundary_permeability_summary.csv")
PERMEABILITY_DETOURS_CSV = os.path.join(ROOT, "outputs", "results", "boundary_permeability_detours.csv")
VINBUS_GEOM  = os.path.join(ROOT, "data", "raw", "vinbus_overpass_relations_geom.json")
VINBUS_STOPS = os.path.join(ROOT, "data", "raw", "vinbus_pseudo_gtfs_fixed", "stops.txt")
VINBUS_ROUTES= os.path.join(ROOT, "data", "raw", "vinbus_pseudo_gtfs_fixed", "routes.txt")
OUT_HTML     = os.path.join(ROOT, "outputs", "maps", "ocean_park_interactive.html")

ANALYTICAL_SPEC = {
    "nai_primary_threshold_m": 800,
    "smci_form": "geometric_mean",
    "default_scenario": "B",
    "default_metric": "typology",
}
DELTA_EPSILON = 1e-10

# ── 1. Grid + metrics ──────────────────────────────────────────────────────
print("Reading grid ...")
grid = gpd.read_file(GRID_GPKG).to_crs("EPSG:4326")
if os.path.exists(STRICT_INPUTS_CSV):
    from src.pilot import compute_pilot_metrics

    print("Reading strict observed MAI inputs ...")
    metrics = compute_pilot_metrics(pd.read_csv(STRICT_INPUTS_CSV))
    metrics_source_note = "Strict observed MAI (no tag-only proxy fallback)"
else:
    metrics = pd.read_csv(METRICS_CSV)
    metrics_source_note = "Processed pilot metrics"
if "cell_id" not in grid.columns:
    grid = grid.reset_index().rename(columns={"index": "cell_id"})
grid["cell_id"] = grid["cell_id"].astype(int)
metrics["cell_id"] = metrics["cell_id"].astype(int)
gdf = grid.merge(metrics, on="cell_id", how="left")
WORLDPOP_CSV = os.path.join(ROOT, "data", "interim", "grid_worldpop.csv")
if os.path.exists(WORLDPOP_CSV):
    worldpop = pd.read_csv(WORLDPOP_CSV, usecols=["cell_id", "pop_sum"])
    gdf = gdf.merge(worldpop, on="cell_id", how="left")
else:
    gdf["pop_sum"] = pd.NA
QUALITY_CSV = os.path.join(ROOT, "outputs", "validation", "data_quality_grades.csv")
if os.path.exists(QUALITY_CSV):
    quality = pd.read_csv(QUALITY_CSV, usecols=["cell_id", "overall_quality_grade"])
    quality = quality.rename(columns={"overall_quality_grade": "overall_grade"})
    gdf = gdf.merge(quality, on="cell_id", how="left")
else:
    gdf["overall_grade"] = pd.NA

# Exact grid bbox (tight — used for stop filtering)
bounds = grid.total_bounds  # [minx, miny, maxx, maxy] = [lon_min, lat_min, lon_max, lat_max]
GRID_LON_MIN, GRID_LAT_MIN, GRID_LON_MAX, GRID_LAT_MAX = bounds
# tiny margin (one cell width ~250m ~ 0.0025 deg) so edge-cells' stops aren't clipped
STOP_LON_MIN = GRID_LON_MIN - 0.003
STOP_LAT_MIN = GRID_LAT_MIN - 0.003
STOP_LON_MAX = GRID_LON_MAX + 0.003
STOP_LAT_MAX = GRID_LAT_MAX + 0.003

print(f"  Grid bbox: lat [{GRID_LAT_MIN:.4f}, {GRID_LAT_MAX:.4f}]  "
      f"lon [{GRID_LON_MIN:.4f}, {GRID_LON_MAX:.4f}]")

# Study area boundary: union of all grid cells → exterior ring
print("Building study area boundary ...")
study_boundary_geom = unary_union(grid.geometry)
study_boundary_geojson = {
    "type": "FeatureCollection",
    "features": [{
        "type": "Feature",
        "geometry": mapping(study_boundary_geom),
        "properties": {"name": "Pilot study area (462 grid cells, 250 m)"},
    }]
}

print("Building Ocean Park / surrounding-context separator ...")
if os.path.exists(OCEAN_BOUNDARY):
    ocean_boundary_geom = gpd.read_file(OCEAN_BOUNDARY).to_crs("EPSG:4326").geometry.iloc[0]
    ocean_boundary_name = "Vinhomes Ocean Park 1 (OSM way 761986888)"
else:
    _metric_crs = grid.estimate_utm_crs()
    _grid_m = grid.to_crs(_metric_crs)
    minx, miny, maxx, maxy = _grid_m.geometry.unary_union.bounds
    _ocean_geom = box(minx + 1700, miny + 1300, maxx - 800, maxy - 1300)
    ocean_boundary_geom = gpd.GeoSeries([_ocean_geom], crs=_metric_crs).to_crs("EPSG:4326").iloc[0]
    ocean_boundary_name = "Approximate Ocean Park 1 core"

# Boundary attributes are computed in a projected CRS, never in degrees.
metric_crs = grid.estimate_utm_crs()
gdf_metric = gdf.to_crs(metric_crs)
ocean_metric = gpd.GeoSeries([ocean_boundary_geom], crs="EPSG:4326").to_crs(metric_crs).iloc[0]
cell_area = gdf_metric.geometry.area
gdf["share_inside_project"] = [
    geom.intersection(ocean_metric).area / area if area else 0.0
    for geom, area in zip(gdf_metric.geometry, cell_area)
]
gdf["boundary_side"] = pd.Series(gdf["share_inside_project"]).map(
    lambda value: "Inside" if value >= 0.75 else "Outside" if value <= 0.25 else "Boundary-straddling"
)
gdf["distance_to_boundary_m"] = gdf_metric.geometry.centroid.distance(ocean_metric.boundary)
gdf["boundary_band"] = pd.cut(
    gdf["distance_to_boundary_m"],
    bins=[-1, 250, 500, 1000, 2000, float("inf")],
    labels=["0-250 m", "250-500 m", "500-1000 m", "1000-2000 m", ">2000 m"],
).astype(str)
gdf["population_density"] = gdf["pop_sum"] / (cell_area.to_numpy() / 1_000_000)
gdf["population_exposure"] = gdf["pop_sum"] * (1 - gdf["SMCI_B"])
context_boundary_geom = study_boundary_geom.difference(ocean_boundary_geom)
zone_boundary_geojson = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": mapping(ocean_boundary_geom),
            "properties": {
                "name": ocean_boundary_name,
                "zone": "Ocean Park 1",
                "color": "#00e5ff",
                "fill": "#00e5ff",
            },
        },
        {
            "type": "Feature",
            "geometry": mapping(context_boundary_geom),
            "properties": {
                "name": "Surrounding context cells",
                "zone": "Adjacent context",
                "color": "#cfd8dc",
                "fill": "#cfd8dc",
            },
        },
    ],
}

TYPOLOGY_COLORS = {
    "Integrated Capability": "#2ecc71",
    "Fragmented Capability": "#f39c12",
    "Transit-Dependent":     "#3498db",
    "Motorcycle Lock-in":    "#e74c3c",
}
DEFAULT_COLOR = "#cccccc"


def typology_transition(before: object, after: object) -> str:
    """Describe Scenario A-to-B class movement without subtracting labels."""
    before, after = str(before), str(after)
    if before == after:
        return "No class change"
    if after == "Integrated Capability":
        return "Moved toward Integrated Capability"
    if before == "Integrated Capability":
        return "Moved away from Integrated Capability"
    return "Changed between intermediate classes"

def safe_float(v):
    """Keep missing values distinct from measured structural zeros in GeoJSON."""
    return None if pd.isna(v) else float(v)


def fmt(v):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "N/A"
    if isinstance(v, float):
        return f"{v:.4f}"
    return str(v)

grid_features = []
zero_nai_features = []
for _, row in gdf.iterrows():
    if row.geometry is None:
        continue
    typ = row.get("typology_B", "")
    color = TYPOLOGY_COLORS.get(str(typ), DEFAULT_COLOR)
    def _f(col):
        return safe_float(row.get(col))
    feature = {
        "type": "Feature",
        "geometry": mapping(row.geometry),
        "properties": {
            "cell_id":    int(row["cell_id"]),
            "has_data":   bool(pd.notna(row.get("SMCI_B"))),
            "population": safe_float(row.get("pop_sum")),
            "population_density": safe_float(row.get("population_density")),
            "population_exposure": safe_float(row.get("population_exposure")),
            "data_quality_grade": None if pd.isna(row.get("overall_grade")) else str(row.get("overall_grade")),
            "share_inside_project": safe_float(row.get("share_inside_project")),
            "boundary_side": str(row.get("boundary_side", "")),
            "distance_to_boundary_m": safe_float(row.get("distance_to_boundary_m")),
            "boundary_band": str(row.get("boundary_band", "")),
            "typology_A": str(row.get("typology_A", "")),
            "typology_B": str(typ),
            "typology_transition": typology_transition(row.get("typology_A", ""), typ),
            "color":      color,
            "NAI":        fmt(row.get("NAI")),
            "MAI_B":      fmt(row.get("MAI_B")),
            "MAI_A":      fmt(row.get("MAI_A")),
            "RAC_B":      fmt(row.get("RAC_B")),
            "RAC_A":      fmt(row.get("RAC_A")),
            "SMCI_A":     fmt(row.get("SMCI_A")),
            "SMCI_B":     fmt(row.get("SMCI_B")),
            "Delta_SMCI": fmt(row.get("Delta_SMCI")),
            "NAI_raw":    _f("NAI"),
            "NAI_norm":   _f("NAI_norm"),
            "MAI_raw":    _f("MAI_B"),
            "MAI_A_raw":  _f("MAI_A"),
            "MAI_A_norm": _f("MAI_A_norm"),
            "MAI_norm":   _f("MAI_B_norm"),
            "MAI_delta_raw": safe_float(row.get("MAI_B")) - safe_float(row.get("MAI_A")) if pd.notna(row.get("MAI_A")) and pd.notna(row.get("MAI_B")) else None,
            "RAC_raw":    _f("RAC_B"),
            "RAC_A_raw":  _f("RAC_A"),
            "RAC_A_norm": _f("RAC_A_norm"),
            "RAC_norm":   _f("RAC_B_norm"),
            "RAC_delta_raw": safe_float(row.get("RAC_B")) - safe_float(row.get("RAC_A")) if pd.notna(row.get("RAC_A")) and pd.notna(row.get("RAC_B")) else None,
            "SMCI_A_raw": _f("SMCI_A"),
            "SMCI_raw":   _f("SMCI_B"),
            "Delta_raw":  _f("Delta_SMCI"),
        },
    }
    grid_features.append(feature)
    if _f("NAI") == 0.0:
        zero_nai_features.append(feature)
grid_geojson = {"type": "FeatureCollection", "features": grid_features}
zero_nai_geojson = {"type": "FeatureCollection", "features": zero_nai_features}
print(f"  {len(grid_features)} grid cells")
print(f"  {len(zero_nai_features)} zero-NAI cells")

# Spatial diagnostics are kept separate from the core accessibility indices.
LISA_CLUSTER_COLORS = {
    "High-High": "#b2182b",
    "Low-Low": "#2166ac",
    "High-Low": "#ef8a62",
    "Low-High": "#67a9cf",
    "Not Significant": "#d9d9d9",
}
lisa_features = []
if os.path.exists(LISA_GPKG):
    print("Reading LISA diagnostics ...")
    lisa = gpd.read_file(LISA_GPKG).to_crs("EPSG:4326")
    lisa_columns = {
        "cluster": "SMCI_B__queen__cluster",
        "p_value": "SMCI_B__queen__p_value",
        "q_value": "SMCI_B__queen__q_value",
        "local_i": "SMCI_B__queen__local_i",
        "spatial_lag": "SMCI_B__queen__spatial_lag",
    }
    missing_lisa = [column for column in lisa_columns.values() if column not in lisa.columns]
    if missing_lisa:
        print(f"  Skipping LISA layer; missing columns: {', '.join(missing_lisa)}")
    else:
        for _, row in lisa.iterrows():
            cluster = str(row[lisa_columns["cluster"]])
            lisa_features.append({
                "type": "Feature",
                "geometry": mapping(row.geometry),
                "properties": {
                    "cell_id": int(row["cell_id"]),
                    "cluster": cluster,
                    "color": LISA_CLUSTER_COLORS.get(cluster, LISA_CLUSTER_COLORS["Not Significant"]),
                    "p_value": float(row[lisa_columns["p_value"]]),
                    "q_value": float(row[lisa_columns["q_value"]]),
                    "local_i": float(row[lisa_columns["local_i"]]),
                    "spatial_lag": float(row[lisa_columns["spatial_lag"]]),
                },
            })
lisa_geojson = {"type": "FeatureCollection", "features": lisa_features}
lisa_significant = sum(feature["properties"]["cluster"] != "Not Significant" for feature in lisa_features)
print(f"  {len(lisa_features)} LISA cells ({lisa_significant} FDR-significant)")

crossing_features = []
if os.path.exists(CROSSINGS_GPKG):
    print("Reading boundary permeability crossings ...")
    crossings = gpd.read_file(CROSSINGS_GPKG).to_crs("EPSG:4326")
    seen_physical_crossings = set()
    for _, row in crossings.iterrows():
        crossing_id = (str(row["mode"]), str(row["physical_edge_id"]))
        if crossing_id in seen_physical_crossings:
            continue
        seen_physical_crossings.add(crossing_id)
        crossing_features.append({
            "type": "Feature",
            "geometry": mapping(row.geometry),
            "properties": {
                "mode": str(row["mode"]),
                "length_m": float(row["length_m"]),
                "highway": str(row["highway"]),
                "access_status": str(row["access_status"]),
                "approx_edge_betweenness": float(row["approx_edge_betweenness"]),
            },
        })
crossings_geojson = {"type": "FeatureCollection", "features": crossing_features}
crossing_counts = {
    mode: sum(feature["properties"]["mode"] == mode for feature in crossing_features)
    for mode in ("walking", "motorcycle")
}
print(f"  {crossing_counts['walking']} walking and {crossing_counts['motorcycle']} motorcycle crossings")

permeability_summary = {}
if os.path.exists(PERMEABILITY_SUMMARY_CSV):
    for _, row in pd.read_csv(PERMEABILITY_SUMMARY_CSV).iterrows():
        permeability_summary[str(row["mode"])] = {
            "crossings_per_km": float(row["physical_crossings_per_km"]),
            "boundary_length_km": float(row["boundary_length_km"]),
        }
if os.path.exists(PERMEABILITY_DETOURS_CSV):
    detours = pd.read_csv(PERMEABILITY_DETOURS_CSV)
    for mode, values in detours.groupby("mode"):
        permeability_summary.setdefault(str(mode), {})["median_detour_ratio"] = float(values["detour_ratio"].median())
walking_detour = permeability_summary.get("walking", {}).get("median_detour_ratio", float("nan"))
motorcycle_detour = permeability_summary.get("motorcycle", {}).get("median_detour_ratio", float("nan"))

# ── 2. POIs ────────────────────────────────────────────────────────────────
print("Reading POIs ...")
pois_gdf = gpd.read_file(POIS_GPKG).to_crs("EPSG:4326")

DOMAIN_COLORS = {
    "education":        "#9b59b6",
    "health":           "#e74c3c",
    "economic":         "#e67e22",
    "daily_needs":      "#27ae60",
    "retail":           "#f1c40f",
    "financial_service":"#8e44ad",
    "transportation":   "#7f8c8d",
    "recreation":       "#1abc9c",
}

def infer_domain(row):
    def _txt(key):
        val = row.get(key, "")
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return ""
        text = str(val).strip().lower()
        return "" if text in {"nan", "none", "<na>"} else text
    cat     = _txt("category")
    amenity = _txt("amenity")
    shop    = _txt("shop")
    edu     = _txt("education")
    office  = _txt("office")
    landuse = _txt("landuse")
    if cat in ("education","higher_ed") or "school" in amenity or "university" in amenity or edu:
        return "education"
    if cat == "health_and_medical" or amenity in ("hospital","clinic","pharmacy","doctors"):
        return "health"
    if cat in ("retail","financial_service") or shop or office or landuse in ("commercial","industrial"):
        return "economic"
    if amenity in ("restaurant","cafe","fast_food","marketplace"):
        return "daily_needs"
    if amenity == "park" or landuse == "park":
        return "recreation"
    if cat == "transportation":
        return "transportation"
    return "daily_needs"

poi_features = []
for _, row in pois_gdf.iterrows():
    geom = row.geometry
    if geom is None:
        continue
    if geom.geom_type != "Point":
        geom = geom.centroid
    lat, lon = geom.y, geom.x
    # POI filter: slightly wider than stop filter to catch edge POIs
    if not (STOP_LAT_MIN - 0.02 < lat < STOP_LAT_MAX + 0.02 and
            STOP_LON_MIN - 0.02 < lon < STOP_LON_MAX + 0.02):
        continue
    domain = infer_domain(row)
    name = str(row.get("name") or row.get("name:vi") or row.get("id") or "POI")
    source = str(row.get("source", "osm_only"))
    cat = str(row.get("category") or row.get("amenity") or row.get("shop") or "")
    poi_features.append({
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [lon, lat]},
        "properties": {
            "name":     name,
            "domain":   domain,
            "source":   source,
            "category": cat,
            "color":    DOMAIN_COLORS.get(domain, "#95a5a6"),
        },
    })
poi_geojson = {"type": "FeatureCollection", "features": poi_features}
print(f"  {len(poi_features)} POIs")

# ── 3. VinBus OSM route lines ──────────────────────────────────────────────
print("Reading VinBus OSM routes ...")
with open(VINBUS_GEOM, encoding="utf-8") as f:
    vinbus_raw = json.load(f)

ROUTE_COLORS = {
    "E01": "#e74c3c", "E02": "#3498db", "E03": "#2ecc71",
    "E10": "#f39c12", "OCP1": "#9b59b6", "OCP2": "#1abc9c",
}

SNAP_TOL = 0.0002  # ~20 m — join way endpoints within this distance

def _dist(a, b):
    return ((a[0]-b[0])**2 + (a[1]-b[1])**2) ** 0.5

route_features = []
for rel in vinbus_raw.get("elements", []):
    if rel.get("type") != "relation":
        continue
    tags = rel.get("tags", {})
    ref  = tags.get("ref", tags.get("name", f"rel_{rel['id']}"))
    # Collect all way segments first
    segs = []
    for member in rel.get("members", []):
        if member.get("type") != "way":
            continue
        seg = [[p["lon"], p["lat"]] for p in member.get("geometry", [])]
        if len(seg) >= 2:
            segs.append(seg)
    if not segs:
        continue
    # Join with tolerance
    coords = segs[0]
    for seg in segs[1:]:
        if _dist(coords[-1], seg[0]) < SNAP_TOL:
            coords.extend(seg[1:])
        elif _dist(coords[-1], seg[-1]) < SNAP_TOL:
            # reversed segment
            coords.extend(list(reversed(seg))[1:])
        else:
            # genuine gap — save current chain, start new
            if len(coords) >= 2:
                route_features.append({
                    "type": "Feature",
                    "geometry": {"type": "LineString", "coordinates": coords},
                    "properties": {
                        "ref":    ref,
                        "name":   tags.get("name", ref),
                        "color":  ROUTE_COLORS.get(ref, "#aaa"),
                        "rel_id": rel["id"],
                    },
                })
            coords = seg
    if len(coords) >= 2:
        route_features.append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": coords},
            "properties": {
                "ref":    ref,
                "name":   tags.get("name", ref),
                "color":  ROUTE_COLORS.get(ref, "#aaa"),
                "rel_id": rel["id"],
            },
        })

route_geojson = {"type": "FeatureCollection", "features": route_features}
# Also compute route bbox for fitBounds
all_route_lats = [p[1] for f in route_features for p in f["geometry"]["coordinates"]]
all_route_lons = [p[0] for f in route_features for p in f["geometry"]["coordinates"]]
route_bounds = {
    "lat_min": min(all_route_lats), "lat_max": max(all_route_lats),
    "lon_min": min(all_route_lons), "lon_max": max(all_route_lons),
}
print(f"  {len(route_features)} route segments ({len(vinbus_raw.get('elements',[]))} relations)")
print(f"  Route bbox: lat[{route_bounds['lat_min']:.4f},{route_bounds['lat_max']:.4f}] "
      f"lon[{route_bounds['lon_min']:.4f},{route_bounds['lon_max']:.4f}]")

# ── 4. VinBus pseudo-GTFS stops — EXACT bbox filter ───────────────────────
print("Reading VinBus pseudo-GTFS stops (tight bbox) ...")
stop_features = []
with open(VINBUS_STOPS, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            lat = float(row["stop_lat"])
            lon = float(row["stop_lon"])
        except (ValueError, KeyError):
            continue
        if not (STOP_LAT_MIN < lat < STOP_LAT_MAX and STOP_LON_MIN < lon < STOP_LON_MAX):
            continue
        stop_features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
            "properties": {
                "name":    row.get("stop_name", ""),
                "stop_id": row.get("stop_id", ""),
                "desc":    row.get("stop_desc", ""),
            },
        })
stops_geojson = {"type": "FeatureCollection", "features": stop_features}
print(f"  {len(stop_features)} VinBus stops (was 1289 with loose filter)")

# ── 5. Hanoi GTFS stops — EXACT bbox filter ────────────────────────────────
print("Reading Hanoi GTFS stops (tight bbox) ...")
hanoi_stop_features = []

def _load_hanoi_stops(reader):
    for row in reader:
        try:
            lat = float(row["stop_lat"])
            lon = float(row["stop_lon"])
        except (ValueError, KeyError):
            continue
        if not (STOP_LAT_MIN < lat < STOP_LAT_MAX and STOP_LON_MIN < lon < STOP_LON_MAX):
            continue
        hanoi_stop_features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
            "properties": {
                "name":    row.get("stop_name", ""),
                "stop_id": row.get("stop_id", ""),
            },
        })

HANOI_STOPS = os.path.join(ROOT, "data", "raw", "hanoi_gtfs", "stops.txt")
if os.path.exists(HANOI_STOPS):
    with open(HANOI_STOPS, encoding="utf-8") as f:
        _load_hanoi_stops(csv.DictReader(f))
else:
    HANOI_ZIP = os.path.join(ROOT, "data", "raw", "hanoi_gtfs.zip")
    if os.path.exists(HANOI_ZIP):
        with zipfile.ZipFile(HANOI_ZIP) as z:
            stops_file = next((n for n in z.namelist() if n.endswith("stops.txt")), None)
            if stops_file:
                with z.open(stops_file) as sf:
                    _load_hanoi_stops(csv.DictReader(io.TextIOWrapper(sf, encoding="utf-8")))

hanoi_stops_geojson = {"type": "FeatureCollection", "features": hanoi_stop_features}
print(f"  {len(hanoi_stop_features)} Hanoi GTFS stops (was 2422 with loose filter)")

# ── 6. Compute histogram data for continuous legend (Python side) ──────────
def make_histogram(features, key, n_bins=20, include_zero=False):
    vals = [f["properties"][key] for f in features
            if isinstance(f["properties"].get(key), (int, float))
            and (include_zero or f["properties"][key] > 0)]
    if not vals:
        return [], 0, 1
    lo, hi = min(vals), max(vals)
    if lo == hi:
        return [len(vals)], lo, hi
    bins = [0] * n_bins
    for v in vals:
        idx = min(int((v - lo) / (hi - lo) * n_bins), n_bins - 1)
        bins[idx] += 1
    return bins, lo, hi


def shared_visual_bounds(features, *keys, diverging: bool = False) -> tuple[float, float]:
    """Use common robust A/B bounds so visual differences are comparable."""
    values = [f["properties"].get(key) for f in features for key in keys]
    values = np.asarray([value for value in values if isinstance(value, (int, float)) and np.isfinite(value)], dtype=float)
    if not len(values):
        return 0.0, 1.0
    lo, hi = np.quantile(values, [0.02, 0.98])
    if diverging:
        bound = max(abs(lo), abs(hi))
        return -float(bound), float(bound)
    return float(lo), float(hi) if hi > lo else float(lo + 1.0)

nai_hist,   nai_lo,   nai_hi   = make_histogram(grid_features, "NAI_raw",   20)
smci_hist,  _, _ = make_histogram(grid_features, "SMCI_raw", 20)
mai_hist,   _, _ = make_histogram(grid_features, "MAI_raw", 20)
rac_hist,   _, _ = make_histogram(grid_features, "RAC_raw", 20)
delta_hist, delta_lo, delta_hi = make_histogram(grid_features, "Delta_raw", 20, include_zero=True)
smci_lo, smci_hi = shared_visual_bounds(grid_features, "SMCI_A_raw", "SMCI_raw")
mai_lo, mai_hi = shared_visual_bounds(grid_features, "MAI_A_raw", "MAI_raw")
rac_lo, rac_hi = shared_visual_bounds(grid_features, "RAC_A_raw", "RAC_raw")
delta_lo, delta_hi = shared_visual_bounds(grid_features, "Delta_raw", diverging=True)
pop_hist, pop_lo, pop_hi = make_histogram(grid_features, "population", 20, include_zero=True)
density_hist, density_lo, density_hi = make_histogram(grid_features, "population_density", 20, include_zero=True)
exposure_hist, exposure_lo, exposure_hi = make_histogram(grid_features, "population_exposure", 20, include_zero=True)

METRIC_META = {
    "nai":   {"label": "NAI",        "unit": "reachable POIs",    "desc": "Walkable POIs within 800 m network distance (~10 min)",
              "long": "<b>NAI</b>: local walkability. It counts nearby everyday POIs reachable on the walking network. Higher values mean the cell has more schools, clinics, shops, parks, or daily services close enough for walking.",
              "how": "Lower value = fewer walkable nearby POIs; higher value = more walkable nearby POIs.",
              "hist": nai_hist,   "lo": nai_lo,   "hi": nai_hi},
    "smci":  {"label": "SMCI_B",     "unit": "index",    "desc": "Sustainable Mobility Capability Index (Scenario B with VinBus)",
              "long": "<b>SMCI_B</b>: final sustainable mobility capability after adding VinBus. It combines local walking access, metropolitan opportunity access, and transit-vs-motorcycle competitiveness. Because it is multiplicative, one weak component can pull the score down.",
              "how": "Lower value = weaker sustainable mobility capability; higher value = stronger capability.",
              "hist": smci_hist,  "lo": smci_lo,  "hi": smci_hi},
    "mai":   {"label": "MAI_B",      "unit": "weighted", "desc": "Metropolitan Accessibility Index — magnitude-weighted, walk+transit, 60 min cutoff",
              "long": "<b>MAI_B</b>: metropolitan opportunity access after VinBus. It measures how many weighted opportunities can be reached by walking plus transit within the 60-minute impedance window. Destination weights use the strict source-backed MAI audit.",
              "how": "Lower value = fewer/weaker metropolitan opportunities reachable by walk+transit; higher value = more/stronger reachable opportunities.",
              "hist": mai_hist,   "lo": mai_lo,   "hi": mai_hi},
    "rac":   {"label": "RAC_B",      "unit": "ratio",    "desc": "Relative Accessibility Competitiveness = RAC_time primary; higher = transit travel time closer to motorcycle",
              "long": "<b>RAC_B</b>: promoted reviewer-safe time competitiveness of walking plus transit against motorcycle access after VinBus. Higher values mean transit narrows the travel-time gap with motorcycles. The previous full RAC with opportunity ratio is retained as robustness, not the primary map.",
              "how": "Lower value = walk+transit is less competitive against motorcycle; higher value = more competitive.",
              "hist": rac_hist,   "lo": rac_lo,   "hi": rac_hi},
    "delta": {"label": "Modeled difference: Scenario B minus A", "unit": "index difference",    "desc": "Shared-scale SMCI(B) minus SMCI(A)",
              "long": "<b>Delta_SMCI</b>: modeled difference between Scenario B and Scenario A using shared normalization bounds. Positive values mean the Scenario B value is higher.",
              "how": "Negative = lower under Scenario B; zero = unchanged; positive = higher under Scenario B.",
              "hist": delta_hist, "lo": delta_lo, "hi": delta_hi},
    "population": {"label": "Population", "unit": "people per cell", "desc": "WorldPop 2020 population estimate",
              "long": "Population is an exposure denominator, not a measurement of accessibility.", "how": "Lower value = fewer estimated residents; higher value = more estimated residents.", "hist": pop_hist, "lo": pop_lo, "hi": pop_hi},
    "density": {"label": "Population density", "unit": "people / km2", "desc": "WorldPop population divided by cell area",
              "long": "Population density is a descriptive demand-side layer, not an input to the primary SMCI.", "how": "Lower value = lower estimated density; higher value = higher estimated density.", "hist": density_hist, "lo": density_lo, "hi": density_hi},
    "exposure": {"label": "Population exposure", "unit": "people x (1 - SMCI_B)", "desc": "Diagnostic population-weighted low-capability exposure",
              "long": "Exposure is Population x (1 - SMCI_B). It is a diagnostic, not a validated independent index.", "how": "Lower value = less estimated exposure; higher value = more estimated exposure.", "hist": exposure_hist, "lo": exposure_lo, "hi": exposure_hi},
    "boundary": {"label": "Boundary fragmentation", "unit": "distance / side", "desc": "Inside, outside, or boundary-straddling project relation",
              "long": "Boundary fragmentation is a descriptive spatial relation to Ocean Park 1, not a causal effect.", "how": "Categories distinguish inside, outside, and boundary-straddling cells.", "hist": [], "lo": 0, "hi": 1},
    "quality": {"label": "Data quality grade", "unit": "A-D provenance grade", "desc": "Cell-level provenance audit",
              "long": "Data-quality grades audit input provenance. They are not an SMCI component or confidence interval.", "how": "A is stronger documented provenance; D is weaker. No local POI is a separate absence label.", "hist": [], "lo": 0, "hi": 1},
}

# ── 7. Serialise ──────────────────────────────────────────────────────────
def js(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':'))

map_center_lat = (GRID_LAT_MIN + GRID_LAT_MAX) / 2
map_center_lon = (GRID_LON_MIN + GRID_LON_MAX) / 2

# ── 8. Build HTML ──────────────────────────────────────────────────────────
print("Building HTML ...")

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Vinhomes Ocean Park — Mobility Capability Map</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
*{{box-sizing:border-box;margin:0;padding:0;}}
html,body{{height:100%;font-family:'Segoe UI',Arial,sans-serif;background:#1a1a2e;}}
#app{{display:flex;height:100vh;}}
#sidebar{{
  width:310px;min-width:240px;background:#16213e;color:#eee;
  overflow-y:auto;padding:14px 12px;flex-shrink:0;font-size:12.5px;
}}
#map{{flex:1;position:relative;}}
@media (max-width:700px){{
  #app{{flex-direction:column;height:100dvh;}}
  #sidebar{{width:100%;min-width:0;max-height:46dvh;padding:10px 12px;}}
  #map{{min-height:54dvh;}}
}}
h2{{font-size:11.5px;color:#4fc3f7;margin:10px 0 5px;letter-spacing:.6px;text-transform:uppercase;font-weight:700;}}
h1{{font-size:15px;color:#fff;margin-bottom:3px;line-height:1.35;font-weight:700;}}
.subtitle{{font-size:10.5px;color:#90a4ae;margin-bottom:2px;}}
.section{{border-top:1px solid #243454;padding-top:9px;margin-top:9px;}}
label{{display:flex;align-items:center;gap:7px;cursor:pointer;padding:3px 0;font-size:12px;}}
label input{{accent-color:#4fc3f7;cursor:pointer;}}
.swatch{{width:13px;height:13px;border-radius:3px;display:inline-block;flex-shrink:0;border:1px solid rgba(255,255,255,0.15);}}
.line-swatch{{width:22px;height:4px;border-radius:2px;display:inline-block;flex-shrink:0;}}
.legend-row{{display:flex;align-items:center;gap:7px;margin:3px 0;font-size:11px;color:#ccc;}}
select{{
  background:#0f3460;color:#eee;border:1px solid #4fc3f7;
  border-radius:4px;padding:5px 7px;font-size:12px;width:100%;margin-top:5px;cursor:pointer;
}}
button{{background:#0f3460;color:#eee;border:1px solid #4fc3f7;border-radius:4px;padding:5px 7px;font-size:11px;cursor:pointer;margin:2px 2px 0 0;}}
button:hover,button:focus{{background:#17517f;outline:2px solid #fff;outline-offset:1px;}}
#info-panel{{
  background:#0d2137;border-radius:6px;padding:9px 10px;margin-top:8px;
  font-size:11px;min-height:70px;line-height:1.65;color:#b0c4de;
}}
#info-panel b{{color:#4fc3f7;}}
.metric-grid{{display:grid;grid-template-columns:1fr 1fr;gap:5px;margin-top:7px;}}
.metric{{background:#112847;border-radius:5px;padding:6px 8px;}}
.metric .val{{font-size:14px;font-weight:700;color:#4fc3f7;}}
.metric .lbl{{font-size:9.5px;color:#7a9ec8;margin-top:1px;}}
.comparison{{grid-column:span 2;background:#0b2742;border-radius:5px;padding:7px 8px;}}
.comparison-row{{display:grid;grid-template-columns:40px 1fr 1fr;gap:4px;align-items:center;margin-top:4px;font-size:9px;color:#9fb7d8;}}
.comparison-bar{{height:7px;border-radius:3px;background:#2b496a;overflow:hidden;}}
.comparison-fill-a{{height:100%;background:#8da0cb;}}
.comparison-fill-b{{height:100%;background:#66c2a5;}}
.badge{{display:inline-block;padding:2px 7px;border-radius:10px;font-size:10px;font-weight:700;}}
/* Continuous legend */
#cont-legend{{display:none;margin-top:8px;}}
#cont-legend .leg-label{{display:flex;justify-content:space-between;font-size:10px;color:#90a4ae;margin-bottom:2px;}}
#cont-legend .leg-bar{{
  height:10px;border-radius:3px;
  background:linear-gradient(to right,
    #313695,#4575b4,#74add1,#abd9e9,#e0f3f8,
    #ffffbf,#fee090,#fdae61,#f46d43,#d73027,#a50026);
  margin-bottom:5px;
}}
#cont-legend .leg-hist{{display:flex;align-items:flex-end;height:36px;gap:1px;margin-bottom:3px;}}
#cont-legend .leg-hist .bar{{
  flex:1;background:rgba(79,195,247,0.5);border-radius:1px 1px 0 0;min-height:1px;
}}
#cont-legend .leg-desc{{font-size:10px;color:#78909c;line-height:1.4;margin-top:4px;}}
#cont-legend .leg-how{{
  font-size:10.5px;color:#d7ecff;line-height:1.45;margin-top:6px;
  background:#0b2742;border-left:3px solid #4fc3f7;border-radius:4px;padding:6px 7px;
}}
#cont-legend .leg-unit{{
  font-size:9.5px;color:#4fc3f7;font-weight:600;
  text-transform:uppercase;letter-spacing:.4px;margin-bottom:2px;
}}
.layer-desc{{
  background:#0d2137;border-radius:6px;padding:9px 10px;margin-top:8px;
  font-size:11px;line-height:1.55;color:#c6d6f0;
}}
.layer-desc ul{{margin:6px 0 0 16px;padding:0;}}
.layer-desc li{{margin:5px 0;}}
.layer-desc b{{color:#e3ecff;}}
.layer-desc .active-desc{{
  margin-top:8px;padding-top:8px;border-top:1px solid #243454;color:#d7ecff;
}}
/* Map attribution override */
.leaflet-control-attribution{{font-size:9px!important;opacity:0.7;}}
.leaflet-control-scale-line{{font-size:9.5px!important;}}
</style>
</head>
<body>
<div id="app">
<div id="sidebar">
  <h1>Vinhomes Ocean Park</h1>
  <div class="subtitle">Fragmented Mobility Capability — Pilot Study</div>
  <div class="subtitle" style="color:#546e7a;">Gia Lam, Hanoi &middot; 462 cells &middot; 250 m grid &middot; 2026</div>
  <div class="subtitle" style="color:#4fc3f7;">{metrics_source_note}</div>

  <div class="section">
    <h2>Basemap</h2>
    <select id="basemap-sel">
      <option value="carto" selected>CartoDB Dark</option>
      <option value="osm">OpenStreetMap</option>
      <option value="esri">Esri Satellite</option>
    </select>
  </div>

  <div class="section">
    <h2>Grid cells</h2>
    <label>Scenario
      <select id="scenario-sel"><option value="B" selected>Scenario B</option><option value="A">Scenario A</option><option value="difference">Difference B minus A</option></select>
    </label>
    <label><input type="checkbox" id="chk-grid" checked> Show 462-cell grid</label>
    <label><input type="checkbox" id="chk-boundary" checked>
      <span class="swatch" style="background:transparent;border:2px dashed #f39c12;"></span>
      Study area boundary
    </label>
    <label><input type="checkbox" id="chk-zones" checked>
      <span class="swatch" style="background:transparent;border:2px solid #00e5ff;"></span>
      Ocean Park / adjacent-context separator
    </label>
    <label><input type="checkbox" id="chk-zero-nai">
      <span class="swatch" style="background:rgba(255,255,255,.08);border:2px solid #ffffff;"></span>
      Zero NAI cells ({len(zero_nai_features)})
    </label>
    <select id="grid-mode">
      <option value="typology" selected>Typology B (primary)</option>
      <option value="smci">SMCI_B — capability index</option>
      <option value="nai">NAI — walkable POIs (count)</option>
      <option value="mai">MAI_B — metro opportunity</option>
      <option value="rac">RAC_B — transit vs motorcycle</option>
      <option value="delta">Modeled difference: Scenario B minus A</option>
      <option value="population">Population</option>
      <option value="density">Population density</option>
      <option value="exposure">Population exposure</option>
      <option value="boundary">Boundary fragmentation</option>
      <option value="quality">Data quality grade</option>
    </select>
    <div style="margin-top:6px;" aria-label="Map presets">
      <button type="button" data-preset="capability">Capability</button><button type="button" data-preset="comparison">Scenario comparison</button><button type="button" data-preset="exposure">Population exposure</button><button type="button" data-preset="boundary">Boundary</button>
    </div>
    <div style="margin-top:4px;" aria-label="Map navigation"><button type="button" id="fit-study">Fit study area</button><button type="button" id="fit-project">Fit project boundary</button><button type="button" id="fit-network">Show full VinBus network</button></div>

    <div id="typo-legend" style="margin-top:9px;">
      <div class="legend-row"><span class="swatch" style="background:#2ecc71;"></span>Integrated Capability</div>
      <div class="legend-row"><span class="swatch" style="background:#f39c12;"></span>Fragmented Capability</div>
      <div class="legend-row"><span class="swatch" style="background:#3498db;"></span>Transit-Dependent</div>
      <div class="legend-row"><span class="swatch" style="background:#e74c3c;"></span>Motorcycle Lock-in</div>
      <div class="legend-row"><span class="swatch" style="background:#999;opacity:.6;"></span>No data / water</div>
    </div>

    <div id="cont-legend">
      <div class="leg-unit" id="leg-unit"></div>
      <div class="leg-hist" id="leg-hist"></div>
      <div class="leg-bar"></div>
      <div class="leg-label"><span id="leg-min"></span><span id="leg-max"></span></div>
      <div class="leg-how" id="leg-how"></div>
      <div class="leg-desc" id="leg-desc"></div>
    </div>
    <div class="layer-desc">
      <div><b>Core layers</b></div>
      <ul>
        <li><b>Typology B</b>: final spatial class for Scenario B.</li>
        <li><b>NAI</b>: local walkability, walking access to nearby everyday amenities.</li>
        <li><b>MAI_B</b>: metropolitan opportunity access after VinBus.</li>
        <li><b>RAC_B</b>: how well walk+transit competes with motorcycle access.</li>
        <li><b>Delta_SMCI</b>: how much VinBus changes SMCI.</li>
        <li><b>SMCI_B</b>: final capability index after VinBus.</li>
      </ul>
      <div class="active-desc" id="active-layer-desc"></div>
      <div class="active-desc" style="border-top-color:#ffffff;">
        <b>Zero NAI caution</b><br>
        NAI = 0 means no mapped walkable POIs within the walking threshold. It does not prove there are no real-world amenities. In this pilot, zero-NAI built cells are analytically important because they also force SMCI_B to 0.
      </div>
    </div>
  </div>

  <div class="section">
    <h2>Spatial diagnostics</h2>
    <label><input type="checkbox" id="chk-lisa">
      <span class="swatch" style="background:#b2182b;"></span>
      SMCI_B LISA clusters ({lisa_significant} FDR-significant cells)
    </label>
    <div style="margin:4px 0 6px 20px;">
      <div class="legend-row"><span class="swatch" style="background:#b2182b;"></span>High-High</div>
      <div class="legend-row"><span class="swatch" style="background:#2166ac;"></span>Low-Low</div>
      <div class="legend-row"><span class="swatch" style="background:#ef8a62;"></span>High-Low</div>
      <div class="legend-row"><span class="swatch" style="background:#67a9cf;"></span>Low-High</div>
      <div class="legend-row"><span class="swatch" style="background:#d9d9d9;"></span>Not significant</div>
    </div>
    <label><input type="checkbox" id="chk-walk-crossings">
      <span class="line-swatch" style="background:#238b45;"></span>
      Walking crossings ({crossing_counts['walking']})
    </label>
    <label><input type="checkbox" id="chk-motorcycle-crossings">
      <span class="line-swatch" style="background:#756bb1;"></span>
      Motorcycle crossings ({crossing_counts['motorcycle']})
    </label>
    <div class="layer-desc">
      <b>Diagnostic only</b><br>
      LISA uses Queen contiguity, 9,999 permutations, and FDR correction. It identifies spatial association, not a boundary effect or causal mechanism.<br><br>
      Crossing lines are modeled Network A/D topology, not confirmed public gates. Median near-boundary detour is {walking_detour:.2f}x for walking and {motorcycle_detour:.2f}x for motorcycle.
    </div>
  </div>

  <div class="section">
    <h2>Points of Interest (strict observed)</h2>
    <label><input type="checkbox" id="chk-poi"> Show POIs</label>
    <div style="margin-top:5px;">
      <div class="legend-row"><span class="swatch" style="background:#9b59b6;border-radius:50%;"></span>Education (incl. higher ed)</div>
      <div class="legend-row"><span class="swatch" style="background:#e74c3c;border-radius:50%;"></span>Health</div>
      <div class="legend-row"><span class="swatch" style="background:#e67e22;border-radius:50%;"></span>Economic / Office</div>
      <div class="legend-row"><span class="swatch" style="background:#27ae60;border-radius:50%;"></span>Daily needs</div>
      <div class="legend-row"><span class="swatch" style="background:#f1c40f;border-radius:50%;"></span>Retail</div>
      <div class="legend-row"><span class="swatch" style="background:#7f8c8d;border-radius:50%;"></span>Transport / Other</div>
    </div>
    <div style="font-size:10px;color:#546e7a;margin-top:4px;">Sources: OSM + Overture + source-backed MAI audit (Decision #21)</div>
  </div>

  <div class="section">
    <h2>Transit Networks</h2>
    <label><input type="checkbox" id="chk-routes">
      <span class="line-swatch" style="background:#e74c3c;"></span>
      VinBus routes (OSM geometry)
    </label>
    <div style="font-size:10px;color:#546e7a;padding:2px 0 5px 20px;">
      E01&thinsp;<span style="color:#e74c3c">&#9632;</span>
      E02&thinsp;<span style="color:#3498db">&#9632;</span>
      E03&thinsp;<span style="color:#2ecc71">&#9632;</span>
      E10&thinsp;<span style="color:#f39c12">&#9632;</span>
      OCP1&thinsp;<span style="color:#9b59b6">&#9632;</span>
      OCP2&thinsp;<span style="color:#1abc9c">&#9632;</span>
    </div>
    <label><input type="checkbox" id="chk-vstops">
      <span class="swatch" style="background:#1abc9c;border-radius:2px;width:10px;height:10px;"></span>
      VinBus stops — Network C (pseudo-GTFS, {len(stop_features)} in area)
    </label>
    <label><input type="checkbox" id="chk-hstops">
      <span class="swatch" style="background:#3498db;border-radius:2px;width:10px;height:10px;"></span>
      Hanoi GTFS stops — Network B baseline ({len(hanoi_stop_features)} in area)
    </label>
    <div style="font-size:10px;color:#546e7a;margin-top:4px;">GTFS: Hanoi 2018 vintage (pre-VinBus baseline, stop geometry valid)</div>
  </div>

  <div class="section">
    <h2>Selected cell</h2>
    <div id="info-panel"></div>
  </div>

  <div class="section" style="margin-top:6px;font-size:10px;color:#455a64;line-height:1.5;">
    Methodology: proposal/proposal_v7.md &sect;3<br>
    Pipeline: scripts/build_accessibility_inputs.py --opportunity-basis observed_strict<br>
    SMCI = NAI<sub>norm</sub> &times; MAI<sub>norm</sub> &times; RAC<sub>norm</sub>
  </div>
</div>

<div id="map"></div>
</div>

<script>
// ── Embedded GeoJSON data ──────────────────────────────────────────────────
const GRID     = {js(grid_geojson)};
const ZERO_NAI = {js(zero_nai_geojson)};
const BOUNDARY = {js(study_boundary_geojson)};
const ZONES    = {js(zone_boundary_geojson)};
const POIS     = {js(poi_geojson)};
const ROUTES   = {js(route_geojson)};
const VSTOPS   = {js(stops_geojson)};
const HSTOPS   = {js(hanoi_stops_geojson)};
const LISA     = {js(lisa_geojson)};
const CROSSINGS = {js(crossings_geojson)};

// ── Metric metadata (for continuous legend) ────────────────────────────────
const METRIC_META = {js(METRIC_META)};
let selectedCellFeature = GRID.features[Math.floor(GRID.features.length / 2)] || null;

// ── Map init ──────────────────────────────────────────────────────────────
const map = L.map('map', {{
  zoomControl: true,
  attributionControl: true,
}}).setView([{map_center_lat:.4f}, {map_center_lon:.4f}], 13);

// Scale bar (bottom-left, metric)
L.control.scale({{imperial: false, maxWidth: 150}}).addTo(map);

// Basemaps
const basemaps = {{
  carto: L.tileLayer(
    'https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png',
    {{attribution:'&copy; <a href="https://carto.com">CartoDB</a> &copy; <a href="https://openstreetmap.org">OSM</a>', maxZoom:19, subdomains:'abcd'}}
  ),
  osm: L.tileLayer(
    'https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',
    {{attribution:'&copy; <a href="https://openstreetmap.org">OpenStreetMap</a>', maxZoom:19}}
  ),
  esri: L.tileLayer(
    'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}',
    {{attribution:'&copy; Esri &copy; OSM', maxZoom:18}}
  ),
}};
basemaps.carto.addTo(map);

// Custom attribution
map.attributionControl.setPrefix(
  'Pilot study: <i>Fragmented Mobility Capability, Vinhomes Ocean Park 2026</i>'
);

document.getElementById('basemap-sel').addEventListener('change', e => {{
  Object.values(basemaps).forEach(l => map.removeLayer(l));
  basemaps[e.target.value].addTo(map);
}});

// ── Colour helpers ─────────────────────────────────────────────────────────
function lerp(a,b,t){{ return a+(b-a)*t; }}
function clamp(v,lo,hi){{ return Math.max(lo,Math.min(hi,v)); }}

const VIRIDIS = [
  [68,1,84],[72,40,120],[62,74,137],[49,104,142],[38,130,142],
  [31,158,137],[53,183,121],[109,205,89],[180,222,44],[253,231,37]
];
const DELTA = [[178,24,43],[244,165,130],[245,245,245],[146,197,222],[33,102,172]];
function paletteColor(t, palette) {{
  t = clamp(t, 0, 0.9999);
  const n = palette.length - 1;
  const i = Math.floor(t * n);
  const f = t * n - i;
  const [r1,g1,b1] = palette[i];
  const [r2,g2,b2] = palette[Math.min(i+1,n)];
  return `rgb(${{Math.round(lerp(r1,r2,f))}},${{Math.round(lerp(g1,g2,f))}},${{Math.round(lerp(b1,b2,f))}})`;
}}
function norm(v,lo,hi){{ return hi===lo ? 0.5 : clamp((v-lo)/(hi-lo),0,1); }}

// ── Study area boundary ────────────────────────────────────────────────────
const boundaryLayer = L.geoJSON(BOUNDARY, {{
  interactive: false,
  style: {{
    color: '#f39c12', weight: 2.5, dashArray: '6 4',
    fillColor: 'transparent', fillOpacity: 0,
  }},
}});
boundaryLayer.addTo(map);

document.getElementById('chk-boundary').addEventListener('change', e => {{
  e.target.checked ? boundaryLayer.addTo(map) : map.removeLayer(boundaryLayer);
}});

const zoneLayer = L.geoJSON(ZONES, {{
  interactive: false,
  style: f => {{
    const isOcean = f.properties.zone === 'Ocean Park';
    return {{
      color: f.properties.color,
      weight: isOcean ? 3.2 : 1.6,
      dashArray: isOcean ? null : '5 5',
      fillColor: f.properties.fill,
      fillOpacity: isOcean ? 0.07 : 0.025,
      opacity: isOcean ? 0.98 : 0.72,
    }};
  }},
}});
zoneLayer.addTo(map);

document.getElementById('chk-zones').addEventListener('change', e => {{
  e.target.checked ? zoneLayer.addTo(map) : map.removeLayer(zoneLayer);
}});

// ── Grid layer ────────────────────────────────────────────────────────────
let gridMode = 'typology';
let scenario = 'B';
function fieldFor(mode) {{
  if (mode === 'nai') return 'NAI_raw';
  if (mode === 'delta') return 'Delta_raw';
  if (mode === 'population') return 'population';
  if (mode === 'density') return 'population_density';
  if (mode === 'exposure') return 'population_exposure';
  if (mode === 'boundary') return 'boundary_side';
  if (mode === 'quality') return 'data_quality_grade';
  if (mode === 'typology') return null;
  if (scenario === 'difference') return mode === 'smci' ? 'Delta_raw' : `${{mode.toUpperCase()}}_delta_raw`;
  if (mode === 'smci') return scenario === 'A' ? 'SMCI_A_raw' : 'SMCI_raw';
  return scenario === 'A' ? `${{mode.toUpperCase()}}_A_raw` : `${{mode.toUpperCase()}}_raw`;
}}

function gridStyle(f) {{
  const p = f.properties;
  let fill = p.color || '#ccc';
  if (gridMode === 'typology' && scenario === 'difference') {{
    fill = {{'No class change':'#9e9e9e','Moved toward Integrated Capability':'#1b9e77','Moved away from Integrated Capability':'#d95f02','Changed between intermediate classes':'#7570b3'}}[p.typology_transition] || '#9e9e9e';
  }} else if (gridMode === 'boundary') {{
    fill = {{'Inside':'#2c7fb8','Outside':'#fdbb84','Boundary-straddling':'#7fcdbb'}}[p.boundary_side] || '#808080';
  }} else if (gridMode === 'quality') {{
    fill = {{'A':'#1b9e77','B':'#66a61e','C':'#e6ab02','D':'#d95f02','No local POI':'#7570b3'}}[p.data_quality_grade] || '#808080';
  }}
  if (gridMode !== 'typology') {{
    const m = METRIC_META[gridMode];
    const value = p[fieldFor(gridMode)];
    if (gridMode === 'boundary' || gridMode === 'quality') return {{fillColor:fill, fillOpacity:0.70, color:'#000', weight:0.4, opacity:0.55}};
    if (value === null || value === undefined) return {{fillColor:'#808080', fillOpacity:0.45, color:'#fff', weight:0.8, dashArray:'3 3'}};
    if (value === 0 && gridMode !== 'delta') return {{fillColor:'#7f7f7f', fillOpacity:0.75, color:'#fff', weight:0.9, dashArray:'3 3'}};
    fill = paletteColor(norm(value, m.lo, m.hi), gridMode === 'delta' ? DELTA : VIRIDIS);
  }}
  return {{fillColor:fill, fillOpacity:0.68, color:'#000', weight:0.3, opacity:0.45}};
}}

const BADGE_COLORS = {{
  'Integrated Capability': ['#2ecc71','#1a1a1a'],
  'Fragmented Capability': ['#f39c12','#1a1a1a'],
  'Transit-Dependent':     ['#3498db','#fff'],
  'Motorcycle Lock-in':    ['#e74c3c','#fff'],
}};

const METRIC_KEYS = {{
  typology: null,
  nai: 'NAI_raw',
  smci: 'SMCI_raw',
  mai: 'MAI_raw',
  rac: 'RAC_raw',
  delta: 'Delta_raw',
  population: 'population',
  density: 'population_density',
  exposure: 'population_exposure',
  boundary: 'boundary_side',
  quality: 'data_quality_grade',
}};

function modeHelp(mode) {{
  if (mode === 'typology') {{
    return `
      <b>${{scenario === 'difference' ? 'Typology transition: Scenario B minus A' : 'Typology ' + scenario}}</b><br>
      Four classes combine local walking access (NAI) with metropolitan competitiveness (MCS).
      Green/orange/blue/red are categories, not a heat scale. Click any cell for its metrics.`;
  }}
  const m = METRIC_META[mode];
  return `
    <b>${{m.label}} heatmap</b><br>
    Lower value to higher value; exact values remain available in the selected-cell panel.<br>
    ${{m.how}}<br>
    <span style="color:#78909c;">Current range: ${{m.lo.toFixed(4)}} to ${{m.hi.toFixed(4)}}. Click any cell for exact values.</span>`;
}}

function layerDescription(mode) {{
  if (mode === 'typology') {{
    return `<b>Selected: ${{scenario === 'difference' ? 'Typology transition' : 'Typology ' + scenario}}</b><br>
      This is the final classification map for Scenario B. It groups cells into Integrated Capability,
      Fragmented Capability, Transit-Dependent, and Motorcycle Lock-in by combining local access (NAI)
      with metropolitan competitiveness. It is categorical, so the colors are class labels rather than
      a cold-to-hot heat scale.`;
  }}
  const m = METRIC_META[mode];
  return `<b>Selected: ${{m.label}}</b><br>${{m.long}}<br><span style="color:#9fb7d8;">${{m.how}}</span>`;
}}

function updateActiveDescription(mode) {{
  document.getElementById('active-layer-desc').innerHTML = layerDescription(mode);
}}

function heatPosition(mode, value) {{
  if (mode === 'typology' || mode === 'boundary' || mode === 'quality') return '';
  const m = METRIC_META[mode];
  const t = norm(value, m.lo, m.hi);
  if (t < 0.25) return 'low / cold';
  if (t < 0.50) return 'lower-middle';
  if (t < 0.75) return 'upper-middle';
  return 'high / warm';
}}

function setDefaultInfo() {{
  if (selectedCellFeature) {{
    renderSelectedCell(selectedCellFeature);
  }} else {{
    document.getElementById('info-panel').innerHTML = modeHelp(gridMode);
  }}
}}

function comparisonBar(label, a, b) {{
  if (a === null || b === null || a === undefined || b === undefined) return '';
  const max = Math.max(a, b, 1e-9);
  return `<div class="comparison-row"><span>${{label}}</span><div class="comparison-bar" title="Scenario A: ${{a.toFixed(4)}}"><div class="comparison-fill-a" style="width:${{(a / max) * 100}}%"></div></div><div class="comparison-bar" title="Scenario B: ${{b.toFixed(4)}}"><div class="comparison-fill-b" style="width:${{(b / max) * 100}}%"></div></div></div>`;
}}

function componentBar(label, value) {{
  if (value === null || value === undefined) return '';
  return `<div class="comparison-row"><span>${{label}}</span><div class="comparison-bar" style="grid-column:span 2" title="Scenario B normalized value: ${{value.toFixed(4)}}"><div class="comparison-fill-b" style="width:${{Math.max(0, Math.min(1, value)) * 100}}%"></div></div></div>`;
}}

function renderSelectedCell(f) {{
    const p = f.properties;
    const activeTypology = scenario === 'A' ? p.typology_A : p.typology_B;
    const [bg,fg] = BADGE_COLORS[activeTypology] || ['#555','#fff'];
    const activeKey = METRIC_KEYS[gridMode];
    const activeValue = activeKey ? p[fieldFor(gridMode)] : null;
    const activeMetric = activeKey ? `
      <div class="metric" style="grid-column:span 2;border:1px solid #4fc3f7;">
        <div class="val">${{activeValue.toFixed ? activeValue.toFixed(4) : activeValue}}</div>
        <div class="lbl">${{METRIC_META[gridMode].label}} — ${{heatPosition(gridMode, activeValue)}} on current heatmap</div>
      </div>` : '';
    document.getElementById('info-panel').innerHTML = `
      <b>Cell #${{p.cell_id}}</b>&nbsp;
      <span class="badge" style="background:${{bg}};color:${{fg}};">${{activeTypology}}</span>
      <div style="margin:5px 0;color:#b0c4de;">Scenario A: ${{p.typology_A}} &rarr; Scenario B: ${{p.typology_B}}<br>${{p.typology_transition}}</div>
      <div class="metric-grid">
        ${{activeMetric}}
        <div class="metric">
          <div class="val">${{p.NAI}}</div>
          <div class="lbl">NAI &mdash; walkable POIs</div>
        </div>
        <div class="metric">
          <div class="val">${{p.MAI_B}}</div>
          <div class="lbl">MAI_B &mdash; metro opp.</div>
        </div>
        <div class="metric">
          <div class="val">${{p.RAC_B}}</div>
          <div class="lbl">RAC_B &mdash; competitiveness</div>
        </div>
        <div class="metric">
          <div class="val">${{p.SMCI_B}}</div>
          <div class="lbl">SMCI_B</div>
        </div>
        <div class="metric" style="grid-column:span 2;">
          <div class="val">${{p.Delta_SMCI}}</div>
          <div class="lbl">&Delta;SMCI &mdash; modeled Scenario B minus A</div>
        </div>
        <div class="metric">
          <div class="val">${{p.population === null ? 'N/A' : p.population.toFixed(0)}}</div>
          <div class="lbl">Population estimate</div>
        </div>
        <div class="metric">
          <div class="val">${{p.distance_to_boundary_m === null ? 'N/A' : p.distance_to_boundary_m.toFixed(0) + ' m'}}</div>
          <div class="lbl">${{p.boundary_side}} (${{p.boundary_band}})</div>
        </div>
        <div class="metric">
          <div class="val">${{p.population_density === null ? 'N/A' : p.population_density.toFixed(0)}}</div>
          <div class="lbl">Population density / km2</div>
        </div>
        <div class="metric">
          <div class="val">${{p.data_quality_grade || 'N/A'}}</div>
          <div class="lbl">Data-quality grade</div>
        </div>
        <div class="comparison">
          <b>Scenario comparison</b> <span style="color:#8da0cb">A</span> / <span style="color:#66c2a5">B</span>
          ${{comparisonBar('MAI', p.MAI_A_raw, p.MAI_raw)}}
          ${{comparisonBar('RAC', p.RAC_A_raw, p.RAC_raw)}}
          ${{comparisonBar('SMCI', p.SMCI_A_raw, p.SMCI_raw)}}
          <div style="margin-top:6px"><b>Scenario B component balance</b></div>
          ${{componentBar('NAI', p.NAI_norm)}}
          ${{componentBar('MAI', p.MAI_norm)}}
          ${{componentBar('RAC', p.RAC_norm)}}
        </div>
      </div>`;
}}

function onEachCell(f, layer) {{
  layer.on('click', () => {{
    selectedCellFeature = f;
    renderSelectedCell(f);
  }});
  layer.on('mouseover', () => layer.setStyle({{weight:1.5, color:'#fff', opacity:0.9}}));
  layer.on('mouseout',  () => {{
    if (gridLayer.hasLayer(layer)) gridLayer.resetStyle(layer);
    else zeroNaiLayer.resetStyle(layer);
  }});
}}

const gridLayer = L.geoJSON(GRID, {{style:gridStyle, onEachFeature:onEachCell}});
gridLayer.addTo(map);
zoneLayer.bringToFront();
boundaryLayer.bringToFront();

const zeroNaiLayer = L.geoJSON(ZERO_NAI, {{
  style: {{
    color: '#ffffff',
    weight: 2.0,
    dashArray: '2 4',
    fillColor: '#ffffff',
    fillOpacity: 0.09,
    opacity: 0.95,
  }},
  onEachFeature: onEachCell,
}});

document.getElementById('chk-zero-nai').addEventListener('change', e => {{
  if (e.target.checked) {{
    zeroNaiLayer.addTo(map);
    zeroNaiLayer.bringToFront();
  }} else {{
    map.removeLayer(zeroNaiLayer);
  }}
}});

// LISA is an overlay, not a replacement for the underlying SMCI/typology layer.
const lisaLayer = L.geoJSON(LISA, {{
  style: f => ({{
    color: '#ffffff',
    weight: 0.8,
    fillColor: f.properties.color,
    fillOpacity: f.properties.cluster === 'Not Significant' ? 0.20 : 0.68,
  }}),
  onEachFeature: (f, layer) => {{
    const p = f.properties;
    layer.bindTooltip(
      `<b>Cell #${{p.cell_id}}</b><br>SMCI_B LISA: <b>${{p.cluster}}</b><br>FDR q = ${{p.q_value.toFixed(4)}}`,
      {{sticky: true}}
    );
    layer.bindPopup(
      `<b>SMCI_B LISA diagnostic</b><br>` +
      `Cell #${{p.cell_id}}: <b>${{p.cluster}}</b><br>` +
      `Local Moran's I: ${{p.local_i.toFixed(4)}}<br>` +
      `Permutation p: ${{p.p_value.toFixed(4)}}; FDR q: ${{p.q_value.toFixed(4)}}<br><br>` +
      `<small>Queen contiguity, 9,999 permutations. This is spatial association, not causal evidence.</small>`
    );
  }},
}});

function setLayerVisible(layer, visible) {{
  if (visible) {{
    layer.addTo(map);
    layer.bringToFront();
  }} else {{
    map.removeLayer(layer);
  }}
}}

document.getElementById('chk-lisa').addEventListener('change', e => {{
  setLayerVisible(lisaLayer, e.target.checked);
}});

function crossingLayer(mode, color) {{
  return L.geoJSON(CROSSINGS, {{
    filter: f => f.properties.mode === mode,
    style: {{color, weight: 3.5, opacity: 0.9, lineCap: 'round'}},
    onEachFeature: (f, layer) => {{
      const p = f.properties;
      layer.bindTooltip(
        `<b>${{mode === 'walking' ? 'Walking' : 'Motorcycle'}} modeled crossing</b><br>` +
        `${{p.highway}} &middot; ${{p.length_m.toFixed(0)}} m<br>` +
        `Approx. edge betweenness: ${{p.approx_edge_betweenness.toFixed(4)}}<br>` +
        `<small>OSM access status: ${{p.access_status}}; not gate validation.</small>`,
        {{sticky: true}}
      );
    }},
  }});
}}

const walkingCrossingsLayer = crossingLayer('walking', '#238b45');
const motorcycleCrossingsLayer = crossingLayer('motorcycle', '#756bb1');
document.getElementById('chk-walk-crossings').addEventListener('change', e => {{
  setLayerVisible(walkingCrossingsLayer, e.target.checked);
}});
document.getElementById('chk-motorcycle-crossings').addEventListener('change', e => {{
  setLayerVisible(motorcycleCrossingsLayer, e.target.checked);
}});

document.getElementById('chk-grid').addEventListener('change', e => {{
  if (e.target.checked) {{
    gridLayer.addTo(map);
    zoneLayer.bringToFront();
    boundaryLayer.bringToFront();
    if (document.getElementById('chk-zero-nai').checked) zeroNaiLayer.bringToFront();
  }} else {{
    map.removeLayer(gridLayer);
  }}
}});

// ── Continuous legend update ───────────────────────────────────────────────
function updateContLegend(mode) {{
  const typoLeg = document.getElementById('typo-legend');
  const contLeg = document.getElementById('cont-legend');
  if (mode === 'typology') {{
    typoLeg.style.display = '';
    contLeg.style.display = 'none';
    return;
  }}
  typoLeg.style.display = 'none';
  contLeg.style.display = '';

  const m = METRIC_META[mode];
  document.getElementById('leg-unit').textContent = m.unit.toUpperCase();
  document.getElementById('leg-min').textContent  = m.lo.toFixed(4);
  document.getElementById('leg-max').textContent  = m.hi.toFixed(4);
  document.getElementById('leg-how').textContent  = m.how;
  document.getElementById('leg-desc').textContent = m.desc;

  // Draw mini histogram
  const histEl = document.getElementById('leg-hist');
  histEl.innerHTML = '';
  const maxBin = Math.max(...m.hist, 1);
  m.hist.forEach((count, i) => {{
    const t = i / (m.hist.length - 1 || 1);
    const bar = document.createElement('div');
    bar.className = 'bar';
    bar.style.height = (count / maxBin * 100) + '%';
    bar.style.background = paletteColor(t, mode === 'delta' ? DELTA : VIRIDIS);
    bar.title = `n=${{count}}`;
    histEl.appendChild(bar);
  }});
}}

document.getElementById('grid-mode').addEventListener('change', e => {{
  gridMode = e.target.value;
  const differenceOption = document.querySelector('#scenario-sel option[value="difference"]');
  differenceOption.disabled = gridMode === 'nai';
  if (gridMode === 'nai' && scenario === 'difference') {{ scenario = 'B'; document.getElementById('scenario-sel').value = 'B'; }}
  gridLayer.setStyle(gridStyle);
  updateContLegend(gridMode);
  updateActiveDescription(gridMode);
  setDefaultInfo();
  updateUrlState();
}});
document.getElementById('scenario-sel').addEventListener('change', e => {{
  scenario = e.target.value;
  if (scenario === 'difference' && gridMode === 'nai') {{
    scenario = 'B';
    e.target.value = 'B';
  }}
  gridLayer.setStyle(gridStyle);
  updateContLegend(gridMode);
  updateActiveDescription(gridMode);
  setDefaultInfo();
  updateUrlState();
}});
function updateUrlState() {{
  const state = new URLSearchParams(window.location.search);
  state.set('scenario', scenario); state.set('metric', gridMode);
  history.replaceState(null, '', `${{window.location.pathname}}?${{state.toString()}}`);
}}
const initialState = new URLSearchParams(window.location.search);
if (['A','B','difference'].includes(initialState.get('scenario'))) {{ scenario = initialState.get('scenario'); document.getElementById('scenario-sel').value = scenario; }}
if (METRIC_META[initialState.get('metric')] || initialState.get('metric') === 'typology') {{ gridMode = initialState.get('metric'); document.getElementById('grid-mode').value = gridMode; }}
updateContLegend(gridMode);
updateActiveDescription(gridMode);
setDefaultInfo();

// ── POI layer ─────────────────────────────────────────────────────────────
function poiIcon(color) {{
  return L.divIcon({{
    className: '',
    html: `<svg width="11" height="11" viewBox="0 0 11 11">
      <circle cx="5.5" cy="5.5" r="4.5" fill="${{color}}" stroke="#fff" stroke-width="1.5"/>
    </svg>`,
    iconSize: [11,11], iconAnchor: [5.5,5.5],
  }});
}}

const poiLayer = L.geoJSON(POIS, {{
  pointToLayer: (f,ll) => L.marker(ll, {{icon: poiIcon(f.properties.color)}}),
  onEachFeature: (f,layer) => {{
    const p = f.properties;
    layer.bindTooltip(
      `<b>${{p.name}}</b><br><span style="color:#aaa">${{p.domain}}</span> &middot; ${{p.source}}`,
      {{sticky:true, className:'leaflet-tooltip'}}
    );
  }},
}});
document.getElementById('chk-poi').addEventListener('change', e => {{
  e.target.checked ? poiLayer.addTo(map) : map.removeLayer(poiLayer);
}});

// ── Route layer ───────────────────────────────────────────────────────────
const routeLayer = L.geoJSON(ROUTES, {{
  style: f => ({{color:f.properties.color, weight:3.5, opacity:0.85, lineJoin:'round'}}),
  onEachFeature: (f,layer) => {{
    layer.bindTooltip(
      `VinBus <b>${{f.properties.ref}}</b><br>${{f.properties.name}}`,
      {{sticky:true}}
    );
  }},
}});
document.getElementById('chk-routes').addEventListener('change', e => {{
  e.target.checked ? routeLayer.addTo(map) : map.removeLayer(routeLayer);
}});

// ── Stop icons ────────────────────────────────────────────────────────────
function stopIcon(color, size=9) {{
  return L.divIcon({{
    className: '',
    html: `<svg width="${{size}}" height="${{size}}">
      <rect width="${{size}}" height="${{size}}" rx="2" fill="${{color}}" stroke="#fff" stroke-width="1.2"/>
    </svg>`,
    iconSize: [size,size], iconAnchor: [size/2,size/2],
  }});
}}

const vstopLayer = L.geoJSON(VSTOPS, {{
  pointToLayer: (f,ll) => L.marker(ll, {{icon: stopIcon('#1abc9c')}}),
  onEachFeature: (f,layer) => layer.bindTooltip(
    `<b>${{f.properties.name}}</b><br><span style="color:#aaa">VinBus stop &middot; ID ${{f.properties.stop_id}}</span>`,
    {{sticky:true}}
  ),
}});
document.getElementById('chk-vstops').addEventListener('change', e => {{
  e.target.checked ? vstopLayer.addTo(map) : map.removeLayer(vstopLayer);
}});

const hstopLayer = L.geoJSON(HSTOPS, {{
  pointToLayer: (f,ll) => L.marker(ll, {{icon: stopIcon('#3498db', 8)}}),
  onEachFeature: (f,layer) => layer.bindTooltip(
    `<b>${{f.properties.name}}</b><br><span style="color:#aaa">Hanoi GTFS 2018 — Network B baseline</span>`,
    {{sticky:true}}
  ),
}});

document.getElementById('chk-hstops').addEventListener('change', e => {{
  e.target.checked ? hstopLayer.addTo(map) : map.removeLayer(hstopLayer);
}});

// ── Initial fit: union of grid + all routes so OCP1/OCP2 (east of grid) visible ──
function selectMapState(nextScenario, nextMetric) {{
  scenario = nextScenario; gridMode = nextMetric;
  document.getElementById('scenario-sel').value = scenario;
  document.getElementById('grid-mode').value = gridMode;
  gridLayer.setStyle(gridStyle); updateContLegend(gridMode); updateActiveDescription(gridMode); setDefaultInfo(); updateUrlState();
}}
document.querySelectorAll('[data-preset]').forEach(button => button.addEventListener('click', () => {{
  const preset = button.dataset.preset;
  if (preset === 'capability') selectMapState('B', 'typology');
  if (preset === 'comparison') selectMapState('difference', 'delta');
  if (preset === 'exposure') selectMapState('B', 'exposure');
  if (preset === 'boundary') selectMapState('B', 'boundary');
}}));
document.getElementById('fit-study').addEventListener('click', () => map.fitBounds(gridLayer.getBounds(), {{padding:[20,20]}}));
document.getElementById('fit-project').addEventListener('click', () => map.fitBounds(zoneLayer.getBounds(), {{padding:[20,20]}}));
document.getElementById('fit-network').addEventListener('click', () => {{ routeLayer.addTo(map); document.getElementById('chk-routes').checked = true; map.fitBounds(routeLayer.getBounds(), {{padding:[20,20]}}); }});

const STUDY_BOUNDS = [
  [{GRID_LAT_MIN:.4f}, {GRID_LON_MIN:.4f}],
  [{GRID_LAT_MAX:.4f}, {GRID_LON_MAX:.4f}],
];
map.fitBounds(STUDY_BOUNDS, {{padding:[20,20]}});
</script>
</body>
</html>"""

os.makedirs(os.path.dirname(OUT_HTML), exist_ok=True)
with open(OUT_HTML, "w", encoding="utf-8") as f:
    f.write(HTML)

size_kb = os.path.getsize(OUT_HTML) // 1024
print(f"\nDone -> {OUT_HTML}  ({size_kb} KB)")
print(f"  VinBus stops in area : {len(stop_features)}  (was 1289)")
print(f"  Hanoi GTFS stops     : {len(hanoi_stop_features)}  (was 2422)")
print("Open in any browser.")
