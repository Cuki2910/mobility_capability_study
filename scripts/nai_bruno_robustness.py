"""Compute Bruno-style CCS/NPT diagnostics from walking-network routes."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import geopandas as gpd
import networkx as nx
import numpy as np
import pandas as pd

from scripts.audit_pois import NAI_CATEGORIES, poi_category
from src.neighborhood_access import (
    category_completeness,
    neighborhood_proximity_time,
    npt_benefit,
    weighted_gini,
    weighted_quantile,
)
from src.routing import load_timed_graph, nearest_graph_nodes


def _load_category_contract(path: Path) -> tuple[list[str], list[int], float]:
    """Read the intentionally small YAML contract without adding a parser dependency."""
    section, categories, ks, penalty = "", [], [], 20.0
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.endswith(":"):
            section = stripped[:-1]
        elif stripped.startswith("-"):
            value = stripped[1:].strip()
            (categories if section == "categories" else ks).append(int(value) if section == "requested_npt_k" else value)
        elif stripped.startswith("missing_category_penalty_min:"):
            penalty = float(stripped.split(":", 1)[1].strip())
    return categories, ks, penalty


def _coverage_rows(result: pd.DataFrame, thresholds: list[int], completeness: list[float]) -> pd.DataFrame:
    rows = []
    total_pop = result["pop_sum"].sum()
    for threshold in thresholds:
        ccs = result[f"CCS_{threshold}"]
        for q in completeness:
            mask = ccs >= q
            rows.append({
                "threshold_m": threshold,
                "completeness_threshold": q,
                "cell_share": float(mask.mean()),
                "population_share": float(result.loc[mask, "pop_sum"].sum() / total_pop),
            })
        zero = ccs.eq(0)
        rows.append({
            "threshold_m": threshold,
            "completeness_threshold": "zero_access",
            "cell_share": float(zero.mean()),
            "population_share": float(result.loc[zero, "pop_sum"].sum() / total_pop),
        })
    return pd.DataFrame(rows)


def _inequality_rows(result: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    rows = []
    weights = result["pop_sum"].to_numpy(dtype=float)
    for column in columns:
        values = result[column].to_numpy(dtype=float)
        quantiles = weighted_quantile(values, weights, np.array([0.1, 0.5, 0.9]))
        rows.append({
            "metric": column,
            "population_weighted_mean": float(np.average(values, weights=weights)),
            "population_weighted_p10": float(quantiles[0]),
            "population_weighted_median": float(quantiles[1]),
            "population_weighted_p90": float(quantiles[2]),
            "population_weighted_gini": weighted_gini(values, weights),
        })
    return pd.DataFrame(rows)


def _markdown_table(frame: pd.DataFrame, decimals: int = 4) -> str:
    """Render Markdown without depending on the optional tabulate package."""
    def render(value: object) -> str:
        return f"{value:.{decimals}f}" if isinstance(value, (float, np.floating)) else str(value)

    values = frame.copy()
    return "\n".join([
        "| " + " | ".join(values.columns) + " |",
        "| " + " | ".join("---" for _ in values.columns) + " |",
        *["| " + " | ".join(render(value) for value in row) + " |" for row in values.itertuples(index=False, name=None)],
    ])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--grid", type=Path, default=Path("data/interim/pilot_grid.gpkg"))
    parser.add_argument("--pois", type=Path, default=Path("data/interim/merged_pois_observed.gpkg"))
    parser.add_argument("--graph", type=Path, default=Path("data/raw/pilot_walk_network.graphml"))
    parser.add_argument("--population", type=Path, default=Path("data/interim/grid_worldpop.csv"))
    parser.add_argument("--thresholds-m", type=int, nargs="+", default=[600, 800, 1000, 1200])
    parser.add_argument("--category-contract", type=Path, default=Path("config/nai_categories.yml"))
    parser.add_argument("--output", type=Path, default=Path("outputs/validation/nai_bruno_cells.csv"))
    parser.add_argument("--summary", type=Path, default=Path("outputs/validation/nai_bruno_summary.md"))
    parser.add_argument("--coverage-output", type=Path, default=Path("outputs/validation/nai_population_coverage.csv"))
    parser.add_argument("--inequality-output", type=Path, default=Path("outputs/validation/nai_inequality.md"))
    parser.add_argument("--smci-output", type=Path, default=Path("outputs/validation/smci_npt_robustness.md"))
    parser.add_argument("--metrics", type=Path, default=Path("data/processed/pilot_metrics.csv"))
    args = parser.parse_args()

    contract_categories, requested_ks, penalty = _load_category_contract(args.category_contract)
    grid, pois = gpd.read_file(args.grid), gpd.read_file(args.pois)
    pois["nai_category"] = pois.apply(poi_category, axis=1)
    categories = list(NAI_CATEGORIES)
    if categories != contract_categories:
        raise ValueError("NAI category contract does not match scripts.audit_pois.NAI_CATEGORIES")
    graph, weight = load_timed_graph(args.graph, "walk")
    grid_pts = gpd.GeoDataFrame(geometry=grid.to_crs(3857).centroid.to_crs(4326), crs="EPSG:4326")
    poi_pts = gpd.GeoDataFrame(geometry=pois.to_crs(3857).centroid.to_crs(4326), crs="EPSG:4326")
    origins, destinations = nearest_graph_nodes(graph, grid_pts), nearest_graph_nodes(graph, poi_pts)
    by_category = {c: set(np.asarray(destinations)[pois["nai_category"].to_numpy() == c]) for c in categories}
    max_threshold = max(args.thresholds_m)
    cutoff_s = max_threshold / (4.8 * 1000 / 3600)
    times = np.full((len(grid), len(categories)), np.nan)
    counts = np.zeros_like(times)
    for i, origin in enumerate(origins):
        lengths = nx.single_source_dijkstra_path_length(graph, origin, cutoff=cutoff_s, weight=weight)
        for j, category in enumerate(categories):
            reached = [value for node, value in lengths.items() if node in by_category[category]]
            counts[i, j] = len(reached)
            if reached:
                times[i, j] = min(reached) / 60
    result = pd.DataFrame({"cell_id": grid["cell_id"].astype(int)})
    for j, category in enumerate(categories):
        result[f"reachable_{category}"] = counts[:, j].astype(int)
        result[f"nearest_{category}_min"] = times[:, j]
    # Apply each walking catchment to the same precomputed routes. Times beyond
    # the threshold remain missing and receive the declared penalty in NPT.
    for threshold in args.thresholds_m:
        within = np.where(times <= threshold / (4.8 * 1000 / 60), times, np.nan)
        ccs = category_completeness(np.where(np.isfinite(within), counts, 0))
        result[f"CCS_{threshold}"] = ccs
        for k in requested_ks:
            npt = neighborhood_proximity_time(
                within, k=k, missing_penalty_min=penalty, category_slots=max(k, len(categories))
            )
            result[f"NPT_K{k}_{threshold}_min"] = npt
            result[f"NPT_benefit_K{k}_{threshold}"] = npt_benefit(npt, penalty)
    result["CCS"] = result["CCS_800"]
    result["NPT_K1_min"] = result["NPT_K1_800_min"]
    result["NPT_K3_min"] = result["NPT_K3_800_min"]
    result["NPT_K5_min"] = result["NPT_K5_800_min"]
    total_counts = counts.sum(axis=1)
    result["local_access_class"] = np.select(
        [result["CCS"].eq(0), result["CCS"].lt(0.5), result["CCS"].lt(1) & (total_counts >= len(categories) * 2), result["CCS"].lt(1)],
        ["Zero", "Low", "Abundant-but-incomplete", "Incomplete"], default="Locally-complete"
    )
    pop = pd.read_csv(args.population, usecols=["cell_id", "pop_sum"])
    result = result.merge(pop, on="cell_id", how="left", validate="one_to_one")
    if result["pop_sum"].isna().any() or (result["pop_sum"] < 0).any():
        raise ValueError("WorldPop must provide a non-negative value for every grid cell")
    metrics = pd.read_csv(args.metrics)
    result = result.merge(metrics[["cell_id", "MAI_A_norm", "MAI_B_norm", "RAC_A_norm", "RAC_B_norm"]], on="cell_id", how="left", validate="one_to_one")
    benefit = result["NPT_benefit_K3_800"].to_numpy(dtype=float)
    for scenario in ("A", "B"):
        product = benefit * result[f"MAI_{scenario}_norm"].to_numpy() * result[f"RAC_{scenario}_norm"].to_numpy()
        result[f"SMCI_NPT_product_{scenario}"] = product
        result[f"SMCI_NPT_geometric_{scenario}"] = np.cbrt(product)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False)
    result_gpkg = args.output.with_suffix(".gpkg")
    grid.merge(result, on="cell_id", validate="one_to_one").to_file(result_gpkg, driver="GPKG")
    coverage = _coverage_rows(result, args.thresholds_m, [0.50, 0.67, 0.75])
    coverage.to_csv(args.coverage_output, index=False)
    inequality = _inequality_rows(result, ["CCS_800", "NPT_K1_800_min", "NPT_K3_800_min", "NPT_benefit_K3_800"])
    args.inequality_output.write_text("# Bruno NAI Population-Weighted Inequality\n\n" + _markdown_table(inequality) + "\n", encoding="utf-8")
    class_counts = result["local_access_class"].value_counts()
    lines = ["# Bruno NAI Robustness", "", "- Primary threshold: 800 m network walking", f"- Sensitivity thresholds: {', '.join(map(str, args.thresholds_m))} m", f"- Missing-category penalty: {penalty:g} min", "- The four observed categories are school, healthcare, retail, and park. K=5 adds one declared penalty slot rather than silently using K=4.", f"- Mean CCS (800 m): {result['CCS'].mean():.3f}", f"- Population-weighted CCS Gini (800 m): {weighted_gini(result['CCS'].to_numpy(), result['pop_sum'].to_numpy()):.3f}", "", "## Local access classes", ""]
    lines += [f"- {label}: {int(count)} cells" for label, count in class_counts.items()]
    lines += ["", "## Coverage", "", _markdown_table(coverage, decimals=3), "", "## Interpretation", "", "These are supplementary local-access robustness diagnostics. They do not replace the primary rank-based NAI x MCS typology and are not observed travel behavior."]
    args.summary.write_text("\n".join(lines) + "\n", encoding="utf-8")
    smci_lines = ["# SMCI NPT Robustness", "", "NPT benefit is 1 - NPT/20, clipped to [0, 1]. Product and geometric forms are both shown explicitly; neither replaces the canonical GM SMCI.", "", "| Metric | Scenario A | Scenario B |", "|---|---:|---:|"]
    for operator in ("product", "geometric"):
        smci_lines.append(f"| Mean SMCI_NPT_{operator} | {result[f'SMCI_NPT_{operator}_A'].mean():.4f} | {result[f'SMCI_NPT_{operator}_B'].mean():.4f} |")
    args.smci_output.write_text("\n".join(smci_lines) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}, {result_gpkg}, {args.summary}, {args.coverage_output}, {args.inequality_output}, and {args.smci_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
