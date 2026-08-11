"""Validate optional local agent file ownership against the current diff."""
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.agent_gate import ROOT, changed_files, default_base, load_policy, normalize_paths

def owns(path: str, reservations: tuple[str, ...]) -> bool:
    return any(path == item or path.startswith(item.rstrip("/") + "/") for item in reservations)
def validate(record: dict, changed: tuple[str, ...], branch: str) -> list[str]:
    required = {"task", "branch", "owner", "paths", "canonical_outputs"}
    if set(record) != required: return [f"Ownership fields must be exactly {sorted(required)}"]
    try: paths = normalize_paths(record["paths"])
    except (TypeError, ValueError) as exc: return [str(exc)]
    errors = []
    if record["branch"] != branch: errors.append(f"Reserved branch {record['branch']!r} does not match {branch!r}")
    allowed_meta = {".agent/ownership.json"}
    outside = [path for path in changed if path not in allowed_meta and not owns(path, paths)]
    if outside: errors.append("Changed files outside ownership: " + ", ".join(outside))
    return errors
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--file", type=Path, default=Path(".agent/ownership.json")); parser.add_argument("--base"); args = parser.parse_args()
    if not args.file.exists(): print("Ownership check skipped: no .agent/ownership.json"); return 0
    try:
        policy = load_policy(); base = args.base or default_base(policy)
        record = json.loads(args.file.read_text(encoding="utf-8-sig"))
        branch = subprocess.run(("git", "branch", "--show-current"), cwd=ROOT, text=True, capture_output=True, check=True).stdout.strip()
        errors = validate(record, changed_files(base), branch)
    except (OSError, ValueError, json.JSONDecodeError, subprocess.CalledProcessError) as exc: print(f"ownership: {exc}", file=sys.stderr); return 2
    if errors: print("\n".join(errors), file=sys.stderr); return 1
    print(f"Ownership PASS: {record['task']} ({len(record['paths'])} paths)"); return 0
if __name__ == "__main__": raise SystemExit(main())
