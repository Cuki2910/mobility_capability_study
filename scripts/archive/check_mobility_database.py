"""Search MobilityDatabase catalogs for candidate GTFS feeds."""
from __future__ import annotations

import argparse
from pathlib import Path
from urllib.request import urlopen

import pandas as pd


CATALOG_CSV_URL = "https://bit.ly/catalogs-csv"
HANOI_BBOX = {
    "min_lat": 20.85,
    "max_lat": 21.15,
    "min_lon": 105.75,
    "max_lon": 106.05,
}


def _contains_text(row: pd.Series, query: str) -> bool:
    text = " ".join(str(row.get(col, "")) for col in ["location.municipality", "provider", "name", "note"])
    return query.lower() in text.lower()


def _bbox_intersects_hanoi(row: pd.Series) -> bool:
    cols = {
        "min_lat": "location.bounding_box.minimum_latitude",
        "max_lat": "location.bounding_box.maximum_latitude",
        "min_lon": "location.bounding_box.minimum_longitude",
        "max_lon": "location.bounding_box.maximum_longitude",
    }
    try:
        bbox = {key: float(row[col]) for key, col in cols.items()}
    except (TypeError, ValueError):
        return False
    return not (
        bbox["max_lat"] < HANOI_BBOX["min_lat"]
        or bbox["min_lat"] > HANOI_BBOX["max_lat"]
        or bbox["max_lon"] < HANOI_BBOX["min_lon"]
        or bbox["min_lon"] > HANOI_BBOX["max_lon"]
    )


def search_catalog(catalog: pd.DataFrame, query: str, country_code: str) -> pd.DataFrame:
    gtfs = catalog[catalog["data_type"].fillna("").str.lower().eq("gtfs")].copy()
    country = gtfs[gtfs["location.country_code"].fillna("").str.upper().eq(country_code.upper())].copy()
    text_match = country[country.apply(lambda row: _contains_text(row, query), axis=1)]
    bbox_match = country[country.apply(_bbox_intersects_hanoi, axis=1)]
    keep = [
        "mdb_source_id",
        "status",
        "provider",
        "name",
        "location.country_code",
        "location.subdivision_name",
        "location.municipality",
        "is_official",
        "urls.direct_download",
        "urls.latest",
        "urls.license",
        "location.bounding_box.minimum_latitude",
        "location.bounding_box.maximum_latitude",
        "location.bounding_box.minimum_longitude",
        "location.bounding_box.maximum_longitude",
        "location.bounding_box.extracted_on",
    ]
    if text_match.empty and bbox_match.empty:
        return pd.DataFrame(columns=[col for col in keep if col in country.columns])
    out = pd.concat([text_match, bbox_match], ignore_index=True).drop_duplicates(subset=["mdb_source_id"])
    out = out[[col for col in keep if col in out.columns]]
    sort_cols = [col for col in ["status", "provider", "name"] if col in out.columns]
    return out.sort_values(sort_cols, na_position="last") if sort_cols else out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", default="Hanoi")
    parser.add_argument("--country-code", default="VN")
    parser.add_argument("--catalog-url", default=CATALOG_CSV_URL)
    parser.add_argument("--output", type=Path, default=Path("data/interim/mobility_database_hanoi_candidates.csv"))
    args = parser.parse_args()

    with urlopen(args.catalog_url, timeout=60) as response:
        catalog = pd.read_csv(response)
    candidates = search_catalog(catalog, args.query, args.country_code)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    candidates.to_csv(args.output, index=False)
    print(f"Found {len(candidates)} candidate GTFS feeds; wrote {args.output}")
    if not candidates.empty:
        print(candidates[["mdb_source_id", "status", "provider", "name", "location.municipality"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
