import math
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from headline_metrics import SCHEMA_VERSION, build_headline_metrics, load_headline_metrics


def _write_fixture(root: Path) -> None:
    (root / "outputs/validation").mkdir(parents=True)
    (root / "data/processed").mkdir(parents=True)
    (root / "data/interim").mkdir(parents=True)
    pd.Series({
        "n_cells": 4, "mean_SMCI_A": .15, "mean_SMCI_B": .25,
        "mean_Delta_SMCI": .1, "share_improved": .75,
    }, name="value").to_csv(root / "outputs/pilot_summary.csv")
    metrics = pd.DataFrame({
        "cell_id": [0, 1, 2, 3], "NAI": [0, 1, 2, 3],
        "SMCI_A": [0, .1, .2, .3], "SMCI_B": [0, .2, .3, .5],
        "Delta_SMCI": [0, .1, .1, .2],
        "typology_A": ["A", "A", "B", "B"],
        "typology_B": ["A", "B", "B", "B"],
    })
    metrics["SMCI_product_A"] = metrics["SMCI_A"] ** 3
    metrics["SMCI_product_B"] = metrics["SMCI_B"] ** 3
    metrics["Delta_SMCI_product"] = metrics["SMCI_product_B"] - metrics["SMCI_product_A"]
    metrics.to_csv(root / "data/processed/pilot_metrics.csv", index=False)
    pd.DataFrame({"cell_id": [0, 1, 2, 3], "pop_sum": [1., 1., 2., 4.]}).to_csv(
        root / "data/interim/grid_worldpop.csv", index=False)
    pd.DataFrame({"variable": ["NAI", "MAI", "RAC"], "VIF": [1., 2., 3.]}).to_csv(
        root / "outputs/validation/vif_flags.csv", index=False)
    pd.DataFrame({
        "variant": ["legacy_full_rac"], "VIF_NAI": [3.], "VIF_MAI": [9.], "VIF_RAC": [10.],
        "kappa_vs_current": [.9], "spearman_SMCI_vs_current": [.98], "cells_relabelled": [1],
    }).to_csv(root / "outputs/validation/metric_variant_audit.csv", index=False)
    exposure = metrics[["cell_id"]].assign(
        pop_sum=[1., 1., 2., 4.], built_class=["built"] * 4,
        zero_nai=[True, False, False, False], zero_access_built=[True, False, False, False],
    )
    exposure.to_csv(root / "outputs/validation/built_population_zero_access.csv", index=False)
    pd.DataFrame({
        "model_motorcycle_minutes": [5., 8.], "google_maps_android_minutes": [6., 10.],
    }).to_csv(root / "outputs/validation/manual_motorcycle_validation_template.csv", index=False)
    pd.DataFrame({
        "nai_category": ["park", "school"], "count": [2, 3],
        "empty_category_flag": [False, False],
    }).to_csv(root / "outputs/poi_audit.csv", index=False)
    pd.DataFrame({
        "poi_id": [10, 11, 12],
        "obs_source_tier": ["official_source", "manual_checked", "excluded"],
        "obs_confidence": ["high", "low", "low"],
        "include_in_mai": [True, True, False],
    }).to_csv(root / "data/interim/poi_observed_audit.csv", index=False)
    sensitivity_files = {
        "motorcycle_speed_sensitivity.csv": {
            "scenario": ["baseline"], "mean_SMCI_B": [.2],
            "typology_kappa_vs_baseline": [1.], "cells_relabelled_vs_baseline": [0],
        },
        "transit_impedance_sensitivity.csv": {
            "scenario": ["baseline"], "mean_SMCI_B": [.2],
            "typology_kappa_vs_baseline": [1.], "cells_relabelled_vs_baseline": [0],
        },
        "nai_threshold_sensitivity.csv": {
            "threshold_m": [800.], "n_cells": [4], "mean_SMCI_B": [.2],
            "typology_kappa_vs_reference": [1.],
        },
        "observed_vs_proxy_sensitivity.csv": {
            "metric": ["kappa"], "proxy": [.9], "observed": [1.], "observed_strict": [1.],
        },
        "rac_scaling_kappa.csv": {"comparison": ["a vs b"], "cohens_kappa": [.9]},
        "rac_scaling_spearman.csv": {"comparison": ["a vs b"], "spearman_rho_smci": [.9]},
        "rac_scaling_typology_shift.csv": {
            "from_minmax": ["A"], "to_log_minmax": ["B"], "n_cells": [1],
        },
    }
    for filename, values in sensitivity_files.items():
        pd.DataFrame(values).to_csv(root / "outputs/validation" / filename, index=False)


def test_headline_snapshot_invariants(tmp_path):
    _write_fixture(tmp_path)
    snapshot = build_headline_metrics(tmp_path)
    assert snapshot["schema_version"] == SCHEMA_VERSION
    assert snapshot["delta_groups"] == {"improved": 3, "unchanged": 1, "declined": 0}
    assert snapshot["typology_A"] == {"A": 2, "B": 2}
    assert snapshot["typology_B"] == {"A": 1, "B": 3}
    assert snapshot["typology_transition"]["changed"] == 1
    assert math.isclose(sum(snapshot["population_weighted"]["typology_B_share"].values()), 1.)
    assert snapshot["full_rac_agreement"] == {
        "kappa": .9, "spearman_rho": .98, "cells_relabelled": 1,
    }
    assert snapshot["motorcycle_validation"]["n"] == 2
    assert math.isclose(snapshot["motorcycle_validation"]["mae_minutes"], 1.5)
    assert snapshot["source_tier_coverage"] == {
        "included_mai_records": 2,
        "counts_by_tier": {"manual_checked": 1, "official_source": 1},
        "counts_by_confidence": {"high": 1, "low": 1},
    }


def test_headline_snapshot_requires_sensitivity_output(tmp_path):
    _write_fixture(tmp_path)
    (tmp_path / "outputs/validation/rac_scaling_kappa.csv").unlink()
    with pytest.raises(FileNotFoundError, match="rac_scaling_kappa"):
        build_headline_metrics(tmp_path)


def test_headline_snapshot_rejects_non_finite_sensitivity(tmp_path):
    _write_fixture(tmp_path)
    pd.DataFrame({"scenario": ["baseline"], "kappa": [float("nan")]}).to_csv(
        tmp_path / "outputs/validation/motorcycle_speed_sensitivity.csv", index=False)
    with pytest.raises(ValueError, match="missing columns"):
        build_headline_metrics(tmp_path)


def test_headline_snapshot_rejects_wrong_sensitivity_schema(tmp_path):
    _write_fixture(tmp_path)
    pd.DataFrame({"scenario": ["baseline"], "mean_SMCI_B": [.2]}).to_csv(
        tmp_path / "outputs/validation/transit_impedance_sensitivity.csv", index=False)
    with pytest.raises(ValueError, match="transit_impedance_sensitivity.csv missing columns"):
        build_headline_metrics(tmp_path)


def test_headline_snapshot_float_tolerance(tmp_path):
    _write_fixture(tmp_path)
    summary_path = tmp_path / "outputs/pilot_summary.csv"
    summary = pd.read_csv(summary_path, index_col=0)
    summary.loc["mean_SMCI_B", "value"] += 5e-13
    summary.to_csv(summary_path)
    build_headline_metrics(tmp_path)
    summary.loc["mean_SMCI_B", "value"] += 2e-12
    summary.to_csv(summary_path)
    with pytest.raises(ValueError, match="mean_SMCI_B disagrees"):
        build_headline_metrics(tmp_path)


def test_load_headline_metrics_rejects_stale_schema(tmp_path):
    path = tmp_path / "headline.json"
    path.write_text('{"schema_version": 1}', encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported headline schema"):
        load_headline_metrics(path)
