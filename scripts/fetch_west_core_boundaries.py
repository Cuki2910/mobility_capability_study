"""Fetch real west-side core boundaries from OSM/Nominatim/Overpass.

Outputs replace the earlier rectangle seed boundaries:
- data/raw/west_taymo_smart_city_core_boundary.gpkg
- data/raw/west_taymo_tay_mo_core_boundary.gpkg
- outputs/west_taymo/boundary_provenance.md
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import osmnx as ox
import requests
from shapely.geometry import LineString, MultiLineString, MultiPolygon, Polygon, shape
from shapely.ops import polygonize, unary_union


ROOT = Path(__file__).resolve().parents[1]
OUT_SMART = ROOT / "data/raw/west_taymo_smart_city_core_boundary.gpkg"
OUT_TAYMO = ROOT / "data/raw/west_taymo_tay_mo_core_boundary.gpkg"
REPORT = ROOT / "outputs/west_taymo/boundary_provenance.md"

USER_AGENT = "mobility-capability-study-boundary-fetch/1.0"
WEST_BBOX = (105.72467747747748, 20.98017747747748, 105.771839, 21.026302)
TARGET_CRS = "EPSG:4326"
METRIC_CRS = "EPSG:3857"


def _write_gdf(gdf: gpd.GeoDataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    gdf.to_file(path, driver="GPKG")


def _clean_polygon(geom):
    geom = geom.buffer(0)
    if geom.geom_type == "MultiPolygon":
        geom = max(geom.geoms, key=lambda g: g.area)
    return geom


def fetch_nominatim_polygon(query: str) -> gpd.GeoDataFrame:
    gdf = ox.geocode_to_gdf(query, which_result=None).to_crs(TARGET_CRS)
    poly = gdf[gdf.geometry.geom_type.isin(["Polygon", "MultiPolygon"])].copy()
    if poly.empty:
        raise RuntimeError(f"No polygon result from Nominatim for {query!r}")
    return poly.iloc[[0]].copy()


def overpass_elements(query: str) -> list[dict]:
    for url in [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
    ]:
        try:
            response = requests.post(
                url,
                data={"data": query},
                headers={"User-Agent": USER_AGENT},
                timeout=90,
            )
            response.raise_for_status()
            return response.json().get("elements", [])
        except requests.RequestException:
            continue
    return []


def fetch_tay_mo_admin_polygon() -> gpd.GeoDataFrame | None:
    south, west, north, east = 20.96, 105.70, 21.04, 105.82
    query = f"""
    [out:json][timeout:90];
    (
      relation["boundary"="administrative"]["name"~"Tây Mỗ|Tay Mo|Tay Mỗ|Tây Mo",i]({south},{west},{north},{east});
      way["boundary"="administrative"]["name"~"Tây Mỗ|Tay Mo|Tay Mỗ|Tây Mo",i]({south},{west},{north},{east});
      relation["admin_level"]["name"~"Tây Mỗ|Tay Mo|Tay Mỗ|Tây Mo",i]({south},{west},{north},{east});
    );
    out geom tags;
    """
    elements = overpass_elements(query)
    features = []
    for elem in elements:
        tags = elem.get("tags", {})
        geometry = elem.get("geometry") or []
        if len(geometry) < 4:
            continue
        coords = [(p["lon"], p["lat"]) for p in geometry]
        try:
            geom = Polygon(coords) if coords[0] == coords[-1] else LineString(coords)
            if geom.geom_type == "LineString":
                polys = list(polygonize([geom]))
                if not polys:
                    continue
                geom = max(polys, key=lambda g: g.area)
            features.append({**tags, "osm_type": elem.get("type"), "osm_id": elem.get("id"), "geometry": _clean_polygon(geom)})
        except Exception:
            continue
    if not features:
        return None
    gdf = gpd.GeoDataFrame(features, geometry="geometry", crs=TARGET_CRS)
    gdf = gdf[gdf.geometry.geom_type.isin(["Polygon", "MultiPolygon"])].copy()
    if gdf.empty:
        return None
    gdf["_area_m2"] = gdf.to_crs(METRIC_CRS).area
    return gdf.sort_values("_area_m2", ascending=False).iloc[[0]].drop(columns=["_area_m2"])


def build_tay_mo_organic_core(smart_city_geom) -> gpd.GeoDataFrame:
    """Fallback: trace inherited Tay Mo core from OSM local fabric, excluding Smart City.

    Uses real local OSM/Oveture/landuse/building footprints already fetched in the repo:
    POIs and non-industrial landuse around named Tay Mo streets are buffered and dissolved,
    then clipped away from Smart City. This is not an official ward boundary, but it is
    a reproducible OSM-derived organic-core trace instead of a rectangle.
    """
    poi_paths = [
        ROOT / "data/interim/west_taymo_osm_pois.gpkg",
        ROOT / "data/interim/west_taymo_merged_pois_economic.gpkg",
    ]
    landuse_path = ROOT / "data/raw/west_taymo_osm_landuse_polygons.gpkg"
    buildings_path = ROOT / "data/raw/west_taymo_building_footprints.gpkg"

    pois = [gpd.read_file(p).to_crs(TARGET_CRS) for p in poi_paths if p.exists()]
    landuse = gpd.read_file(landuse_path).to_crs(TARGET_CRS) if landuse_path.exists() else gpd.GeoDataFrame(geometry=[], crs=TARGET_CRS)
    buildings = gpd.read_file(buildings_path).to_crs(TARGET_CRS) if buildings_path.exists() else gpd.GeoDataFrame(geometry=[], crs=TARGET_CRS)

    parts = []
    if pois:
        p = gpd.GeoDataFrame(pd_concat(pois), crs=TARGET_CRS)
        text = (
            p.get("addr:street", "").astype(str)
            + " "
            + p.get("name", "").astype(str)
            + " "
            + p.get("addr:subdistrict", "").astype(str)
        ).str.lower()
        mask = text.str.contains("tây mỗ|tay mo|hữu hưng|miêu nha|sa đôi|cầu cốc|do nha", regex=True, na=False)
        parts.extend(p.loc[mask, "geometry"].dropna().tolist())

    if not landuse.empty:
        text = (landuse.get("name", "").astype(str) + " " + landuse.get("addr:street", "").astype(str)).str.lower()
        mask = text.str.contains("tây mỗ|tay mo|hữu hưng|miêu nha|sa đôi|cầu cốc|do nha", regex=True, na=False)
        parts.extend(landuse.loc[mask, "geometry"].dropna().tolist())

    if not parts:
        raise RuntimeError("Cannot derive Tay Mo organic core: no named OSM local fabric features found.")

    seeds = gpd.GeoSeries(parts, crs=TARGET_CRS).to_crs(METRIC_CRS)
    seed_hull = unary_union(seeds.buffer(120)).convex_hull.buffer(120)

    if not buildings.empty:
        b = buildings.to_crs(METRIC_CRS)
        clipped_buildings = b[b.intersects(seed_hull.buffer(180))].geometry
        if not clipped_buildings.empty:
            fabric = unary_union(list(clipped_buildings.buffer(35)) + [seed_hull]).buffer(0)
        else:
            fabric = seed_hull
    else:
        fabric = seed_hull

    smart_metric = gpd.GeoSeries([smart_city_geom], crs=TARGET_CRS).to_crs(METRIC_CRS).iloc[0]
    organic = fabric.difference(smart_metric.buffer(40)).buffer(0)
    if organic.geom_type == "MultiPolygon":
        organic = max(organic.geoms, key=lambda g: g.area)
    organic = gpd.GeoSeries([organic], crs=METRIC_CRS).to_crs(TARGET_CRS).iloc[0]

    return gpd.GeoDataFrame(
        [
            {
                "name": "Tay Mo organic core",
                "source": "OSM-derived local fabric trace",
                "method": "named POI/landuse seeds + building-footprint dissolve; Smart City excluded",
                "geometry": _clean_polygon(organic),
            }
        ],
        crs=TARGET_CRS,
    )


def pd_concat(frames):
    import pandas as pd

    return pd.concat(frames, ignore_index=True)


def main() -> None:
    smart = fetch_nominatim_polygon("Vinhomes Smart City, Hanoi, Vietnam")
    smart_props = smart.drop(columns="geometry").iloc[0].to_dict()
    smart_out = gpd.GeoDataFrame(
        [
            {
                "name": "Vinhomes Smart City",
                "source": "OpenStreetMap Nominatim",
                "osm_type": smart_props.get("osm_type"),
                "osm_id": smart_props.get("osm_id"),
                "class": smart_props.get("class"),
                "type": smart_props.get("type"),
                "display_name": smart_props.get("display_name"),
                "retrieved": datetime.now(timezone.utc).date().isoformat(),
                "geometry": _clean_polygon(smart.geometry.iloc[0]),
            }
        ],
        crs=TARGET_CRS,
    )
    _write_gdf(smart_out, OUT_SMART)

    tay_admin = fetch_tay_mo_admin_polygon()
    if tay_admin is not None:
        tay = tay_admin.copy()
        tay["source"] = "OpenStreetMap Overpass administrative boundary"
        tay["retrieved"] = datetime.now(timezone.utc).date().isoformat()
        tay["geometry"] = tay.geometry.apply(_clean_polygon)
        tay_method = "OSM administrative boundary"
    else:
        tay = build_tay_mo_organic_core(smart_out.geometry.iloc[0])
        tay["retrieved"] = datetime.now(timezone.utc).date().isoformat()
        tay_method = "OSM-derived local fabric trace"
    _write_gdf(tay, OUT_TAYMO)

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for label, gdf, path, method in [
        ("Smart City", smart_out, OUT_SMART, "OSM Nominatim polygon"),
        ("Tay Mo", tay, OUT_TAYMO, tay_method),
    ]:
        geom = gdf.to_crs(METRIC_CRS).geometry.iloc[0]
        rows.append(
            f"| {label} | {method} | `{path.relative_to(ROOT)}` | {geom.area / 1_000_000:.2f} | "
            f"{len(gdf.geometry.iloc[0].exterior.coords) if gdf.geometry.iloc[0].geom_type == 'Polygon' else 'multi'} |"
        )
    REPORT.write_text(
        "\n".join(
            [
                "# West Core Boundary Provenance",
                "",
                f"Generated UTC: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
                "",
                "| Boundary | Method | Output | Area km2 | Vertices |",
                "|---|---|---|---:|---:|",
                *rows,
                "",
                "Notes:",
                "- Smart City is imported directly from OSM/Nominatim, same pattern as the Ocean Park boundary.",
                "- Tay Mo uses an OSM administrative boundary if Overpass returns one; otherwise it uses an OSM-derived organic-core trace from named local fabric and building footprints, with Smart City removed.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUT_SMART}")
    print(f"Wrote {OUT_TAYMO}")
    print(f"Wrote {REPORT}")


if __name__ == "__main__":
    main()
