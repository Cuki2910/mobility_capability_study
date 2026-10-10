import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_document_consistency import check_document, check_semantic_consistency


def test_stale_marked_claim_fails(tmp_path):
    path = tmp_path / "paper.md"
    path.write_text("Value: <!-- headline:/n_cells|int -->461<!-- /headline -->\n", encoding="utf-8")
    errors = check_document(path, {"n_cells": 462}, {"/n_cells"})
    assert "expected '462', actual '461'" in errors[0]


def test_historical_unmarked_number_ignored(tmp_path):
    path = tmp_path / "paper.md"
    path.write_text("Historical result: 170 cells.\n", encoding="utf-8")
    assert check_document(path, {"n_cells": 462}) == []


def test_missing_required_marker_fails(tmp_path):
    path = tmp_path / "paper.md"
    path.write_text("No canonical claim here.\n", encoding="utf-8")
    assert check_document(path, {"n_cells": 462}, {"/n_cells"}) == [
        f"{path}: missing required marker /n_cells"
    ]


def test_semantic_check_allows_new_method_and_improved_status(tmp_path):
    (tmp_path / "config").mkdir()
    (tmp_path / "config/pipeline.json").write_text(
        json.dumps({"analytical_spec": {"smci_primary_operator": "additive", "nai_primary_threshold_m": 1000}}),
        encoding="utf-8",
    )
    status = tmp_path / "outputs/west_taymo/readiness_status.md"
    status.parent.mkdir(parents=True)
    status.write_text("Status: `READY`\n")
    assert check_semantic_consistency(tmp_path, []) == []


def test_method_transition_allows_historical_snapshot_pending_review(tmp_path):
    (tmp_path / "config").mkdir()
    (tmp_path / "outputs").mkdir()
    (tmp_path / "config/pipeline.json").write_text(json.dumps({"analytical_spec": {"smci_primary_operator": "additive"}}))
    from src.headline_metrics import SCHEMA_VERSION
    (tmp_path / "outputs/headline_metrics.json").write_text(json.dumps({"schema_version": SCHEMA_VERSION, "smci": {"operator": "product"}}))
    assert check_semantic_consistency(tmp_path, []) == []
