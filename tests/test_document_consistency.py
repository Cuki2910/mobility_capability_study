import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_document_consistency import check_document


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
