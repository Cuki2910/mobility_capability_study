"""
Interactive HTML map — Vinhomes Ocean Park & Smart City combined.
"""
import json, math, os, sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import geopandas as gpd
import pandas as pd
from shapely.geometry import mapping, box
from shapely.ops import unary_union

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

VINBUS_GEOM  = os.path.join(ROOT, "data", "raw", "vinbus_overpass_relations_geom.json")
VINBUS_STOPS = os.path.join(ROOT, "data", "raw", "vinbus_pseudo_gtfs_fixed", "stops.txt")
VINBUS_ROUTES= os.path.join(ROOT, "data", "raw", "vinbus_pseudo_gtfs_fixed", "routes.txt")
OUT_HTML     = os.path.join(ROOT, "outputs", "maps", "mobility_capability_combined.html")

TYPOLOGY_COLORS = {"Integrated Capability": "#2ecc71", "Fragmented Capability": "#f39c12", "Transit-Dependent": "#3498db", "Motorcycle Lock-in": "#e74c3c"}
DOMAIN_COLORS = {"education": "#9b59b6", "health": "#e74c3c", "economic": "#e67e22", "daily_needs": "#27ae60", "retail": "#f1c40f", "financial_service":"#8e44ad", "transportation": "#7f8c8d", "recreation": "#1abc9c"}

def fmt(v):
    if pd.isna(v): return "N/A"
    if isinstance(v, float): return f"{v:.4f}"
    return str(v)

def infer_domain(row):
    def _txt(key):
        val = row.get(key, "")
        if pd.isna(val): return ""
        text = str(val).strip().lower()
        return "" if text in {"nan", "none", "<na>"} else text
    cat, amenity, shop, edu, office, landuse = _txt("category"), _txt("amenity"), _txt("shop"), _txt("education"), _txt("office"), _txt("landuse")
    if cat in ("education","higher_ed") or "school" in amenity or "university" in amenity or edu: return "education"
    if cat == "health_and_medical" or amenity in ("hospital","clinic","pharmacy","doctors"): return "health"
    if cat in ("retail","financial_service") or shop or office or landuse in ("commercial","industrial"): return "economic"
    if amenity in ("restaurant","cafe","fast_food","marketplace"): return "daily_needs"
    if amenity == "park" or landuse == "park": return "recreation"
    if cat == "transportation": return "transportation"
    return "daily_needs"

def load_site(grid_path, metrics_path, strict_path, pois_path, core_path, core_name, second_core_path=None, second_core_name=None):
    print(f"Loading {core_name}...")
    grid = gpd.read_file(grid_path).to_crs("EPSG:4326")
    metrics = pd.read_csv(metrics_path)
    if "cell_id" not in grid.columns: grid = grid.reset_index().rename(columns={"index": "cell_id"})
    grid["cell_id"] = grid["cell_id"].astype(int)
    metrics["cell_id"] = metrics["cell_id"].astype(int)
    gdf = grid.merge(metrics, on="cell_id", how="left")
    
    bounds = grid.total_bounds
    GRID_LON_MIN, GRID_LAT_MIN, GRID_LON_MAX, GRID_LAT_MAX = bounds
    
    study_boundary_geom = unary_union(grid.geometry).convex_hull
    study_boundary_geojson = {"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": mapping(study_boundary_geom), "properties": {"name": "Study area"}}]}
    
    core_geom = gpd.read_file(core_path).to_crs("EPSG:4326").geometry.iloc[0] if os.path.exists(core_path) else study_boundary_geom
    zone_features = [{
        "type": "Feature",
        "geometry": mapping(core_geom),
        "properties": {"name": core_name, "zone": "Primary", "color": "#00e5ff", "fill": "#00e5ff"},
    }]
    if second_core_path and os.path.exists(second_core_path):
        second_geom = gpd.read_file(second_core_path).to_crs("EPSG:4326").geometry.iloc[0]
        zone_features.append({
            "type": "Feature",
            "geometry": mapping(second_geom),
            "properties": {"name": second_core_name or "Second zone", "zone": "Secondary", "color": "#ffca28", "fill": "#ffca28"},
        })
    else:
        context_geom = study_boundary_geom.difference(core_geom)
        zone_features.append({
            "type": "Feature",
            "geometry": mapping(context_geom),
            "properties": {"name": "Surrounding", "zone": "Context", "color": "#cfd8dc", "fill": "#cfd8dc"},
        })
    zone_boundary_geojson = {"type": "FeatureCollection", "features": zone_features}
    
    grid_features, zero_nai_features = [], []
    for _, row in gdf.iterrows():
        if row.geometry is None: continue
        typ = str(row.get("typology_B", ""))
        def _f(col): v = row.get(col); return float(v) if pd.notna(v) else 0.0
        feat = {"type": "Feature", "geometry": mapping(row.geometry), "properties": {
            "cell_id": int(row["cell_id"]), "typology_B": typ, "color": TYPOLOGY_COLORS.get(typ, "#ccc"),
            "NAI": fmt(row.get("NAI")), "MAI_B": fmt(row.get("MAI_B")), "RAC_B": fmt(row.get("RAC_B")), "SMCI_B": fmt(row.get("SMCI_B")), "Delta_SMCI": fmt(row.get("Delta_SMCI")),
            "NAI_raw": _f("NAI"), "MAI_raw": _f("MAI_B"), "RAC_raw": _f("RAC_B"), "SMCI_raw": _f("SMCI_B"), "Delta_raw": _f("Delta_SMCI")
        }}
        grid_features.append(feat)
        if _f("NAI") == 0.0: zero_nai_features.append(feat)
        
    pois_gdf = gpd.read_file(pois_path).to_crs("EPSG:4326")
    poi_features = []
    for _, row in pois_gdf.iterrows():
        geom = row.geometry
        if geom is None: continue
        if geom.geom_type != "Point": geom = geom.centroid
        lat, lon = geom.y, geom.x
        if not (GRID_LAT_MIN - 0.02 < lat < GRID_LAT_MAX + 0.02 and GRID_LON_MIN - 0.02 < lon < GRID_LON_MAX + 0.02): continue
        domain = infer_domain(row)
        poi_features.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [lon, lat]}, "properties": {
            "name": str(row.get("name") or row.get("name:vi") or row.get("id") or "POI"),
            "domain": domain, "category": str(row.get("category") or row.get("amenity") or row.get("shop") or ""), "color": DOMAIN_COLORS.get(domain, "#95a5a6")
        }})
        
    return {
        "bounds": [[GRID_LAT_MIN, GRID_LON_MIN], [GRID_LAT_MAX, GRID_LON_MAX]],
        "grid": {"type": "FeatureCollection", "features": grid_features},
        "zero_nai": {"type": "FeatureCollection", "features": zero_nai_features},
        "boundary": study_boundary_geojson, "zones": zone_boundary_geojson,
        "pois": {"type": "FeatureCollection", "features": poi_features}
    }

east_data = load_site(os.path.join(ROOT, "data", "interim", "pilot_grid.gpkg"), os.path.join(ROOT, "data", "processed", "pilot_metrics.csv"), os.path.join(ROOT, "data", "interim", "pilot_accessibility_inputs.csv"), os.path.join(ROOT, "data", "interim", "merged_pois_observed.gpkg"), os.path.join(ROOT, "data", "interim", "ocean_park_1_boundary.geojson"), "Ocean Park 1")
west_data = load_site(
    os.path.join(ROOT, "data", "interim", "west_taymo_grid.gpkg"),
    os.path.join(ROOT, "data", "processed", "west_taymo_metrics.csv"),
    os.path.join(ROOT, "data", "interim", "west_taymo_accessibility_inputs.csv"),
    os.path.join(ROOT, "data", "interim", "west_taymo_merged_pois_economic.gpkg"),
    os.path.join(ROOT, "data", "raw", "west_taymo_tay_mo_core_boundary.gpkg"),
    "Tây Mỗ organic trace",
    second_core_path=os.path.join(ROOT, "data", "raw", "west_taymo_smart_city_core_boundary.gpkg"),
    second_core_name="Vinhomes Smart City OSM boundary",
)

def combine_sites(*sites):
    min_lat = min(s["bounds"][0][0] for s in sites)
    min_lon = min(s["bounds"][0][1] for s in sites)
    max_lat = max(s["bounds"][1][0] for s in sites)
    max_lon = max(s["bounds"][1][1] for s in sites)
    return {
        "bounds": [[min_lat, min_lon], [max_lat, max_lon]],
        "grid": {"type": "FeatureCollection", "features": sum((s["grid"]["features"] for s in sites), [])},
        "zero_nai": {"type": "FeatureCollection", "features": sum((s["zero_nai"]["features"] for s in sites), [])},
        "boundary": {"type": "FeatureCollection", "features": sum((s["boundary"]["features"] for s in sites), [])},
        "zones": {"type": "FeatureCollection", "features": sum((s["zones"]["features"] for s in sites), [])},
        "pois": {"type": "FeatureCollection", "features": sum((s["pois"]["features"] for s in sites), [])},
    }

SITE_DATA = {"east": east_data, "west": west_data}
SITE_DATA["both"] = combine_sites(east_data, west_data)

with open(VINBUS_GEOM, encoding="utf-8") as f: vinbus_raw = json.load(f)
ROUTE_COLORS = {"E01": "#e74c3c", "E02": "#3498db", "E03": "#2ecc71", "E10": "#f39c12", "OCP1": "#9b59b6", "OCP2": "#1abc9c"}
route_features = []
for rel in vinbus_raw["elements"]:
    if rel["type"] != "relation": continue
    name, ref = rel.get("tags", {}).get("name", ""), rel.get("tags", {}).get("ref", "")
    for member in rel.get("members", []):
        if member["type"] == "way" and "geometry" in member:
            route_features.append({"type": "Feature", "geometry": {"type": "LineString", "coordinates": [(p["lon"], p["lat"]) for p in member["geometry"]]}, "properties": {"ref": ref, "name": name, "color": ROUTE_COLORS.get(ref, "#8e44ad")}})
route_geojson = {"type": "FeatureCollection", "features": route_features}

stops_df = pd.read_csv(VINBUS_STOPS)
stops_geojson = {"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": {"type": "Point", "coordinates": [r["stop_lon"], r["stop_lat"]]}, "properties": {"stop_id": str(r["stop_id"]), "name": str(r["stop_name"])}} for _, r in stops_df.iterrows()]}
hanoi_stops_geojson = {"type": "FeatureCollection", "features": []}

METRIC_META = {
    "smci":  {"label": "SMCI_B", "unit": "index", "desc": "Capability index", "formatter": "float",
              "how": "SMCI_B = NAI_norm x MAI_norm x RAC_norm (Scenario B).",
              "long": "Final multiplicative capability index after VinBus. Zero if any one component is zero (weakest-link index)."},
    "nai":   {"label": "NAI", "unit": "count", "desc": "Walkable POIs (800m)", "formatter": "int",
              "how": "Count of qualifying POIs reachable within the 800 m / 10-min walking threshold.",
              "long": "Neighborhood Accessibility Index. A simple count, not magnitude-weighted."},
    "mai":   {"label": "MAI_B", "unit": "opps", "desc": "Metro opportunity", "formatter": "float",
              "how": "Opportunity-weighted, time-decayed access across 4 domains via walk+transit (Scenario B).",
              "long": "Metropolitan Accessibility Index. Higher = more/larger reachable opportunities within 60 min."},
    "rac":   {"label": "RAC_B", "unit": "ratio", "desc": "Walk+transit vs motorcycle", "formatter": "float",
              "how": "Opportunity-weighted walk-transit travel time divided by motorcycle travel time, inverted to a ratio.",
              "long": "Relative Accessibility Competitiveness. 1.0 = walk+transit as fast as motorcycle; below 1.0 = motorcycle faster."},
    "delta": {"label": "Delta SMCI", "unit": "index", "desc": "Scenario B minus Scenario A", "formatter": "float",
              "how": "Delta_SMCI = SMCI(Scenario B) - SMCI(Scenario A), shared A+B normalization.",
              "long": "Modeled difference from adding the VinBus network assumption. Negative values mean lower modeled SMCI under Scenario B."},
}

def _metric_stats(key, raw_key):
    vals = sorted(f["properties"][raw_key] for f in SITE_DATA["both"]["grid"]["features"])
    if not vals:
        return 0.0, 1.0, [0] * 10
    n = len(vals)
    lo = vals[max(0, int(n * 0.02) - 1)]
    hi = vals[min(n - 1, int(n * 0.98))]
    if hi <= lo:
        lo, hi = min(vals), max(vals)
    if hi <= lo:
        hi = lo + 1.0
    bins = 10
    hist = [0] * bins
    for v in vals:
        t = max(0.0, min(0.9999, (v - lo) / (hi - lo)))
        hist[int(t * bins)] += 1
    return lo, hi, hist

for _key, _raw in (("smci", "SMCI_raw"), ("nai", "NAI_raw"), ("mai", "MAI_raw"), ("rac", "RAC_raw"), ("delta", "Delta_raw")):
    _lo, _hi, _hist = _metric_stats(_key, _raw)
    METRIC_META[_key]["lo"] = _lo
    METRIC_META[_key]["hi"] = _hi
    METRIC_META[_key]["hist"] = _hist


def js(obj): return json.dumps(obj, separators=(',', ':'))

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
  <h1 id="site-title">Ocean Park / Context</h1>
  <div class="subtitle" id="site-subtitle">East-side comparison</div>
  <div class="subtitle" id="site-meta" style="color:#546e7a;">Gia Lâm, Hanoi &middot; 250 m grid &middot; 2026</div>
  <div class="subtitle" style="color:#4fc3f7;">Default view: 2 main partitions only (site-specific)</div>

  <div class="section">
    <h2>Study site</h2>
    <select id="site-sel">
      <option value="east" selected>East — Ocean Park / context</option>
      <option value="west">West — Tây Mỗ / Smart City</option>
      <option value="both">Both — East + West overview</option>
    </select>
  </div>

  <div class="section">
    <h2>Basemap</h2>
    <select id="basemap-sel">
      <option value="carto" selected>CartoDB Dark</option>
      <option value="osm">OpenStreetMap</option>
      <option value="esri">Esri Satellite</option>
    </select>
  </div>

  <div class="section" id="grid-section">
    <h2>Grid cells</h2>
    <label><input type="checkbox" id="chk-grid"> Show analysis grid (optional)</label>
    <label><input type="checkbox" id="chk-boundary" checked>
      <span class="swatch" style="background:transparent;border:2px dashed #f39c12;"></span>
      Study area boundary
    </label>
    <label><input type="checkbox" id="chk-zones" checked> Site partitions</label>
    <div style="margin-left:22px;margin-top:3px;">
      <div class="legend-row"><span class="swatch" style="background:rgba(0,229,255,.18);border:2px solid #00e5ff;"></span>Tây Mỗ organic trace</div>
      <div class="legend-row"><span class="swatch" style="background:rgba(255,202,40,.18);border:2px solid #ffca28;"></span>Smart City OSM boundary</div>
      <div class="legend-row"><span class="swatch" style="background:rgba(207,216,220,.04);border:1px dashed #cfd8dc;"></span>Surrounding context</div>
    </div>
    <label><input type="checkbox" id="chk-zero-nai">
      <span class="swatch" style="background:rgba(255,255,255,.08);border:2px solid #ffffff;"></span>
      Zero NAI cells (<span id="count-zero-nai"></span>)
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

  <div class="section" id="both-note" style="display:none;">
    <h2>Overview mode</h2>
    <div class="layer-desc">
      Both mode shows only the main east/west partitions. Select <b>East</b> or <b>West</b> to inspect grid metrics (Typology, SMCI, NAI, MAI, RAC, Delta).
    </div>
  </div>

  <div class="section">
    <h2>Optional diagnostics (off by default)</h2>
    <label><input type="checkbox" id="chk-poi"> POIs</label>
    <label><input type="checkbox" id="chk-routes"> VinBus routes</label>
    <label><input type="checkbox" id="chk-vstops"> VinBus stops (<span id="count-vstops"></span>)</label>
    <label><input type="checkbox" id="chk-hstops"> Hanoi GTFS stops (<span id="count-hstops"></span>)</label>
    <div style="font-size:10px;color:#546e7a;margin-top:4px;">
      Use only for technical QA. Main presentation = core vs surrounding context.
    </div>
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
const SITE_DATA = {js(SITE_DATA)};
const ROUTES   = {js(route_geojson)};
const VSTOPS   = {js(stops_geojson)};
const HSTOPS   = {js(hanoi_stops_geojson)};
const METRIC_META = {js(METRIC_META)};

let requestedSite = (window.location.hash || '').replace('#','');
let currentSite = ['east','west','both'].includes(requestedSite) ? requestedSite : 'east';
let BOUNDARY = SITE_DATA[currentSite].boundary;
let ZONES    = SITE_DATA[currentSite].zones;
let POIS     = SITE_DATA[currentSite].pois;
let GRID     = SITE_DATA[currentSite].grid;
let ZERO_NAI = SITE_DATA[currentSite].zero_nai;

let selectedCellFeature = null;

function applySiteTitle() {{
  const title = document.getElementById('site-title');
  const subtitle = document.getElementById('site-subtitle');
  const meta = document.getElementById('site-meta');
  if (currentSite === 'west') {{
    title.textContent = 'Tây Mỗ / Vinhomes Smart City';
    subtitle.textContent = 'West-side two-zone comparison';
    meta.textContent = 'Tây Mỗ, Hanoi · 250 m grid · 2026';
  }} else if (currentSite === 'both') {{
    title.textContent = 'East + West overview';
    subtitle.textContent = 'Ocean Park plus Tây Mỗ / Smart City';
    meta.textContent = 'Two study areas · 2-zone overview · diagnostics off';
  }} else {{
    title.textContent = 'Ocean Park / Context';
    subtitle.textContent = 'East-side comparison';
    meta.textContent = 'Gia Lâm, Hanoi · 250 m grid · 2026';
  }}
}}

function applySiteControls() {{
  document.getElementById('grid-section').style.display = '';
  document.getElementById('both-note').style.display = 'none';
  document.getElementById('chk-grid').disabled = false;
  document.getElementById('chk-zero-nai').disabled = false;
  document.getElementById('grid-mode').disabled = false;
}}

function combinedBounds() {{
  const siteNames = Object.keys(SITE_DATA);
  const bounds = L.latLngBounds(SITE_DATA[siteNames[0]].bounds);
  siteNames.slice(1).forEach(name => bounds.extend(SITE_DATA[name].bounds));
  return bounds;
}}
const FULL_BOUNDS = combinedBounds();

// ── Map init ──────────────────────────────────────────────────────────────
const map = L.map('map', {{
  zoomControl: true,
  attributionControl: true,
}}).setView([21.0, 105.8], 13);

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

applySiteTitle();
applySiteControls();
document.getElementById('site-sel').value = currentSite;
document.getElementById('site-sel').addEventListener('change', e => {{
  window.location.hash = e.target.value;
  window.location.reload();
}});

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

const boundaryLayer = L.geoJSON(BOUNDARY, {{
  interactive: false,
  style: {{
    color: '#f39c12',
    weight: 2.5,
    dashArray: '6 4',
    fillColor: 'transparent',
    fillOpacity: 0,
  }},
}});
boundaryLayer.addTo(map);

// ── Study area boundary ────────────────────────────────────────────────────


document.getElementById('chk-boundary').addEventListener('change', e => {{
  e.target.checked ? boundaryLayer.addTo(map) : map.removeLayer(boundaryLayer);
}});



const zoneLayer = L.geoJSON(ZONES, {{
  interactive: true,
  style: f => {{
    const zone = f.properties.zone || '';
    const isPartition = zone !== 'Context';
    return {{
      color: f.properties.color,
      weight: isPartition ? 3.4 : 1.4,
      dashArray: isPartition ? null : '5 5',
      fillColor: f.properties.fill,
      fillOpacity: isPartition ? 0.16 : 0.02,
      opacity: isPartition ? 1.0 : 0.65,
    }};
  }},
  onEachFeature: (f, layer) => {{
    layer.bindTooltip(f.properties.name || f.properties.zone || 'Site partition', {{
      sticky: true,
      direction: 'top',
      className: 'cell-tooltip'
    }});
  }},
}});
zoneLayer.addTo(map);

document.getElementById('chk-zones').addEventListener('change', e => {{
  e.target.checked ? zoneLayer.addTo(map) : map.removeLayer(zoneLayer);
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

const METRIC_KEYS = {{
  typology: null,
  nai: 'NAI_raw',
  smci: 'SMCI_raw',
  mai: 'MAI_raw',
  rac: 'RAC_raw',
  delta: 'Delta_raw',
}};

function modeHelp(mode) {{
  if (mode === 'typology') {{
    return `
      <b>Typology B</b><br>
      Four classes combine local walking access (NAI) with metropolitan competitiveness (MCS).
      Green/orange/blue/red are categories, not a heat scale. Click any cell for its metrics.`;
  }}
  const m = METRIC_META[mode];
  return `
    <b>${{m.label}} heatmap</b><br>
    <span style="color:#abd9e9;">Cold blue</span> = lower value.
    <span style="color:#f46d43;">Warm red</span> = higher value.<br>
    ${{m.how}}<br>
    <span style="color:#78909c;">Current range: ${{m.lo.toFixed(4)}} to ${{m.hi.toFixed(4)}}. Click any cell for exact values.</span>`;
}}

function layerDescription(mode) {{
  if (mode === 'typology') {{
    return `<b>Selected: Typology B</b><br>
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
  if (mode === 'typology') return '';
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

function renderSelectedCell(f) {{
    const p = f.properties;
    const [bg,fg] = BADGE_COLORS[p.typology_B] || ['#555','#fff'];
    const activeKey = METRIC_KEYS[gridMode];
    const activeValue = activeKey ? p[activeKey] : null;
    const activeMetric = activeKey ? `
      <div class="metric" style="grid-column:span 2;border:1px solid #4fc3f7;">
        <div class="val">${{activeValue.toFixed ? activeValue.toFixed(4) : activeValue}}</div>
        <div class="lbl">${{METRIC_META[gridMode].label}} — ${{heatPosition(gridMode, activeValue)}} on current heatmap</div>
      </div>` : '';
    document.getElementById('info-panel').innerHTML = `
      <b>Cell #${{p.cell_id}}</b>&nbsp;
      <span class="badge" style="background:${{bg}};color:${{fg}};">${{p.typology_B}}</span>
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
          <div class="lbl">&Delta;SMCI &mdash; VinBus effect (Scenario B &minus; A)</div>
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
document.getElementById('count-zero-nai').textContent = ZERO_NAI.features.length;

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
    bar.style.background = spectralColor(t);
    bar.title = `n=${{count}}`;
    histEl.appendChild(bar);
  }});
}}

document.getElementById('grid-mode').addEventListener('change', e => {{
  gridMode = e.target.value;
  if (!map.hasLayer(gridLayer)) {{
    gridLayer.addTo(map);
    document.getElementById('chk-grid').checked = true;
    zoneLayer.bringToFront();
    boundaryLayer.bringToFront();
  }}
  gridLayer.setStyle(gridStyle);
  updateContLegend(gridMode);
  updateActiveDescription(gridMode);
  setDefaultInfo();
}});
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
      `<b>${{p.name}}</b><br><span style="color:#aaa">${{p.domain}}</span> &middot; ${{p.source || p.category || 'mapped POI'}}`,
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
document.getElementById('count-vstops').textContent = VSTOPS.features.length;

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

document.getElementById('count-hstops').textContent = HSTOPS.features.length;

document.getElementById('chk-hstops').addEventListener('change', e => {{
  e.target.checked ? hstopLayer.addTo(map) : map.removeLayer(hstopLayer);
}});

// ── Initial fit: current study site only (not the full VinBus network) ──

map.fitBounds(L.latLngBounds(SITE_DATA[currentSite].bounds), {{padding:[20,20]}});
</script>
</body>
</html>"""

os.makedirs(os.path.dirname(OUT_HTML), exist_ok=True)
with open(OUT_HTML, "w", encoding="utf-8") as f:
    f.write(HTML)

size_kb = os.path.getsize(OUT_HTML) // 1024
print(f"\nDone -> {OUT_HTML}  ({size_kb} KB)")
print(f"  VinBus stops total : {len(stops_geojson['features'])}")
print("Open in any browser.")
