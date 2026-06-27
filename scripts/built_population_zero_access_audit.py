"""Audit zero-access cells against building footprints and WorldPop."""
from __future__ import annotations

import argparse
from pathlib import Path

import geopandas as gpd
import pandas as pd


def classify_land_use(row: pd.Series) -> str:
    if row["building_count"] > 0:
        return "built"
    if row["pop_sum"] < 1:
        return "unbuilt_or_open_space"
    return "suspect_under_mapped"


def pct(value: float) -> str:
    return f"{value:.1%}"


def build_audit(metrics_path: Path, buildings_path: Path, worldpop_path: Path) -> pd.DataFrame:
    metrics = pd.read_csv(metrics_path)
    buildings = gpd.read_file(buildings_path).drop(columns="geometry", errors="ignore")
    worldpop = pd.read_csv(worldpop_path)

    required = {"cell_id", "NAI", "SMCI_B", "typology_B"}
    missing = required - set(metrics.columns)
    if missing:
        raise ValueError(f"Missing metrics columns: {sorted(missing)}")

    out = metrics.merge(
        buildings[["cell_id", "building_count", "building_footprint_area_m2"]],
        on="cell_id",
        how="left",
    ).merge(
        worldpop[["cell_id", "pop_sum", "pop_density_per_km2"]],
        on="cell_id",
        how="left",
    )
    out["building_count"] = out["building_count"].fillna(0).astype(int)
    out["building_footprint_area_m2"] = out["building_footprint_area_m2"].fillna(0.0)
    out["pop_sum"] = out["pop_sum"].fillna(0.0)
    out["pop_density_per_km2"] = out["pop_density_per_km2"].fillna(0.0)
    out["built_class"] = out.apply(classify_land_use, axis=1)
    out["zero_nai"] = out["NAI"] <= 0
    out["zero_smci_b"] = out["SMCI_B"] <= 0
    out["zero_access_built"] = out["zero_nai"] & (out["built_class"] == "built")
    return out


def write_summary(audit: pd.DataFrame, output_md: Path) -> None:
    total_cells = len(audit)
    total_pop = float(audit["pop_sum"].sum())
    zero_nai = audit[audit["zero_nai"]]
    zero_smci = audit[audit["zero_smci_b"]]
    zero_access_built = audit[audit["zero_access_built"]]
    analysis_cells = audit[audit["built_class"] != "unbuilt_or_open_space"]

    class_summary = audit.groupby("built_class", dropna=False).agg(
        cells=("cell_id", "count"),
        population=("pop_sum", "sum"),
        zero_nai_cells=("zero_nai", "sum"),
        zero_smci_b_cells=("zero_smci_b", "sum"),
    ).reset_index()
    class_summary["cell_share"] = class_summary["cells"] / total_cells
    class_summary["population_share"] = class_summary["population"] / total_pop if total_pop else 0.0
    class_summary["zero_nai_share_within_class"] = class_summary["zero_nai_cells"] / class_summary["cells"]
    class_summary["zero_smci_b_share_within_class"] = class_summary["zero_smci_b_cells"] / class_summary["cells"]

    typology = analysis_cells["typology_B"].value_counts().rename_axis("typology").reset_index(name="cells")
    typology["share"] = typology["cells"] / len(analysis_cells) if len(analysis_cells) else 0.0

    lines = [
        "# Built/Population Zero-Access Audit",
        "",
        "Primary metrics use the current promoted POI layer. This audit checks whether zero-access cells are built, unbuilt/open-space, or potentially under-mapped.",
        "",
        "## Headline",
        "",
        f"- Grid cells: {total_cells}",
        f"- Built cells: {int((audit['built_class'] == 'built').sum())} ({pct((audit['built_class'] == 'built').mean())})",
        f"- Zero-NAI cells: {len(zero_nai)} ({pct(len(zero_nai) / total_cells)})",
        f"- Zero-SMCI_B cells: {len(zero_smci)} ({pct(len(zero_smci) / total_cells)})",
        f"- Zero-NAI built cells: {len(zero_access_built)} ({pct(len(zero_access_built) / total_cells)})",
        f"- Population in zero-NAI built cells: {zero_access_built['pop_sum'].sum():,.0f} ({pct(zero_access_built['pop_sum'].sum() / total_pop) if total_pop else '0.0%'})",
        "",
        "## Built Class Summary",
        "",
        "| Built class | Cells | Cell share | Population | Pop share | Zero NAI within class | Zero SMCI_B within class |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in class_summary.iterrows():
        lines.append(
            f"| {row['built_class']} | {int(row['cells'])} | {pct(row['cell_share'])} | "
            f"{row['population']:,.0f} | {pct(row['population_share'])} | "
            f"{pct(row['zero_nai_share_within_class'])} | {pct(row['zero_smci_b_share_within_class'])} |"
        )
    lines += [
        "",
        "## Typology Distribution Excluding Unbuilt/Open-Space Cells",
        "",
        "| Typology B | Cells | Share |",
        "|---|---:|---:|",
    ]
    for _, row in typology.iterrows():
        lines.append(f"| {row['typology']} | {int(row['cells'])} | {pct(row['share'])} |")
    lines += [
        "",
        "## Interpretation",
        "",
        "Building footprints are present in nearly all cells, so zero inflation cannot be dismissed as only lakes, parks, or open space. Treat zero-NAI built cells as a mapping/accessibility issue that needs cautious interpretation in typology claims.",
    ]
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metrics", type=Path, default=Path("data/processed/pilot_metrics.csv"))
    parser.add_argument("--buildings", type=Path, default=Path("data/interim/grid_building_footprints.gpkg"))
    parser.add_argument("--worldpop", type=Path, default=Path("data/interim/grid_worldpop.csv"))
    parser.add_argument("--output", type=Path, default=Path("outputs/validation/built_population_zero_access.csv"))
    parser.add_argument("--summary", type=Path, default=Path("outputs/validation/built_population_zero_access.md"))
    args = parser.parse_args()

    audit = build_audit(args.metrics, args.buildings, args.worldpop)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    audit.to_csv(args.output, index=False)
    write_summary(audit, args.summary)
    print(f"Wrote {args.output} and {args.summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
