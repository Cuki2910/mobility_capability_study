"""Reviewer-risk metric variant audit.

Runs the metric changes raised in red-team review:
- NAI diversity and category-capped NAI
- RAC full vs time-only vs opportunity-only
- minmax vs winsorized vs log normalization
- multiplicative vs additive SMCI
- alternative typology thresholds
- MAI weight/decay/top-opportunity leverage rebuilds
- strict observed excluded-POI spatial missingness

Outputs:
  outputs/validation/metric_variant_audit.csv
  outputs/validation/metric_variant_audit.md
  outputs/validation/metric_variant_cells.csv
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from statsmodels.stats.outliers_influence import variance_inflation_factor

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.accessibility import MAI_DOMAIN_WEIGHTS
from src.accessibility_inputs import build_network_accessibility_inputs
from src.pilot import compute_pilot_metrics

TYPOLOGIES = [
    "Integrated Capability",
    "Fragmented Capability",
    "Transit-Dependent",
    "Motorcycle Lock-in",
]


def _norm_single(x: np.ndarray, method: str = "minmax") -> np.ndarray:
    x = np.asarray(x, dtype=float)
    if method == "log":
        x = np.log1p(np.maximum(x, 0.0))
    if method == "winsor":
        lo_q, hi_q = np.nanpercentile(x, [1, 99])
        x = np.clip(x, lo_q, hi_q)
    lo, hi = float(np.nanmin(x)), float(np.nanmax(x))
    if hi == lo:
        return np.zeros_like(x, dtype=float)
    return (x - lo) / (hi - lo)


def _norm_pair(a: np.ndarray, b: np.ndarray, method: str = "minmax") -> tuple[np.ndarray, np.ndarray]:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if method == "log":
        a = np.log1p(np.maximum(a, 0.0))
        b = np.log1p(np.maximum(b, 0.0))
    combined = np.concatenate([a, b])
    if method == "winsor":
        lo_q, hi_q = np.nanpercentile(combined, [1, 99])
        a = np.clip(a, lo_q, hi_q)
        b = np.clip(b, lo_q, hi_q)
        combined = np.concatenate([a, b])
    lo, hi = float(np.nanmin(combined)), float(np.nanmax(combined))
    if hi == lo:
        return np.zeros_like(a, dtype=float), np.zeros_like(b, dtype=float)
    return (a - lo) / (hi - lo), (b - lo) / (hi - lo)


def _rank_typology(nai: np.ndarray, mcs: np.ndarray) -> np.ndarray:
    n = len(nai)
    nai_rank = np.argsort(np.argsort(nai, kind="stable"), kind="stable")
    mcs_rank = np.argsort(np.argsort(mcs, kind="stable"), kind="stable")
    nai_hi = nai_rank >= n // 2
    mcs_hi = mcs_rank >= n // 2
    return _labels(nai_hi, mcs_hi)


def _labels(nai_hi: np.ndarray, mcs_hi: np.ndarray) -> np.ndarray:
    labels = np.empty(len(nai_hi), dtype=object)
    labels[nai_hi & mcs_hi] = "Integrated Capability"
    labels[nai_hi & ~mcs_hi] = "Fragmented Capability"
    labels[~nai_hi & mcs_hi] = "Transit-Dependent"
    labels[~nai_hi & ~mcs_hi] = "Motorcycle Lock-in"
    return labels


def _kappa(a: np.ndarray, b: np.ndarray) -> float:
    classes = np.unique(np.concatenate([a, b]))
    p_o = float((a == b).mean())
    p_e = sum((a == c).mean() * (b == c).mean() for c in classes)
    return (p_o - p_e) / (1.0 - p_e) if p_e < 1.0 else 1.0


def _vif(df: pd.DataFrame) -> dict[str, float]:
    x = df.to_numpy(dtype=float)
    rows = {}
    for i, col in enumerate(df.columns):
        rows[col] = float(variance_inflation_factor(x, i))
    return rows


def _daily_category(row: pd.Series) -> str:
    def tag(key: str) -> str:
        val = row.get(key)
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return ""
        s = str(val).strip().lower()
        return "" if s in {"", "nan", "none"} else s

    amenity = tag("amenity")
    shop = tag("shop")
    leisure = tag("leisure")
    tourism = tag("tourism")
    category = tag("category")
    office = tag("office")
    public_transport = tag("public_transport")

    if amenity in {"school", "university", "college", "kindergarten", "language_school"} or category == "education":
        return "education"
    if amenity in {"hospital", "clinic", "doctors", "dentist", "pharmacy"} or category == "health_and_medical":
        return "healthcare"
    if amenity in {"restaurant", "cafe", "fast_food", "food_court", "bar", "pub"} or category == "food_and_beverage":
        return "food"
    if shop:
        return "retail"
    if leisure or tourism or amenity in {"park", "playground", "cinema", "theatre", "community_centre"}:
        return "leisure"
    if amenity in {"bank", "atm", "post_office"} or category == "financial_service":
        return "finance_service"
    if public_transport or amenity in {"bus_station", "ferry_terminal"} or category == "transportation":
        return "transport"
    if office:
        return "work_service"
    return "other_service"


def compute_nai_variants(args: argparse.Namespace) -> pd.DataFrame:
    import geopandas as gpd
    import networkx as nx

    from src.routing import load_timed_graph, nearest_graph_nodes

    grid = gpd.read_file(args.grid)
    pois = gpd.read_file(args.pois)
    graph, weight = load_timed_graph(args.walk_graph, "walk")

    grid_pts = gpd.GeoDataFrame(
        grid[["cell_id"]].copy(),
        geometry=gpd.GeoSeries(grid.to_crs(epsg=3857).geometry.centroid, crs="EPSG:3857").to_crs(epsg=4326),
        crs="EPSG:4326",
    )
    poi_pts = gpd.GeoDataFrame(
        pois.drop(columns="geometry", errors="ignore").copy(),
        geometry=gpd.GeoSeries(pois.to_crs(epsg=3857).geometry.centroid, crs="EPSG:3857").to_crs(epsg=4326),
        crs="EPSG:4326",
    )
    grid_nodes = nearest_graph_nodes(graph, grid_pts)
    poi_nodes = nearest_graph_nodes(graph, poi_pts)
    categories = [_daily_category(row) for _, row in pois.iterrows()]
    unique_categories = sorted(set(categories))
    node_to_cats: dict[int, list[str]] = {}
    for node, cat in zip(poi_nodes, categories):
        node_to_cats.setdefault(node, []).append(cat)

    rows = []
    cutoff_s = args.walk_cutoff_min * 60.0
    for cell_id, origin in zip(grid["cell_id"].astype(str), grid_nodes):
        lengths = nx.single_source_dijkstra_path_length(graph, origin, cutoff=cutoff_s, weight=weight)
        counts = {cat: 0 for cat in unique_categories}
        for node in lengths:
            for cat in node_to_cats.get(node, []):
                counts[cat] += 1
        row = {
            "cell_id": cell_id,
            "NAI_diversity": float(sum(v > 0 for v in counts.values())),
            "NAI_capped": float(sum(min(v, args.nai_category_cap) for v in counts.values())),
        }
        row.update({f"NAI_cat_{cat}": float(v) for cat, v in counts.items()})
        rows.append(row)
    return pd.DataFrame(rows)


def compute_excluded_missingness(args: argparse.Namespace) -> pd.DataFrame:
    import geopandas as gpd

    if not args.audit_csv.exists():
        return pd.DataFrame()
    audit = pd.read_csv(args.audit_csv, dtype={"poi_id": str})
    excluded_ids = set(audit.loc[audit["include_in_mai"].astype(str).str.lower().isin({"false", "0"}), "poi_id"].astype(str))
    if not excluded_ids:
        return pd.DataFrame()
    grid = gpd.read_file(args.grid).to_crs(epsg=3857)
    pois = gpd.read_file(args.pois)
    id_col = "id" if "id" in pois.columns else ("poi_id" if "poi_id" in pois.columns else None)
    if id_col is None:
        return pd.DataFrame()
    excluded = pois[pois[id_col].astype(str).isin(excluded_ids)].to_crs(epsg=3857)
    if excluded.empty:
        return pd.DataFrame()
    centroids = grid.geometry.centroid
    poi_points = excluded.geometry.centroid
    counts = []
    for geom in centroids:
        counts.append(int((poi_points.distance(geom) <= args.excluded_radius_m).sum()))
    return pd.DataFrame({
        "cell_id": grid["cell_id"].astype(str).to_numpy(),
        "strict_excluded_pois_800m": counts,
    })


def compute_variant(
    base: pd.DataFrame,
    nai: np.ndarray,
    name: str,
    rac_variant: str = "full",
    norm_method: str = "minmax",
    smci_kind: str = "product",
    typology_kind: str = "rank",
    nai_abs_threshold: float | None = None,
    mcs_abs_threshold: float | None = None,
) -> tuple[dict, pd.DataFrame]:
    nai = np.asarray(nai, dtype=float)
    nai_norm = _norm_single(nai, norm_method)
    mai_a_norm, mai_b_norm = _norm_pair(base["MAI_A"], base["MAI_B"], norm_method)

    rt_a, rt_b = _norm_pair(base["RAC_time_A_raw"], base["RAC_time_B_raw"], norm_method)
    ro_a, ro_b = _norm_pair(base["RAC_opp_A_raw"], base["RAC_opp_B_raw"], norm_method)
    if rac_variant == "full":
        rac_a_raw = np.sqrt(rt_a * ro_a)
        rac_b_raw = np.sqrt(rt_b * ro_b)
        rac_a_norm, rac_b_norm = _norm_pair(rac_a_raw, rac_b_raw, norm_method)
        rac_label = "RAC"
    elif rac_variant == "time_only":
        rac_a_norm, rac_b_norm = rt_a, rt_b
        rac_label = "RAC_time"
    elif rac_variant == "opp_only":
        rac_a_norm, rac_b_norm = ro_a, ro_b
        rac_label = "RAC_opp"
    else:
        raise ValueError(f"unknown rac_variant={rac_variant}")

    mcs_b = np.sqrt(mai_b_norm * rac_b_norm)
    if smci_kind == "product":
        smci_b = nai_norm * mai_b_norm * rac_b_norm
    elif smci_kind == "additive":
        smci_b = (nai_norm + mai_b_norm + rac_b_norm) / 3.0
    else:
        raise ValueError(f"unknown smci_kind={smci_kind}")

    if typology_kind == "rank":
        labels = _rank_typology(nai, mcs_b)
    elif typology_kind == "absolute":
        if nai_abs_threshold is None or mcs_abs_threshold is None:
            raise ValueError("absolute typology requires thresholds")
        labels = _labels(nai >= nai_abs_threshold, mcs_b >= mcs_abs_threshold)
    else:
        raise ValueError(f"unknown typology_kind={typology_kind}")

    vif = _vif(pd.DataFrame({"NAI": nai_norm, "MAI": mai_b_norm, rac_label: rac_b_norm}))
    cell_df = pd.DataFrame({
        "cell_id": base["cell_id"].astype(str),
        f"{name}_NAI": nai,
        f"{name}_MCS_B": mcs_b,
        f"{name}_SMCI_B": smci_b,
        f"{name}_typology_B": labels,
    })
    summary = {
        "variant": name,
        "family": "postprocess",
        "nai_variant": "custom",
        "rac_variant": rac_variant,
        "norm_method": norm_method,
        "smci_kind": smci_kind,
        "typology_kind": typology_kind,
        "mean_SMCI_B": float(smci_b.mean()),
        "zero_SMCI_B_cells": int((smci_b == 0).sum()),
        "typology_counts": "; ".join(f"{t}:{int((labels == t).sum())}" for t in TYPOLOGIES),
        "VIF_NAI": float(vif["NAI"]),
        "VIF_MAI": float(vif["MAI"]),
        "VIF_RAC": float(vif[rac_label]),
        "max_VIF": float(max(vif.values())),
    }
    return summary, cell_df


def summarize_rebuild(name: str, inputs: pd.DataFrame, baseline: pd.DataFrame) -> dict:
    metrics = compute_pilot_metrics(inputs)
    rho, _ = spearmanr(baseline["SMCI_B"], metrics["SMCI_B"])
    return {
        "variant": name,
        "family": "rebuild",
        "mean_SMCI_B": float(metrics["SMCI_B"].mean()),
        "share_improved": float((metrics["Delta_SMCI"] > 0).mean()),
        "zero_SMCI_B_cells": int((metrics["SMCI_B"] == 0).sum()),
        "kappa_vs_current": _kappa(baseline["typology_B"].to_numpy(), metrics["typology_B"].to_numpy()),
        "spearman_SMCI_vs_current": float(rho),
        "cells_relabelled": int((baseline["typology_B"].to_numpy() != metrics["typology_B"].to_numpy()).sum()),
    }


def build_inputs(args: argparse.Namespace, **kwargs) -> pd.DataFrame:
    vinbus_geometry = args.vinbus_geometry if args.vinbus_geometry.exists() else None
    vinbus_gtfs_dir = args.vinbus_gtfs_dir if (args.vinbus_gtfs_dir / "stops.txt").exists() else None
    speed_csv = args.speed_factor_csv if args.speed_factor_csv.exists() else None
    return build_network_accessibility_inputs(
        args.grid,
        args.pois,
        args.walk_graph,
        args.drive_graph,
        vinbus_geometry_json=vinbus_geometry,
        gtfs_zip=args.gtfs if args.gtfs.exists() else None,
        gtfs_status="baseline_limited",
        speed_factor_csv=speed_csv,
        vinbus_gtfs_dir=vinbus_gtfs_dir,
        walk_cutoff_min=args.walk_cutoff_min,
        buildings_path=args.buildings if args.buildings.exists() else None,
        pop_weighting=True,
        worldpop_csv=args.worldpop_csv if args.worldpop_csv.exists() else None,
        opportunity_basis=args.opportunity_basis,
        **kwargs,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--grid", type=Path, default=Path("data/interim/pilot_grid.gpkg"))
    parser.add_argument("--pois", type=Path, default=Path("data/interim/merged_pois_observed.gpkg"))
    parser.add_argument("--audit-csv", type=Path, default=Path("data/interim/poi_observed_audit.csv"))
    parser.add_argument("--walk-graph", type=Path, default=Path("data/raw/pilot_walk_network.graphml"))
    parser.add_argument("--drive-graph", type=Path, default=Path("data/raw/pilot_drive_network.graphml"))
    parser.add_argument("--vinbus-geometry", type=Path, default=Path("data/raw/vinbus_overpass_relations_geom.json"))
    parser.add_argument("--vinbus-gtfs-dir", type=Path, default=Path("data/raw/vinbus_pseudo_gtfs_fixed"))
    parser.add_argument("--speed-factor-csv", type=Path, default=Path("data/raw/motorcycle_speed_calibration.csv"))
    parser.add_argument("--gtfs", type=Path, default=Path("data/raw/hanoi_gtfs.zip"))
    parser.add_argument("--buildings", type=Path, default=Path("data/raw/building_footprints.gpkg"))
    parser.add_argument("--worldpop-csv", type=Path, default=Path("data/interim/grid_worldpop.csv"))
    parser.add_argument("--opportunity-basis", choices=["proxy", "observed", "observed_strict"], default="observed_strict")
    parser.add_argument(
        "--walk-cutoff-min",
        type=float,
        default=10.0,
        help="NAI walk cutoff in minutes. Default matches the 800 m / 80 m-min primary (Decision #27).",
    )
    parser.add_argument("--nai-category-cap", type=int, default=3)
    parser.add_argument("--excluded-radius-m", type=float, default=800.0)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/validation"))
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    print("Building strict baseline inputs...")
    baseline_inputs = build_inputs(args, t_full_min=30.0, t_zero_min=60.0, decay_kind="linear", domain_weights=MAI_DOMAIN_WEIGHTS["default"])
    baseline_metrics = compute_pilot_metrics(baseline_inputs)
    baseline_metrics["cell_id"] = baseline_metrics["cell_id"].astype(str)

    nai_variants = compute_nai_variants(args)
    missingness = compute_excluded_missingness(args)
    nai_variants["cell_id"] = nai_variants["cell_id"].astype(str)
    base = baseline_metrics.merge(nai_variants, on="cell_id", how="left")
    if not missingness.empty:
        missingness["cell_id"] = missingness["cell_id"].astype(str)
        base = base.merge(missingness, on="cell_id", how="left")
    base["strict_excluded_pois_800m"] = base.get("strict_excluded_pois_800m", pd.Series(np.zeros(len(base)))).fillna(0)

    summaries: list[dict] = []
    cell_frames: list[pd.DataFrame] = []

    candidate_specs = [
        ("legacy_full_rac", "NAI", "full", "minmax", "product", "rank", None, None),
        ("nai_diversity", "NAI_diversity", "full", "minmax", "product", "rank", None, None),
        ("nai_capped", "NAI_capped", "full", "minmax", "product", "rank", None, None),
        ("rac_time_only", "NAI", "time_only", "minmax", "product", "rank", None, None),
        ("rac_opp_only", "NAI", "opp_only", "minmax", "product", "rank", None, None),
        ("winsor_norm", "NAI", "full", "winsor", "product", "rank", None, None),
        ("log_norm", "NAI", "full", "log", "product", "rank", None, None),
        ("additive_smci", "NAI", "full", "minmax", "additive", "rank", None, None),
        ("reviewer_safe_capped_time_winsor", "NAI_capped", "time_only", "winsor", "product", "rank", None, None),
        ("reviewer_safe_diversity_time_winsor", "NAI_diversity", "time_only", "winsor", "product", "rank", None, None),
        ("absolute_count5_mcs60", "NAI", "full", "minmax", "product", "absolute", 5.0, None),
        ("absolute_diversity4_mcs60", "NAI_diversity", "full", "minmax", "product", "absolute", 4.0, None),
    ]
    baseline_labels = baseline_metrics["typology_B"].to_numpy()
    baseline_smci = baseline_metrics["SMCI_B"].to_numpy()
    baseline_mcs60 = float(np.nanpercentile(baseline_metrics["MCS_B"], 60))

    for name, nai_col, rac_var, norm, smci, typo, nai_thr, mcs_thr in candidate_specs:
        if typo == "absolute" and mcs_thr is None:
            mcs_thr = baseline_mcs60
        summary, cells = compute_variant(
            base,
            base[nai_col].to_numpy(dtype=float),
            name,
            rac_variant=rac_var,
            norm_method=norm,
            smci_kind=smci,
            typology_kind=typo,
            nai_abs_threshold=nai_thr,
            mcs_abs_threshold=mcs_thr,
        )
        labels = cells[f"{name}_typology_B"].to_numpy()
        smci_vals = cells[f"{name}_SMCI_B"].to_numpy()
        rho, _ = spearmanr(baseline_smci, smci_vals)
        summary.update({
            "nai_variant": nai_col,
            "kappa_vs_current": _kappa(baseline_labels, labels),
            "spearman_SMCI_vs_current": float(rho),
            "cells_relabelled": int((baseline_labels != labels).sum()),
            "share_cells_with_excluded_poi_800m": float((base["strict_excluded_pois_800m"] > 0).mean()),
            "max_excluded_pois_800m": int(base["strict_excluded_pois_800m"].max()),
        })
        summaries.append(summary)
        cell_frames.append(cells)

    rebuild_specs = [
        ("weights_equal", {"domain_weights": MAI_DOMAIN_WEIGHTS["equal"]}),
        ("weights_job_heavy", {"domain_weights": MAI_DOMAIN_WEIGHTS["job_heavy"]}),
        ("weights_econ_light", {"domain_weights": MAI_DOMAIN_WEIGHTS["econ_light"]}),
        ("weights_service_health_heavy", {"domain_weights": MAI_DOMAIN_WEIGHTS["service_health_heavy"]}),
        ("decay_20_40", {"t_full_min": 20.0, "t_zero_min": 40.0, "decay_kind": "linear"}),
        ("decay_45_90", {"t_full_min": 45.0, "t_zero_min": 90.0, "decay_kind": "linear"}),
        ("decay_exponential_30_60", {"t_full_min": 30.0, "t_zero_min": 60.0, "decay_kind": "exponential"}),
        ("mai_no_top1pct", {"drop_top_opportunity_pct": 1.0}),
        ("mai_no_top5pct", {"drop_top_opportunity_pct": 5.0}),
    ]
    for name, kwargs in rebuild_specs:
        full_kwargs = {"t_full_min": 30.0, "t_zero_min": 60.0, "decay_kind": "linear", "domain_weights": MAI_DOMAIN_WEIGHTS["default"]}
        full_kwargs.update(kwargs)
        print(f"Rebuilding variant: {name}")
        inputs = build_inputs(args, **full_kwargs)
        summaries.append(summarize_rebuild(name, inputs, baseline_metrics))

    summary_df = pd.DataFrame(summaries)
    post = summary_df[summary_df["family"] == "postprocess"].copy()
    eligible = post[
        (post["kappa_vs_current"] >= 0.85)
        & (post["spearman_SMCI_vs_current"] >= 0.95)
        & (post["zero_SMCI_B_cells"] <= int((baseline_smci == 0).sum()))
    ].copy()
    if not eligible.empty:
        eligible["promotion_score"] = (
            -eligible["max_VIF"].fillna(999.0)
            + eligible["kappa_vs_current"].fillna(0.0)
            + eligible["spearman_SMCI_vs_current"].fillna(0.0)
        )
        recommended = eligible.sort_values(["promotion_score", "mean_SMCI_B"], ascending=False).iloc[0]["variant"]
    else:
        recommended = "current"
    summary_df["recommended_primary"] = summary_df["variant"].eq(recommended)

    cell_out = base[["cell_id", "NAI", "NAI_diversity", "NAI_capped", "strict_excluded_pois_800m"]].copy()
    for cells in cell_frames:
        cell_out = cell_out.merge(cells, on="cell_id", how="left")

    summary_csv = args.output_dir / "metric_variant_audit.csv"
    cells_csv = args.output_dir / "metric_variant_cells.csv"
    md_path = args.output_dir / "metric_variant_audit.md"
    summary_df.to_csv(summary_csv, index=False)
    cell_out.to_csv(cells_csv, index=False)

    current = summary_df.loc[summary_df["variant"] == "legacy_full_rac"].iloc[0]
    recommended_row = summary_df.loc[summary_df["variant"] == recommended].iloc[0]
    lines = [
        "# Metric Variant Audit",
        "",
        "Reviewer-risk variants were compared against the current strict observed MAI specification.",
        "",
        "## Recommendation",
        "",
        f"- Recommended primary candidate: **{recommended}**",
        f"- Legacy full-RAC max VIF: {current.get('max_VIF', np.nan):.2f}",
        f"- Recommended max VIF: {recommended_row.get('max_VIF', np.nan):.2f}",
        f"- Kappa vs current typology: {recommended_row.get('kappa_vs_current', np.nan):.4f}",
        f"- Spearman rho vs current SMCI_B: {recommended_row.get('spearman_SMCI_vs_current', np.nan):.4f}",
        f"- Relabelled cells vs current: {int(recommended_row.get('cells_relabelled', 0))} / {len(base)}",
        "",
        "Promotion rule: eligible candidates must keep kappa >= 0.85, Spearman rho >= 0.95, and not increase zero-SMCI cells; among them, the lowest-VIF candidate wins.",
        "",
        "## Post-process Metric Candidates",
        "",
        "| Variant | NAI | RAC | Norm | SMCI | Kappa | Rho | Max VIF | Zero SMCI | Relabelled |",
        "|---|---|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for _, r in post.iterrows():
        lines.append(
            f"| {r['variant']} | {r.get('nai_variant', '')} | {r.get('rac_variant', '')} | "
            f"{r.get('norm_method', '')} | {r.get('smci_kind', '')} | "
            f"{r.get('kappa_vs_current', np.nan):.4f} | {r.get('spearman_SMCI_vs_current', np.nan):.4f} | "
            f"{r.get('max_VIF', np.nan):.2f} | {int(r.get('zero_SMCI_B_cells', 0))} | {int(r.get('cells_relabelled', 0))} |"
        )
    lines += [
        "",
        "## Rebuild Sensitivities",
        "",
        "| Variant | Mean SMCI_B | Share improved | Kappa | Rho | Zero SMCI | Relabelled |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, r in summary_df[summary_df["family"] == "rebuild"].iterrows():
        lines.append(
            f"| {r['variant']} | {r.get('mean_SMCI_B', np.nan):.4f} | {r.get('share_improved', np.nan):.1%} | "
            f"{r.get('kappa_vs_current', np.nan):.4f} | {r.get('spearman_SMCI_vs_current', np.nan):.4f} | "
            f"{int(r.get('zero_SMCI_B_cells', 0))} | {int(r.get('cells_relabelled', 0))} |"
        )
    lines += [
        "",
        "## Missingness",
        "",
        f"- Cells within {args.excluded_radius_m:.0f} m of at least one strict-excluded POI: {(base['strict_excluded_pois_800m'] > 0).mean():.1%}",
        f"- Max strict-excluded POIs within {args.excluded_radius_m:.0f} m of a cell: {int(base['strict_excluded_pois_800m'].max())}",
        "",
        f"Wrote `{summary_csv}` and `{cells_csv}`.",
    ]
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {summary_csv}, {cells_csv}, {md_path}")
    print(f"Recommended primary candidate: {recommended}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
