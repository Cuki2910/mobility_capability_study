"""Prepare manual POI and Android motorcycle check files with direct links."""
from __future__ import annotations

import argparse
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd


ANDROID_COLUMNS = {
    "google_maps_android_minutes": pd.NA,
    "android_lookup_date": pd.NA,
    "android_lookup_time": pd.NA,
    "android_traffic_condition": pd.NA,
    "android_device_notes": pd.NA,
}


def directions_url(row) -> str:
    origin = f"{row['origin_lat']},{row['origin_lon']}"
    destination = f"{row['destination_lat']},{row['destination_lon']}"
    return (
        "https://www.google.com/maps/dir/?api=1"
        f"&origin={quote_plus(origin)}"
        f"&destination={quote_plus(destination)}"
        "&travelmode=driving"
    )


def prepare_motorcycle_template(path: Path, output: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    for column, default in ANDROID_COLUMNS.items():
        if column not in df.columns:
            df[column] = default
    df["google_maps_directions_url"] = df.apply(directions_url, axis=1)
    df["android_check_status"] = df["google_maps_android_minutes"].apply(lambda v: "done" if pd.notna(v) else "unchecked")
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output, index=False)
    return df


def write_motorcycle_markdown(df: pd.DataFrame, output: Path) -> None:
    lines = ["# Android Motorcycle Validation Checklist", "", "Open each link on Android Google Maps, switch to motorcycle mode if shown, record minutes.", ""]
    for row in df.itertuples(index=False):
        lines.append(f"## Pair {row.sample_id}: {row.origin_name} -> {row.destination_name}")
        lines.append(f"- Model motorcycle minutes: {row.model_motorcycle_minutes}")
        lines.append(f"- Current car minutes: {row.gmaps_car_minutes}")
        lines.append(f"- Link: {row.google_maps_directions_url}")
        lines.append(f"- Fill: `google_maps_android_minutes`, `android_lookup_date`, `android_lookup_time`, `android_traffic_condition`")
        lines.append("")
    output.write_text("\n".join(lines), encoding="utf-8")


def write_poi_markdown(path: Path, output: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    lines = ["# POI Spot-Check Checklist", "", "For each row, open OSM and Google Maps links. Set status to confirmed, missing_in_osm, misclassified, or duplicate.", ""]
    for row in df.itertuples(index=False):
        name = getattr(row, "name", "")
        lines.append(f"## {row.nai_category}: {name if pd.notna(name) else '(unnamed)'}")
        lines.append(f"- Coordinates: {row.lat}, {row.lon}")
        lines.append(f"- OSM: {row.osm_url}")
        lines.append(f"- Google Maps: {row.google_maps_search_url}")
        lines.append(f"- Current status: {row.spot_check_status}")
        lines.append("")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    return df


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--motorcycle", type=Path, default=Path("outputs/validation/manual_motorcycle_validation_template.csv"))
    parser.add_argument("--motorcycle-md", type=Path, default=Path("outputs/validation/android_motorcycle_checklist.md"))
    parser.add_argument("--poi", type=Path, default=Path("data/interim/poi_spot_check.csv"))
    parser.add_argument("--poi-md", type=Path, default=Path("outputs/poi_spot_check_checklist.md"))
    args = parser.parse_args()

    moto = prepare_motorcycle_template(args.motorcycle, args.motorcycle)
    write_motorcycle_markdown(moto, args.motorcycle_md)
    write_poi_markdown(args.poi, args.poi_md)
    print(f"Prepared {args.motorcycle}, {args.motorcycle_md}, and {args.poi_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
