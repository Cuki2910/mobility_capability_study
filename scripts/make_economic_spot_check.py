"""Build a manual spot-check sheet for the OSM economic POIs added to the layer.

Reads the synthetic economic POIs (landuse/office/bank) and emits a CSV with a
Google Maps link per row so a human can confirm each is a genuine employment /
economic destination (not a tagging artefact, residential building, or duplicate).

Run:
  python scripts/make_economic_spot_check.py

Output:
  outputs/validation/economic_poi_spot_check.csv
  outputs/validation/economic_poi_spot_check.md
"""
from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

ECON_SYNTH = Path("data/interim/landuse_poi_synthetic.gpkg")
OUT_CSV = Path("outputs/validation/economic_poi_spot_check.csv")
OUT_MD = Path("outputs/validation/economic_poi_spot_check.md")


def main() -> int:
    import geopandas as gpd
    import pandas as pd
    from src.accessibility_inputs import classify_poi_opportunity_domain

    if not ECON_SYNTH.exists():
        print(f"Error: {ECON_SYNTH} not found. Run fetch_osm_landuse.py first.")
        return 1

    gdf = gpd.read_file(ECON_SYNTH)
    # Ensure WGS84 for lat/lon link
    gdf = gdf.to_crs("EPSG:4326")

    rows = []
    for _, r in gdf.iterrows():
        geom = r.geometry
        if geom is None or geom.is_empty:
            continue
        lat, lon = geom.y, geom.x
        domain, weight = classify_poi_opportunity_domain(r)
        rows.append({
            "name": r.get("name"),
            "source": r.get("source"),
            "amenity": r.get("amenity"),
            "office": r.get("office"),
            "landuse": r.get("landuse"),
            "classified_domain": domain,
            "opportunity_weight": round(float(weight), 3),
            "lat": round(lat, 6),
            "lon": round(lon, 6),
            "gmaps_url": f"https://www.google.com/maps/search/?api=1&query={lat},{lon}",
            "confirmed": "",          # human fills: yes / no
            "true_domain": "",        # human fills if reclassification needed
            "notes": "",
        })

    df = pd.DataFrame(rows)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CSV, index=False, encoding="utf-8")

    # Markdown summary
    from collections import Counter
    dom_counts = Counter(df["classified_domain"])
    src_counts = Counter(df["source"])
    lines = [
        "# Economic POI Spot-Check",
        "",
        f"Total economic candidate POIs to review: **{len(df)}**",
        "",
        "Each row in `economic_poi_spot_check.csv` has a `gmaps_url`. Open it, confirm",
        "the POI is a genuine economic/employment destination, and fill `confirmed`",
        "(yes/no) plus `true_domain` if it should be reclassified.",
        "",
        "## Classified domain breakdown",
        "",
        "| Domain | Count |",
        "|---|---|",
    ]
    for d, c in dom_counts.most_common():
        lines.append(f"| {d} | {c} |")
    lines += ["", "## Source breakdown", "", "| Source | Count |", "|---|---|"]
    for s, c in src_counts.most_common():
        lines.append(f"| {s} | {c} |")
    lines += [
        "",
        "## Review guidance",
        "",
        "- `osm_landuse` industrial polygons (e.g. wastewater plant, bus depot) are",
        "  economic land but low employment density — confirm or downweight.",
        "- `osm_office` with education names should already be higher_education;",
        "  flag any that slipped through as economic.",
        "- `osm_amenity_econ` banks/markets/post offices are usually reliable.",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_CSV} ({len(df)} rows)")
    print(f"Wrote {OUT_MD}")
    print(f"Domain breakdown: {dict(dom_counts)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
