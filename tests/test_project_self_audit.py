import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.project_self_audit import data_requirement_status


def test_data_requirement_status_reads_explicit_contract_status(tmp_path):
    status = tmp_path / "status.md"
    status.write_text("# Status\n\nStatus: `NOT_RUN_DATA_REQUIRED`\n", encoding="utf-8")
    assert data_requirement_status(status) == "NOT_RUN_DATA_REQUIRED"


def test_data_requirement_status_rejects_missing_or_unmarked_file(tmp_path):
    assert data_requirement_status(tmp_path / "missing.md") is None
    status = tmp_path / "status.md"
    status.write_text("No status marker", encoding="utf-8")
    assert data_requirement_status(status) is None
