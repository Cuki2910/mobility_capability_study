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

import geopandas as gpd
import pandas as pd
from shapely.geometry import mapping
from shapely.ops import unary_union

# ── paths ──────────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRID_GPKG    = os.path.join(ROOT, "data", "interim", "pilot_grid.gpkg")
METRICS_CSV  = os.path.join(ROOT, "data", "processed", "pilot_metrics.csv")
POIS_GPKG    = os.path.join(ROOT, "data", "interim", "merged_pois_economic.gpkg")
VINBUS_GEOM  = os.path.join(ROOT, "data", "raw", "vinbus_overpass_relations_geom.json")
VINBUS_STOPS = os.path.join(ROOT, "data", "raw", "vinbus_pseudo_gtfs_fixed", "stops.txt")
VINBUS_ROUTES= os.path.join(ROOT, "data", "raw", "vinbus_pseudo_gtfs_fixed", "routes.txt")
OUT_HTML     = os.path.join(ROOT, "outputs", "maps", "ocean_park_interactive.html")

# ── 1. Grid + metrics ──────────────────────────────────────────────────────
print("Reading grid ...")
grid = gpd.read_file(GRID_GPKG).to_crs("EPSG:4326")
metrics = pd.read_csv(METRICS_CSV)
if "cell_id" not in grid.columns:
    grid = grid.reset_index().rename(columns={"index": "cell_id"})
grid["cell_id"] = grid["cell_id"].astype(int)
metrics["cell_id"] = metrics["cell_id"].astype(int)
gdf = grid.merge(metrics, on="cell_id", how="left")

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
study_union = unary_union(grid.geometry)
# Use convex hull for a clean presentation outline; keep union as fallback
study_boundary_geom = study_union.convex_hull
study_boundary_geojson = {
    "type": "FeatureCollection",
    "features": [{
        "type": "Feature",
        "geometry": mapping(study_boundary_geom),
        "properties": {"name": "Pilot study area (462 grid cells, 250 m)"},
    }]
}

TYPOLOGY_COLORS = {
    "Integrated Capability": "#2ecc71",
    "Fragmented Capability": "#f39c12",
    "Transit-Dependent":     "#3498db",
    "Motorcycle Lock-in":    "#e74c3c",
}
DEFAULT_COLOR = "#cccccc"

def fmt(v):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "N/A"
    if isinstance(v, float):
        return f"{v:.4f}"
    return str(v)

grid_features = []
for _, row in gdf.iterrows():
    if row.geometry is None:
        continue
    typ = row.get("typology_B", "")
    color = TYPOLOGY_COLORS.get(str(typ), DEFAULT_COLOR)
    def _f(col):
        v = row.get(col)
        return float(v) if pd.notna(v) else 0.0
    grid_features.append({
        "type": "Feature",
        "geometry": mapping(row.geometry),
        "properties": {
            "cell_id":    int(row["cell_id"]),
            "typology_B": str(typ),
            "color":      color,
            "NAI":        fmt(row.get("NAI")),
            "MAI_B":      fmt(row.get("MAI_B")),
            "RAC_B":      fmt(row.get("RAC_B")),
            "SMCI_B":     fmt(row.get("SMCI_B")),
            "Delta_SMCI": fmt(row.get("Delta_SMCI")),
            "NAI_raw":    _f("NAI"),
            "MAI_raw":    _f("MAI_B"),
            "RAC_raw":    _f("RAC_B"),
            "SMCI_raw":   _f("SMCI_B"),
            "Delta_raw":  _f("Delta_SMCI"),
        },
    })
grid_geojson = {"type": "FeatureCollection", "features": grid_features}
print(f"  {len(grid_features)} grid cells")

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
    cat     = str(row.get("category", "") or "").lower()
    amenity = str(row.get("amenity",  "") or "").lower()
    shop    = str(row.get("shop",     "") or "").lower()
    edu     = str(row.get("education","") or "").lower()
    office  = str(row.get("office",   "") or "").lower()
    landuse = str(row.get("landuse",  "") or "").lower()
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
def make_histogram(features, key, n_bins=20):
    vals = [f["properties"][key] for f in features
            if isinstance(f["properties"].get(key), (int, float)) and f["properties"][key] > 0]
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

nai_hist,   nai_lo,   nai_hi   = make_histogram(grid_features, "NAI_raw",   20)
smci_hist,  smci_lo,  smci_hi  = make_histogram(grid_features, "SMCI_raw",  20)
mai_hist,   mai_lo,   mai_hi   = make_histogram(grid_features, "MAI_raw",   20)
rac_hist,   rac_lo,   rac_hi   = make_histogram(grid_features, "RAC_raw",   20)
delta_hist, delta_lo, delta_hi = make_histogram(grid_features, "Delta_raw", 20)

METRIC_META = {
    "nai":   {"label": "NAI",        "unit": "count",    "desc": "Walkable POIs within 800m network distance",
              "hist": nai_hist,   "lo": nai_lo,   "hi": nai_hi},
    "smci":  {"label": "SMCI_B",     "unit": "index",    "desc": "Sustainable Mobility Capability Index (Scenario B with VinBus)",
              "hist": smci_hist,  "lo": smci_lo,  "hi": smci_hi},
    "mai":   {"label": "MAI_B",      "unit": "weighted", "desc": "Metropolitan Accessibility Index — magnitude-weighted, walk+transit, 60 min cutoff",
              "hist": mai_hist,   "lo": mai_lo,   "hi": mai_hi},
    "rac":   {"label": "RAC_B",      "unit": "ratio",    "desc": "Relative Accessibility Competitiveness = geom. mean(RAC_time, RAC_opp); higher = transit more competitive vs motorcycle",
              "hist": rac_hist,   "lo": rac_lo,   "hi": rac_hi},
    "delta": {"label": "Delta_SMCI", "unit": "index",    "desc": "SMCI change from adding VinBus (Scenario B minus A); positive = VinBus improves capability",
              "hist": delta_hist, "lo": delta_lo, "hi": delta_hi},
}

# ── 7. Serialise ──────────────────────────────────────────────────────────
def js(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':'))

map_center_lat = (GRID_LAT_MIN + GRID_LAT_MAX) / 2
map_center_lon = (GRID_LON_MIN + GRID_LON_MAX) / 2

# ── 8. Build HTML ──────────────────────────────────────────────────────────
print("Building HTML ...")

HTML = f"""<!DOCTYPE html>
<html lang="vi">
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
#info-panel{{
  background:#0d2137;border-radius:6px;padding:9px 10px;margin-top:8px;
  font-size:11px;min-height:70px;line-height:1.65;color:#b0c4de;
}}
#info-panel b{{color:#4fc3f7;}}
.metric-grid{{display:grid;grid-template-columns:1fr 1fr;gap:5px;margin-top:7px;}}
.metric{{background:#112847;border-radius:5px;padding:6px 8px;}}
.metric .val{{font-size:14px;font-weight:700;color:#4fc3f7;}}
.metric .lbl{{font-size:9.5px;color:#7a9ec8;margin-top:1px;}}
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
#cont-legend .leg-unit{{
  font-size:9.5px;color:#4fc3f7;font-weight:600;
  text-transform:uppercase;letter-spacing:.4px;margin-bottom:2px;
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
    <label><input type="checkbox" id="chk-grid" checked> Show 462-cell grid</label>
    <label><input type="checkbox" id="chk-boundary" checked>
      <span class="swatch" style="background:transparent;border:2px dashed #f39c12;"></span>
      Study area boundary
    </label>
    <select id="grid-mode">
      <option value="typology" selected>Typology B (primary)</option>
      <option value="smci">SMCI_B — capability index</option>
      <option value="nai">NAI — walkable POIs (count)</option>
      <option value="mai">MAI_B — metro opportunity</option>
      <option value="rac">RAC_B — transit vs motorcycle</option>
      <option value="delta">Delta SMCI — VinBus effect</option>
    </select>

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
      <div class="leg-desc" id="leg-desc"></div>
    </div>
  </div>

  <div class="section">
    <h2>Points of Interest (208)</h2>
    <label><input type="checkbox" id="chk-poi" checked> Show POIs</label>
    <div style="margin-top:5px;">
      <div class="legend-row"><span class="swatch" style="background:#9b59b6;border-radius:50%;"></span>Education (incl. higher ed)</div>
      <div class="legend-row"><span class="swatch" style="background:#e74c3c;border-radius:50%;"></span>Health</div>
      <div class="legend-row"><span class="swatch" style="background:#e67e22;border-radius:50%;"></span>Economic / Office</div>
      <div class="legend-row"><span class="swatch" style="background:#27ae60;border-radius:50%;"></span>Daily needs</div>
      <div class="legend-row"><span class="swatch" style="background:#f1c40f;border-radius:50%;"></span>Retail</div>
      <div class="legend-row"><span class="swatch" style="background:#7f8c8d;border-radius:50%;"></span>Transport / Other</div>
    </div>
    <div style="font-size:10px;color:#546e7a;margin-top:4px;">Sources: OSM + Overture Places + OSM landuse (Decision #18)</div>
  </div>

  <div class="section">
    <h2>Transit Networks</h2>
    <label><input type="checkbox" id="chk-routes" checked>
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
    <label><input type="checkbox" id="chk-vstops" checked>
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
    <div id="info-panel">Click any grid cell to see its metrics.</div>
  </div>

  <div class="section" style="margin-top:6px;font-size:10px;color:#455a64;line-height:1.5;">
    Methodology: proposal/proposal_v7.md &sect;3<br>
    Pipeline: scripts/run_pilot_metrics.py<br>
    SMCI = NAI<sub>norm</sub> &times; MAI<sub>norm</sub> &times; RAC<sub>norm</sub>
  </div>
</div>

<div id="map"></div>
</div>

<script>
// ── Embedded GeoJSON data ──────────────────────────────────────────────────
const GRID     = {js(grid_geojson)};
const BOUNDARY = {js(study_boundary_geojson)};
const POIS     = {js(poi_geojson)};
const ROUTES   = {js(route_geojson)};
const VSTOPS   = {js(stops_geojson)};
const HSTOPS   = {js(hanoi_stops_geojson)};

// ── Metric metadata (for continuous legend) ────────────────────────────────
const METRIC_META = {js(METRIC_META)};

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

const SPECTRAL = [
  [49,54,149],[69,117,180],[116,173,209],[171,217,233],[224,243,248],
  [255,255,191],[254,224,144],[253,174,97],[244,109,67],[215,48,39],[165,0,38]
];
function spectralColor(t) {{
  t = clamp(t, 0, 0.9999);
  const n = SPECTRAL.length - 1;
  const i = Math.floor(t * n);
  const f = t * n - i;
  const [r1,g1,b1] = SPECTRAL[i];
  const [r2,g2,b2] = SPECTRAL[Math.min(i+1,n)];
  return `rgb(${{Math.round(lerp(r1,r2,f))}},${{Math.round(lerp(g1,g2,f))}},${{Math.round(lerp(b1,b2,f))}})`;
}}
function norm(v,lo,hi){{ return hi===lo ? 0.5 : clamp((v-lo)/(hi-lo),0,1); }}

// ── Study area boundary ────────────────────────────────────────────────────
const boundaryLayer = L.geoJSON(BOUNDARY, {{
  style: {{
    color: '#f39c12', weight: 2.5, dashArray: '6 4',
    fillColor: 'transparent', fillOpacity: 0,
  }},
}});
boundaryLayer.addTo(map);

document.getElementById('chk-boundary').addEventListener('change', e => {{
  e.target.checked ? boundaryLayer.addTo(map) : map.removeLayer(boundaryLayer);
}});

// ── Grid layer ────────────────────────────────────────────────────────────
let gridMode = 'typology';

function gridStyle(f) {{
  const p = f.properties;
  let fill = p.color || '#ccc';
  if (gridMode !== 'typology') {{
    const m = METRIC_META[gridMode];
    fill = spectralColor(norm(p[gridMode==='nai'?'NAI_raw':gridMode==='smci'?'SMCI_raw':gridMode==='mai'?'MAI_raw':gridMode==='rac'?'RAC_raw':'Delta_raw'], m.lo, m.hi));
  }}
  return {{fillColor:fill, fillOpacity:0.68, color:'#000', weight:0.3, opacity:0.45}};
}}

const BADGE_COLORS = {{
  'Integrated Capability': ['#2ecc71','#1a1a1a'],
  'Fragmented Capability': ['#f39c12','#1a1a1a'],
  'Transit-Dependent':     ['#3498db','#fff'],
  'Motorcycle Lock-in':    ['#e74c3c','#fff'],
}};

function onEachCell(f, layer) {{
  layer.on('click', () => {{
    const p = f.properties;
    const [bg,fg] = BADGE_COLORS[p.typology_B] || ['#555','#fff'];
    document.getElementById('info-panel').innerHTML = `
      <b>Cell #${{p.cell_id}}</b>&nbsp;
      <span class="badge" style="background:${{bg}};color:${{fg}};">${{p.typology_B}}</span>
      <div class="metric-grid">
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
          <div class="lbl">&Delta;SMCI &mdash; VinBus effect (Scenario B &minus; A)</div>
        </div>
      </div>`;
  }});
  layer.on('mouseover', () => layer.setStyle({{weight:1.5, color:'#fff', opacity:0.9}}));
  layer.on('mouseout',  () => gridLayer.resetStyle(layer));
}}

const gridLayer = L.geoJSON(GRID, {{style:gridStyle, onEachFeature:onEachCell}});
gridLayer.addTo(map);

document.getElementById('chk-grid').addEventListener('change', e => {{
  e.target.checked ? gridLayer.addTo(map) : map.removeLayer(gridLayer);
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
    bar.style.background = spectralColor(t);
    bar.title = `n=${{count}}`;
    histEl.appendChild(bar);
  }});
}}

document.getElementById('grid-mode').addEventListener('change', e => {{
  gridMode = e.target.value;
  gridLayer.setStyle(gridStyle);
  updateContLegend(gridMode);
}});

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
poiLayer.addTo(map);

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
routeLayer.addTo(map);

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
vstopLayer.addTo(map);

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
const FULL_BOUNDS = [
  [{route_bounds['lat_min']:.4f}, {route_bounds['lon_min']:.4f}],
  [{route_bounds['lat_max']:.4f}, {route_bounds['lon_max']:.4f}],
];
map.fitBounds(FULL_BOUNDS, {{padding:[20,20]}});
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
