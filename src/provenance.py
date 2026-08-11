"""Deterministic research-pipeline provenance and lineage utilities."""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import subprocess
import tempfile
import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 2


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_path(path: Path) -> str:
    """Hash a file or directory deterministically without loading it into memory."""
    digest = hashlib.sha256()
    if path.is_dir():
        for child in sorted(p for p in path.rglob("*") if p.is_file()):
            digest.update(child.relative_to(path).as_posix().encode("utf-8"))
            digest.update(bytes.fromhex(sha256_path(child)))
        return digest.hexdigest()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def artifact_record(path: Path, role: str) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing {role}: {path}")
    return {"path": path.as_posix(), "role": role, "sha256": sha256_path(path),
            "size_bytes": path.stat().st_size if path.is_file() else None}


def git_state(root: Path) -> dict[str, Any]:
    def run(*args: str) -> str:
        result = subprocess.run(["git", *args], cwd=root, text=True,
                                capture_output=True, check=False)
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    return {"commit": run("rev-parse", "HEAD"),
            "dirty": bool(run("status", "--porcelain"))}


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


def _safe_relative(value: str) -> bool:
    path = Path(value)
    return bool(value) and not path.is_absolute() and ".." not in path.parts


def load_pipeline(path: Path) -> dict[str, Any]:
    pipeline = json.loads(path.read_text(encoding="utf-8-sig"))
    if pipeline.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"Unsupported pipeline schema: {pipeline.get('schema_version')}")
    nodes = pipeline.get("nodes")
    if not isinstance(nodes, dict) or not nodes:
        raise ValueError("Pipeline must contain a non-empty nodes object")
    allowed = {"objective", "command", "depends_on", "inputs", "outputs", "decisions", "evaluations", "resources", "tags", "artifact_contract"}
    producers: dict[str, str] = {}
    for name, node in nodes.items():
        unknown = set(node) - allowed
        if unknown:
            raise ValueError(f"{name} has unknown fields: {sorted(unknown)}")
        if not node.get("objective") or not isinstance(node.get("command"), list):
            raise ValueError(f"{name} requires objective and command")
        for value in (*node.get("inputs", []), *node.get("outputs", [])):
            if not _safe_relative(value):
                raise ValueError(f"Unsafe pipeline path: {value}")
        for output in node.get("outputs", []):
            if output in producers:
                raise ValueError(f"Duplicate output producer: {output}")
            producers[output] = name
    topological_order(nodes)
    return pipeline


def graph_edges(nodes: dict[str, Any]) -> list[dict[str, str]]:
    producers = {path: name for name, node in nodes.items() for path in node.get("outputs", [])}
    edges: list[dict[str, str]] = []
    for name, node in nodes.items():
        edges += [{"source": dep, "target": name, "type": "DEPENDS_ON"} for dep in node.get("depends_on", [])]
        edges += [{"source": name, "target": path, "type": "PRODUCED"} for path in node.get("outputs", [])]
        edges += [{"source": producers[path], "target": name, "type": "DERIVED_FROM"} for path in node.get("inputs", []) if path in producers]
        edges += [{"source": name, "target": decision, "type": "GOVERNED_BY"} for decision in node.get("decisions", [])]
        edges += [{"source": name, "target": evaluator, "type": "EVALUATED_BY"} for evaluator in node.get("evaluations", [])]
    return edges


def validate_artifact_contract(node: dict[str, Any], root: Path) -> list[str]:
    errors = []
    contracts = node.get("artifact_contract", {})
    for output in node.get("outputs", []):
        path = root / output
        contract = contracts.get(output, {})
        if not path.exists(): errors.append(f"missing output: {output}")
        elif contract.get("non_empty", True) and path.is_file() and path.stat().st_size == 0: errors.append(f"empty output: {output}")
        elif contract.get("suffix") and path.suffix != contract["suffix"]: errors.append(f"wrong suffix: {output}")
    return errors


def topological_order(nodes: dict[str, Any]) -> list[str]:
    order: list[str] = []
    state: dict[str, int] = {}
    def visit(name: str) -> None:
        if name not in nodes:
            raise ValueError(f"Unknown pipeline dependency: {name}")
        if state.get(name) == 1:
            raise ValueError(f"Pipeline cycle detected at: {name}")
        if state.get(name) == 2:
            return
        state[name] = 1
        for dependency in nodes[name].get("depends_on", []):
            visit(dependency)
        state[name] = 2
        order.append(name)
    for node_name in nodes:
        visit(node_name)
    return order


def select_nodes(nodes: dict[str, Any], *, node: str | None = None,
                 start: str | None = None, end: str | None = None) -> list[str]:
    order = topological_order(nodes)
    for value in (node, start, end):
        if value is not None and value not in nodes:
            raise ValueError(f"Unknown pipeline node: {value}")
    if node:
        required: set[str] = set()
        def include(name: str) -> None:
            for dependency in nodes[name].get("depends_on", []):
                include(dependency)
            required.add(name)
        include(node)
        return [name for name in order if name in required]
    first = order.index(start) if start else 0
    last = order.index(end) + 1 if end else len(order)
    if first >= last:
        raise ValueError("--from must precede --to")
    return order[first:last]


def is_fresh(node: dict[str, Any], root: Path,
             manifest_dir: Path | None = None, node_id: str | None = None) -> bool:
    inputs = [root / value for value in node.get("inputs", [])]
    outputs = [root / value for value in node.get("outputs", [])]
    paths = inputs + outputs
    if not outputs or any(not path.exists() for path in paths):
        return False
    if manifest_dir is not None and node_id is not None:
        for manifest_path in sorted(manifest_dir.glob("*.json"), reverse=True):
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            prior = next((item for item in manifest.get("nodes", [])
                          if item["node_id"] == node_id
                          and item["status"] in {"succeeded", "skipped_fresh"}), None)
            if prior is None:
                continue
            hashes = {item["path"]: item["sha256"] for item in prior.get("artifacts", [])}
            return all(hashes.get(path.as_posix()) == sha256_path(path) for path in paths)
        return False
    newest_input = max((path.stat().st_mtime_ns for path in inputs), default=0)
    oldest_output = min(path.stat().st_mtime_ns for path in outputs)
    return oldest_output >= newest_input


def new_manifest(run_id: str, pipeline_path: Path, root: Path) -> dict[str, Any]:
    return {"schema_version": SCHEMA_VERSION, "run_id": run_id,
            "pipeline": pipeline_path.as_posix(), "pipeline_sha256": sha256_path(pipeline_path),
            "started_at": utc_now(), "finished_at": None, "status": "running",
            "git": git_state(root), "environment": {"python": platform.python_version(),
            "platform": platform.platform()}, "nodes": []}


def rebuild_sqlite(manifest_dir: Path, database: Path) -> None:
    """Rebuild the disposable query index from immutable JSON manifests."""
    database.parent.mkdir(parents=True, exist_ok=True)
    temporary = database.with_suffix(database.suffix + ".tmp")
    temporary.unlink(missing_ok=True)
    connection = sqlite3.connect(temporary)
    try:
        connection.executescript("""
            CREATE TABLE runs (run_id TEXT PRIMARY KEY, status TEXT, started_at TEXT,
                finished_at TEXT, git_commit TEXT, git_dirty INTEGER);
            CREATE TABLE nodes (run_id TEXT, node_id TEXT, status TEXT, command TEXT,
                started_at TEXT, finished_at TEXT, exit_code INTEGER,
                PRIMARY KEY (run_id, node_id));
            CREATE TABLE dependencies (run_id TEXT, node_id TEXT, dependency TEXT);
            CREATE TABLE decisions (run_id TEXT, node_id TEXT, decision_id TEXT);
            CREATE TABLE artifacts (run_id TEXT, node_id TEXT, path TEXT, role TEXT,
                sha256 TEXT, size_bytes INTEGER);
        """)
        for path in sorted(manifest_dir.glob("*.json")):
            manifest = json.loads(path.read_text(encoding="utf-8"))
            git = manifest.get("git", {})
            connection.execute("INSERT INTO runs VALUES (?, ?, ?, ?, ?, ?)",
                (manifest["run_id"], manifest["status"], manifest["started_at"],
                 manifest.get("finished_at"), git.get("commit"), int(bool(git.get("dirty")))))
            for node in manifest.get("nodes", []):
                values = (manifest["run_id"], node["node_id"])
                connection.execute("INSERT INTO nodes VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (*values, node["status"], json.dumps(node["command"]),
                     node["started_at"], node.get("finished_at"), node.get("exit_code")))
                connection.executemany("INSERT INTO dependencies VALUES (?, ?, ?)",
                    [(*values, item) for item in node.get("depends_on", [])])
                connection.executemany("INSERT INTO decisions VALUES (?, ?, ?)",
                    [(*values, item) for item in node.get("decisions", [])])
                connection.executemany("INSERT INTO artifacts VALUES (?, ?, ?, ?, ?, ?)",
                    [(*values, item["path"], item["role"], item["sha256"], item["size_bytes"])
                     for item in node.get("artifacts", [])])
        connection.commit()
    finally:
        connection.close()
    os.replace(temporary, database)
