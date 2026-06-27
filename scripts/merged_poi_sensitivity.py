"""Prepare Overture-only spot checks and compare merged-POI pilot metrics."""
from __future__ import annotations

import argparse
from pathlib import Path

import geopandas as gpd
import pandas as pd


TYPOLOGY_ORDER = [
    "Integrated Capability",
    "Fragmented Capability",
    "Transit-Dependent",
    "Motorcycle Lock-in",
]


def pct(value: float) -> str:
    return f"{value:.1%}"


def make_spot_check(merged_pois_path: Path, output: Path) -> pd.DataFrame:
    pois = gpd.read_file(merged_pois_path).to_crs(epsg=4326)
    overture = pois[pois["source"] == "overture_only"].copy()
    overture["longitude"] = overture.geometry.x
    overture["latitude"] = overture.geometry.y
    overture["map_url"] = overture.apply(
        lambda r: f"https://www.google.com/maps/search/?api=1&query={r['latitude']:.7f},{r['longitude']:.7f}",
        axis=1,
    )
    for col in ["name", "category", "confidence"]:
        if col not in overture.columns:
            overture[col] = ""
    out = overture[["name", "category", "confidence", "latitude", "longitude", "map_url"]].copy().reset_index(drop=True)
    out["spot_check_status"] = "unchecked"
    out["notes"] = ""
    output.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output, index=False)
    return out


def compare_metrics(primary_path: Path, merged_path: Path, output_csv: Path, output_md: Path) -> pd.DataFrame:
    primary = pd.read_csv(primary_path)
    merged = pd.read_csv(merged_path)
    joined = primary.merge(merged, on="cell_id", suffixes=("_primary", "_merged"))
    if len(joined) != len(primary):
        raise ValueError("Merged metrics do not align one-to-one with primary metrics by cell_id")

    joined["Delta_SMCI_B_merged_minus_primary"] = joined["SMCI_B_merged"] - joined["SMCI_B_primary"]
    joined["Delta_NAI_merged_minus_primary"] = joined["NAI_merged"] - joined["NAI_primary"]
    joined["typology_changed"] = joined["typology_B_primary"] != joined["typology_B_merged"]
    joined["primary_zero_nai"] = joined["NAI_primary"] <= 0
    joined["merged_zero_nai"] = joined["NAI_merged"] <= 0
    joined["zero_nai_resolved"] = joined["primary_zero_nai"] & ~joined["merged_zero_nai"]
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    keep_cols = [
        "cell_id",
        "NAI_primary",
        "NAI_merged",
        "Delta_NAI_merged_minus_primary",
        "SMCI_B_primary",
        "SMCI_B_merged",
        "Delta_SMCI_B_merged_minus_primary",
        "typology_B_primary",
        "typology_B_merged",
        "typology_changed",
        "zero_nai_resolved",
    ]
    joined[keep_cols].to_csv(output_csv, index=False)
    write_summary(joined, output_md)
    return joined


def write_summary(joined: pd.DataFrame, output_md: Path) -> None:
    n = len(joined)
    mean_primary = joined["SMCI_B_primary"].mean()
    mean_merged = joined["SMCI_B_merged"].mean()
    typology_changed = int(joined["typology_changed"].sum())
    zero_resolved = int(joined["zero_nai_resolved"].sum())
    primary_zero = int(joined["primary_zero_nai"].sum())
    merged_zero = int(joined["merged_zero_nai"].sum())

    typology = pd.DataFrame({"typology": TYPOLOGY_ORDER})
    primary_counts = joined["typology_B_primary"].value_counts()
    merged_counts = joined["typology_B_merged"].value_counts()
    typology["primary_cells"] = typology["typology"].map(primary_counts).fillna(0).astype(int)
    typology["merged_cells"] = typology["typology"].map(merged_counts).fillna(0).astype(int)
    typology["delta_cells"] = typology["merged_cells"] - typology["primary_cells"]

    lines = [
        "# Merged-POI Sensitivity",
        "",
        "Primary pilot results remain OSM-only until Overture-only POIs are manually spot-checked. This run tests the effect of using the OSM + Overture union.",
        "",
        "## Headline",
        "",
        f"- Cells compared: {n}",
        f"- Mean SMCI_B primary: {mean_primary:.4f}",
        f"- Mean SMCI_B merged POIs: {mean_merged:.4f}",
        f"- Mean SMCI_B delta: {mean_merged - mean_primary:+.4f}",
        f"- Typology changes: {typology_changed}/{n} ({pct(typology_changed / n)})",
        f"- Zero-NAI cells primary: {primary_zero}/{n} ({pct(primary_zero / n)})",
        f"- Zero-NAI cells merged: {merged_zero}/{n} ({pct(merged_zero / n)})",
        f"- Zero-NAI cells resolved by merged POIs: {zero_resolved}/{n} ({pct(zero_resolved / n)})",
        "",
        "## Typology Counts",
        "",
        "| Typology B | Primary | Merged POIs | Delta |",
        "|---|---:|---:|---:|",
    ]
    for _, row in typology.iterrows():
        lines.append(f"| {row['typology']} | {row['primary_cells']} | {row['merged_cells']} | {row['delta_cells']:+d} |")
    lines += [
        "",
        "## Acceptance Rule",
        "",
        "Keep OSM-only as primary unless Overture-only spot-check reaches at least 70% confirmed and shows no severe systematic category error. Until then, this file is a sensitivity result, not the primary result.",
    ]
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--merged-pois", type=Path, default=Path("data/interim/merged_pois.gpkg"))
    parser.add_argument("--primary-metrics", type=Path, default=Path("data/processed/pilot_metrics.csv"))
    parser.add_argument("--merged-metrics", type=Path, default=Path("data/processed/pilot_metrics_merged_pois.csv"))
    parser.add_argument("--spot-check", type=Path, default=Path("data/interim/overture_only_spot_check.csv"))
    parser.add_argument("--output", type=Path, default=Path("outputs/validation/merged_poi_sensitivity.csv"))
    parser.add_argument("--summary", type=Path, default=Path("outputs/validation/merged_poi_sensitivity.md"))
    args = parser.parse_args()

    spot = make_spot_check(args.merged_pois, args.spot_check)
    print(f"Wrote {args.spot_check} ({len(spot)} Overture-only POIs)")
    if args.merged_metrics.exists():
        compare_metrics(args.primary_metrics, args.merged_metrics, args.output, args.summary)
        print(f"Wrote {args.output} and {args.summary}")
    else:
        print(f"Merged metrics not found yet: {args.merged_metrics}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
