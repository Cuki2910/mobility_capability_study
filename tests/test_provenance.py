import json
import os
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from provenance import (artifact_record, is_fresh, rebuild_sqlite, select_nodes,
                        sha256_path, topological_order, write_json_atomic)


def test_hash_and_atomic_json(tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("research", encoding="utf-8")
    assert sha256_path(source) == artifact_record(source, "input")["sha256"]
    target = tmp_path / "manifest.json"
    write_json_atomic(target, {"ok": True})
    assert json.loads(target.read_text()) == {"ok": True}


def test_dag_order_selection_and_cycle():
    nodes = {"a": {}, "b": {"depends_on": ["a"]}, "c": {"depends_on": ["b"]}}
    assert topological_order(nodes) == ["a", "b", "c"]
    assert select_nodes(nodes, node="c") == ["a", "b", "c"]
    with pytest.raises(ValueError, match="cycle"):
        topological_order({"a": {"depends_on": ["b"]}, "b": {"depends_on": ["a"]}})


def test_freshness_detects_newer_input(tmp_path):
    source, output = tmp_path / "in", tmp_path / "out"
    source.write_text("1")
    output.write_text("1")
    node = {"inputs": ["in"], "outputs": ["out"]}
    assert is_fresh(node, tmp_path)
    newer = output.stat().st_mtime_ns + 1_000_000_000
    source.touch()
    os.utime(source, ns=(newer, newer))
    assert not is_fresh(node, tmp_path)


def test_sqlite_rebuild(tmp_path):
    manifests = tmp_path / "runs"
    manifests.mkdir()
    payload = {"run_id": "r1", "status": "succeeded", "started_at": "a",
               "finished_at": "b", "git": {"commit": "abc", "dirty": False},
               "nodes": [{"node_id": "n", "status": "succeeded", "command": ["python"],
                          "started_at": "a", "finished_at": "b", "exit_code": 0,
                          "depends_on": [], "decisions": ["DEC-001"], "artifacts": []}]}
    write_json_atomic(manifests / "r1.json", payload)
    database = tmp_path / "lineage.sqlite"
    rebuild_sqlite(manifests, database)
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT status FROM runs").fetchone()[0] == "succeeded"
        assert connection.execute("SELECT decision_id FROM decisions").fetchone()[0] == "DEC-001"
