"""Verify and record the reproducible baseline before publication analysis."""
from __future__ import annotations

import argparse
import importlib.metadata
import json
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.provenance import git_state, sha256_path

CANONICAL_INPUTS = (
    "config/pipeline.json",
    "data/interim/pilot_accessibility_inputs.csv",
    "data/interim/grid_worldpop.csv",
    "data/processed/pilot_metrics.csv",
    "outputs/pilot_summary.csv",
    "outputs/headline_metrics.json",
)
PUBLICATION_OUTPUTS = (
    "outputs/headline_metrics.json",
    "outputs/project_self_audit.md",
    "outputs/supervisor_memo.md",
    "paper/paper_draft.md",
    "proposal/proposal_v7.md",
)
PACKAGES = ("geopandas", "networkx", "numpy", "osmnx", "pandas", "pytest",
            "rasterio", "scikit-learn", "scipy", "shapely", "statsmodels")


def run_tests(root: Path) -> tuple[int, str]:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests", "-q"], cwd=root,
        text=True, capture_output=True, check=False,
    )
    output = "\n".join(part.strip() for part in (result.stdout, result.stderr) if part.strip())
    summary = next((line for line in reversed(output.splitlines()) if " passed" in line), output[-500:])
    return result.returncode, summary


def build_report(root: Path, *, run_pytest: bool = True) -> tuple[str, bool]:
    missing_inputs = [path for path in CANONICAL_INPUTS if not (root / path).exists()]
    inputs = {path: sha256_path(root / path) for path in CANONICAL_INPUTS if (root / path).exists()}
    outputs = {path: ("present" if (root / path).exists() else "missing")
               for path in PUBLICATION_OUTPUTS}
    test_code, test_summary = run_tests(root) if run_pytest else (0, "not run (--skip-tests)")
    headline = root / "outputs/headline_metrics.json"
    headline_schema = None
    if headline.exists():
        headline_schema = json.loads(headline.read_text(encoding="utf-8")).get("schema_version")
    packages = {}
    for package in PACKAGES:
        try:
            packages[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            packages[package] = "missing"
    passed = not missing_inputs and test_code == 0 and headline_schema == 2
    git = git_state(root)
    lines = [
        "# Baseline Integrity", "",
        f"- Gate: **{'PASS' if passed else 'FAIL'}**",
        f"- Git commit: `{git['commit']}`",
        f"- Git dirty: `{git['dirty']}`",
        f"- Python: `{platform.python_version()}`",
        f"- Platform: `{platform.platform()}`",
        f"- Tests: `{test_summary}`",
        f"- Headline schema: `{headline_schema}`",
        f"- Headline SHA-256: `{inputs.get('outputs/headline_metrics.json', 'missing')}`",
        "", "## Direct package versions", "",
        *[f"- {name}: `{version}`" for name, version in packages.items()],
        "", "## Canonical input checksums", "",
        *([f"- `{path}`: `{digest}`" for path, digest in inputs.items()] or ["- None"]),
        "", "## Missing canonical inputs", "",
        *([f"- `{path}`" for path in missing_inputs] or ["- None"]),
        "", "## Publication-critical artifact presence", "",
        *[f"- `{path}`: **{status}**" for path, status in outputs.items()],
        "",
        "> Presence is recorded here. Freshness remains enforced by the DAG manifest hashes.",
    ]
    return "\n".join(lines) + "\n", passed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=Path("outputs/validation/baseline_integrity.md"))
    parser.add_argument("--skip-tests", action="store_true")
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    report, passed = build_report(ROOT, run_pytest=not args.skip_tests)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")
    print(f"Wrote {output}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
