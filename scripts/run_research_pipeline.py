"""Run the deterministic research DAG and persist artifact lineage."""
from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.provenance import (artifact_record, is_fresh, load_pipeline, new_manifest,
                            rebuild_sqlite, select_nodes, utc_now, write_json_atomic)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pipeline", type=Path, default=Path("config/pipeline.json"))
    parser.add_argument("--node")
    parser.add_argument("--from", dest="start")
    parser.add_argument("--to", dest="end")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    pipeline_path = args.pipeline if args.pipeline.is_absolute() else ROOT / args.pipeline
    pipeline = load_pipeline(pipeline_path)
    selected = select_nodes(pipeline["nodes"], node=args.node, start=args.start, end=args.end)
    if args.dry_run:
        for name in selected:
            spec = pipeline["nodes"][name]
            print(f"{name}: {' '.join(spec['command'])}")
        return 0

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    manifest_dir = ROOT / "outputs" / "lineage" / "runs"
    manifest_path = manifest_dir / f"{run_id}.json"
    manifest = new_manifest(run_id, args.pipeline, ROOT)
    write_json_atomic(manifest_path, manifest)
    try:
        for name in selected:
            spec = pipeline["nodes"][name]
            record = {"node_id": name, "command": spec["command"],
                      "depends_on": spec.get("depends_on", []),
                      "decisions": spec.get("decisions", []), "started_at": utc_now(),
                      "finished_at": None, "status": "running", "exit_code": None,
                      "artifacts": []}
            manifest["nodes"].append(record)
            write_json_atomic(manifest_path, manifest)
            if not args.force and is_fresh(spec, ROOT, manifest_dir, name):
                record.update(status="skipped_fresh", exit_code=0, finished_at=utc_now())
            else:
                missing = [path for path in spec.get("inputs", []) if not (ROOT / path).exists()]
                if missing:
                    raise FileNotFoundError(f"{name} missing inputs: {missing}")
                result = subprocess.run(spec["command"], cwd=ROOT, check=False)
                record["exit_code"] = result.returncode
                record["finished_at"] = utc_now()
                record["status"] = "succeeded" if result.returncode == 0 else "failed"
                if result.returncode:
                    raise RuntimeError(f"{name} failed with exit code {result.returncode}")
                missing_outputs = [path for path in spec.get("outputs", [])
                                   if not (ROOT / path).exists()]
                if missing_outputs:
                    record["status"] = "failed"
                    record["exit_code"] = 1
                    raise FileNotFoundError(f"{name} missing outputs: {missing_outputs}")
            record["artifacts"] = [artifact_record(ROOT / path, "input")
                                   for path in spec.get("inputs", [])]
            record["artifacts"] += [artifact_record(ROOT / path, "output")
                                    for path in spec.get("outputs", [])]
            write_json_atomic(manifest_path, manifest)
        manifest["status"] = "succeeded"
        return_code = 0
    except Exception as error:
        if manifest["nodes"] and manifest["nodes"][-1]["status"] == "running":
            manifest["nodes"][-1].update(status="failed", finished_at=utc_now())
        manifest["status"] = "failed"
        manifest["error"] = f"{type(error).__name__}: {error}"
        print(manifest["error"], file=sys.stderr)
        return_code = 1
    finally:
        manifest["finished_at"] = utc_now()
        write_json_atomic(manifest_path, manifest)
        rebuild_sqlite(manifest_dir, ROOT / "outputs" / "lineage" / "research_lineage.sqlite")
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
