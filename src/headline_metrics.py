"""Build one machine-readable snapshot of publication headline metrics."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

SCHEMA_VERSION = 3
FLOAT_ABS_TOLERANCE = 1e-12

SENSITIVITY_INPUTS = {
    "motorcycle_speed": (
        "outputs/validation/motorcycle_speed_sensitivity.csv",
        ("scenario", "mean_SMCI_B", "typology_kappa_vs_baseline", "cells_relabelled_vs_baseline"),
    ),
    "transit_impedance": (
        "outputs/validation/transit_impedance_sensitivity.csv",
        ("scenario", "mean_SMCI_B", "typology_kappa_vs_baseline", "cells_relabelled_vs_baseline"),
    ),
    "nai_threshold": (
        "outputs/validation/nai_threshold_sensitivity.csv",
        ("threshold_m", "n_cells", "mean_SMCI_B", "typology_kappa_vs_reference"),
    ),
    "observed_vs_proxy": (
        "outputs/validation/observed_vs_proxy_sensitivity.csv",
        ("metric", "proxy", "observed", "observed_strict"),
    ),
    "rac_scaling_kappa": (
        "outputs/validation/rac_scaling_kappa.csv", ("comparison", "cohens_kappa"),
    ),
    "rac_scaling_spearman": (
        "outputs/validation/rac_scaling_spearman.csv", ("comparison", "spearman_rho_smci"),
    ),
    "rac_scaling_typology_shift": (
        "outputs/validation/rac_scaling_typology_shift.csv",
        ("from_minmax", "to_log_minmax", "n_cells"),
    ),
}


def _read(root: Path, relative: str, required: tuple[str, ...] = ()) -> pd.DataFrame:
    path = root / relative
    if not path.exists():
        raise FileNotFoundError(f"Missing canonical headline input: {relative}")
    frame = pd.read_csv(path)
    missing = sorted(set(required) - set(frame.columns))
    if missing:
        raise ValueError(f"{relative} missing columns: {', '.join(missing)}")
    return frame


def _finite(value: Any, label: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{label} must be finite")
    return result


def _records(frame: pd.DataFrame, label: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for row in frame.to_dict(orient="records"):
        clean: dict[str, Any] = {}
        for key, value in row.items():
            if pd.isna(value):
                raise ValueError(f"{label}.{key} contains a missing value")
            clean[str(key)] = value.item() if isinstance(value, np.generic) else value
        records.append(clean)
    return records


def _counts(series: pd.Series) -> dict[str, int]:
    return {str(key): int(value) for key, value in series.value_counts().sort_index().items()}


def _assert_close(actual: Any, expected: Any, label: str) -> None:
    if not math.isclose(_finite(actual, label), _finite(expected, label),
                        rel_tol=0.0, abs_tol=FLOAT_ABS_TOLERANCE):
        raise ValueError(f"{label} disagrees with pilot_metrics")


def load_headline_metrics(path: Path) -> dict[str, Any]:
    """Load a snapshot only when its schema is current."""
    import json

    snapshot = json.loads(path.read_text(encoding="utf-8"))
    if snapshot.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(
            f"Unsupported headline schema: {snapshot.get('schema_version')}; "
            f"expected {SCHEMA_VERSION}"
        )
    return snapshot


def build_headline_metrics(root: Path = Path(".")) -> dict[str, Any]:
    summary_frame = _read(root, "outputs/pilot_summary.csv")
    if not {"Unnamed: 0", "value"}.issubset(summary_frame.columns):
        raise ValueError("outputs/pilot_summary.csv must contain index labels and value")
    summary = summary_frame.set_index("Unnamed: 0")["value"]
    metrics = _read(
        root,
        "data/processed/pilot_metrics.csv",
        (
            "cell_id", "NAI", "SMCI_A", "SMCI_B", "Delta_SMCI",
            "SMCI_product_A", "SMCI_product_B", "Delta_SMCI_product",
            "typology_A", "typology_B",
        ),
    )
    if metrics["cell_id"].duplicated().any():
        raise ValueError("pilot_metrics.csv contains duplicate cell_id")

    n_cells = len(metrics)
    if int(summary["n_cells"]) != n_cells:
        raise ValueError("pilot_summary n_cells disagrees with pilot_metrics")
    delta = metrics["Delta_SMCI"]
    _assert_close(summary["mean_SMCI_A"], metrics["SMCI_A"].mean(), "mean_SMCI_A")
    _assert_close(summary["mean_SMCI_B"], metrics["SMCI_B"].mean(), "mean_SMCI_B")
    _assert_close(summary["mean_Delta_SMCI"], delta.mean(), "mean_Delta_SMCI")
    _assert_close(summary["share_improved"], (delta > 0).mean(), "share_improved")
    typology_a = _counts(metrics["typology_A"])
    typology_b = _counts(metrics["typology_B"])
    transition = pd.crosstab(metrics["typology_A"], metrics["typology_B"])

    vif_primary_frame = _read(root, "outputs/validation/vif_flags.csv", ("variable", "VIF"))
    vif_primary = {
        str(row.variable): _finite(row.VIF, f"vif.primary.{row.variable}")
        for row in vif_primary_frame.itertuples()
    }
    variants = _read(
        root,
        "outputs/validation/metric_variant_audit.csv",
        ("variant", "VIF_NAI", "VIF_MAI", "VIF_RAC", "kappa_vs_current", "spearman_SMCI_vs_current", "cells_relabelled"),
    )
    legacy_rows = variants.loc[variants["variant"] == "legacy_full_rac"]
    if len(legacy_rows) != 1:
        raise ValueError("metric_variant_audit.csv must contain one legacy_full_rac row")
    legacy = legacy_rows.iloc[0]

    worldpop = _read(root, "data/interim/grid_worldpop.csv", ("cell_id", "pop_sum"))
    if worldpop["cell_id"].duplicated().any():
        raise ValueError("grid_worldpop.csv contains duplicate cell_id")
    weighted = metrics.merge(worldpop[["cell_id", "pop_sum"]], on="cell_id", how="left", validate="one_to_one")
    if weighted["pop_sum"].isna().any() or (weighted["pop_sum"] < 0).any():
        raise ValueError("WorldPop weights must exist and be non-negative for every cell")
    total_population = _finite(weighted["pop_sum"].sum(), "population.total")
    if total_population <= 0:
        raise ValueError("population.total must be positive")
    weights = weighted["pop_sum"] / total_population
    population_typology = {
        label: _finite(weights[weighted["typology_B"] == label].sum(), f"population.typology_B.{label}")
        for label in typology_b
    }
    if not math.isclose(sum(population_typology.values()), 1.0, abs_tol=1e-9):
        raise ValueError("Population typology shares do not sum to one")

    exposure = _read(
        root,
        "outputs/validation/built_population_zero_access.csv",
        ("cell_id", "pop_sum", "built_class", "zero_nai", "zero_access_built"),
    )
    if exposure["cell_id"].duplicated().any() or set(exposure["cell_id"]) != set(metrics["cell_id"]):
        raise ValueError("built_population_zero_access cell IDs disagree with pilot_metrics")
    zero_built = exposure["zero_access_built"].astype(bool)

    motorcycle = _read(
        root,
        "outputs/validation/manual_motorcycle_validation_template.csv",
        ("model_motorcycle_minutes", "google_maps_android_minutes"),
    )
    valid_motorcycle = motorcycle.loc[
        motorcycle["google_maps_android_minutes"].notna()
        & (motorcycle["google_maps_android_minutes"] > 0)
    ].copy()
    if valid_motorcycle.empty:
        raise ValueError("No completed motorcycle validation records")
    errors = valid_motorcycle["model_motorcycle_minutes"] - valid_motorcycle["google_maps_android_minutes"]

    sensitivities = {
        name: _records(_read(root, path, required), f"sensitivities.{name}")
        for name, (path, required) in SENSITIVITY_INPUTS.items()
    }

    source_audit = _read(
        root,
        "data/interim/poi_observed_audit.csv",
        ("poi_id", "obs_source_tier", "obs_confidence", "include_in_mai"),
    )
    included = source_audit.loc[
        source_audit["include_in_mai"].astype(str).str.lower().eq("true")
    ]
    if included.empty:
        raise ValueError("poi_observed_audit contains no included MAI records")
    if included[["obs_source_tier", "obs_confidence"]].isna().any().any():
        raise ValueError("Included MAI records require source tier and confidence")

    poi = _read(root, "outputs/poi_audit.csv", ("nai_category", "count", "empty_category_flag"))
    poi_counts = {str(row.nai_category): int(row.count) for row in poi.itertuples()}

    snapshot = {
        "schema_version": SCHEMA_VERSION,
        "n_cells": n_cells,
        "smci": {
            "operator": "equal_weight_geometric_mean",
            "legacy_operator": "product",
            "mean_A": _finite(metrics["SMCI_A"].mean(), "smci.mean_A"),
            "mean_B": _finite(metrics["SMCI_B"].mean(), "smci.mean_B"),
            "mean_delta": _finite(delta.mean(), "smci.mean_delta"),
            "positive_median_A": _finite(metrics.loc[metrics["SMCI_A"] > 0, "SMCI_A"].median(), "smci.positive_median_A"),
            "positive_median_B": _finite(metrics.loc[metrics["SMCI_B"] > 0, "SMCI_B"].median(), "smci.positive_median_B"),
        },
        "smci_legacy_product": {
            "mean_A": _finite(metrics["SMCI_product_A"].mean(), "smci_product.mean_A"),
            "mean_B": _finite(metrics["SMCI_product_B"].mean(), "smci_product.mean_B"),
            "mean_delta": _finite(metrics["Delta_SMCI_product"].mean(), "smci_product.mean_delta"),
        },
        "delta_groups": {
            "improved": int((delta > 0).sum()),
            "unchanged": int((delta == 0).sum()),
            "declined": int((delta < 0).sum()),
        },
        "typology_A": typology_a,
        "typology_B": typology_b,
        "typology_transition": {
            "changed": int((metrics["typology_A"] != metrics["typology_B"]).sum()),
            "matrix": {
                str(source): {str(target): int(value) for target, value in row.items()}
                for source, row in transition.iterrows()
            },
        },
        "zero_access": {
            "zero_nai_cells": int((metrics["NAI"] == 0).sum()),
            "built_zero_nai_cells": int(zero_built.sum()),
            "population_exposed": _finite(exposure.loc[zero_built, "pop_sum"].sum(), "zero_access.population_exposed"),
            "population_exposed_share": _finite(exposure.loc[zero_built, "pop_sum"].sum() / exposure["pop_sum"].sum(), "zero_access.population_exposed_share"),
        },
        "population_weighted": {
            "total_population": total_population,
            "mean_SMCI_A": _finite((weighted["SMCI_A"] * weights).sum(), "population_weighted.mean_SMCI_A"),
            "mean_SMCI_B": _finite((weighted["SMCI_B"] * weights).sum(), "population_weighted.mean_SMCI_B"),
            "mean_Delta_SMCI": _finite((weighted["Delta_SMCI"] * weights).sum(), "population_weighted.mean_Delta_SMCI"),
            "share_improved": _finite(weights[weighted["Delta_SMCI"] > 0].sum(), "population_weighted.share_improved"),
            "typology_B_share": population_typology,
        },
        "vif": {
            "primary": vif_primary,
            "legacy_full_rac": {
                "NAI": _finite(legacy["VIF_NAI"], "vif.legacy.NAI"),
                "MAI": _finite(legacy["VIF_MAI"], "vif.legacy.MAI"),
                "RAC": _finite(legacy["VIF_RAC"], "vif.legacy.RAC"),
            },
        },
        "full_rac_agreement": {
            "kappa": _finite(legacy["kappa_vs_current"], "full_rac_agreement.kappa"),
            "spearman_rho": _finite(legacy["spearman_SMCI_vs_current"], "full_rac_agreement.spearman_rho"),
            "cells_relabelled": int(legacy["cells_relabelled"]),
        },
        "motorcycle_validation": {
            "n": len(valid_motorcycle),
            "mae_minutes": _finite(errors.abs().mean(), "motorcycle_validation.mae"),
            "mbe_minutes": _finite(errors.mean(), "motorcycle_validation.mbe"),
            "rmse_minutes": _finite(np.sqrt((errors ** 2).mean()), "motorcycle_validation.rmse"),
        },
        "poi_coverage": {
            "counts_by_nai_category": poi_counts,
            "total": sum(poi_counts.values()),
            "empty_categories": sorted(str(row.nai_category) for row in poi.itertuples() if bool(row.empty_category_flag)),
        },
        "source_tier_coverage": {
            "included_mai_records": len(included),
            "counts_by_tier": _counts(included["obs_source_tier"]),
            "counts_by_confidence": _counts(included["obs_confidence"]),
        },
        "sensitivities": sensitivities,
        "source_files": sorted([
            "outputs/pilot_summary.csv",
            "data/processed/pilot_metrics.csv",
            "data/interim/grid_worldpop.csv",
            "outputs/validation/vif_flags.csv",
            "outputs/validation/metric_variant_audit.csv",
            "outputs/validation/built_population_zero_access.csv",
            "outputs/validation/manual_motorcycle_validation_template.csv",
            "outputs/poi_audit.csv",
            "data/interim/poi_observed_audit.csv",
            *(path for path, _ in SENSITIVITY_INPUTS.values()),
        ]),
    }
    if sum(snapshot["delta_groups"].values()) != n_cells:
        raise ValueError("Delta group counts do not sum to n_cells")
    if sum(typology_a.values()) != n_cells or sum(typology_b.values()) != n_cells:
        raise ValueError("Typology counts do not sum to n_cells")
    return snapshot
