"""Fail when marked publication claims disagree with the canonical snapshot."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.headline_metrics import load_headline_metrics

MARKER = re.compile(
    r"<!--\s*headline:(?P<path>/[^|]+)\|(?P<format>[^\s]+)\s*-->"
    r"(?P<actual>.*?)<!--\s*/headline\s*-->", re.DOTALL,
)
DEFAULT_DOCUMENTS = (Path("proposal/proposal_v7.md"), Path("paper/paper_draft.md"), Path("outputs/supervisor_memo.md"))
REQUIRED_PATHS = {
    Path("proposal/proposal_v7.md"): {"/n_cells", "/typology_B/Motorcycle Lock-in", "/typology_B/Fragmented Capability", "/full_rac_agreement/kappa", "/full_rac_agreement/cells_relabelled"},
    Path("paper/paper_draft.md"): {"/n_cells", "/delta_groups/improved", "/typology_B/Motorcycle Lock-in", "/full_rac_agreement/kappa", "/full_rac_agreement/cells_relabelled"},
    Path("outputs/supervisor_memo.md"): {"/n_cells", "/smci/mean_A", "/smci/mean_B", "/delta_groups/improved"},
}


def _resolve(snapshot: dict[str, Any], pointer: str) -> Any:
    value: Any = snapshot
    for part in pointer.lstrip("/").split("/"):
        if not isinstance(value, dict) or part not in value:
            raise KeyError(f"Unknown headline pointer: {pointer}")
        value = value[part]
    return value


def _render(value: Any, spec: str) -> str:
    if spec == "int": return str(int(value))
    if spec == "percent1": return f"{float(value):.1%}"
    return format(value, spec)


def check_document(path: Path, snapshot: dict[str, Any], required: set[str] | None = None) -> list[str]:
    if not path.exists(): return [f"{path}: missing document"]
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    seen: set[str] = set()
    for match in MARKER.finditer(text):
        pointer = match.group("path").strip()
        seen.add(pointer)
        line = text.count("\n", 0, match.start()) + 1
        try: expected = _render(_resolve(snapshot, pointer), match.group("format"))
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"{path}:{line}: {exc}")
            continue
        actual = match.group("actual").strip()
        if actual != expected: errors.append(f"{path}:{line}: {pointer} expected {expected!r}, actual {actual!r}")
    errors.extend(f"{path}: missing required marker {pointer}" for pointer in sorted((required or set()) - seen))
    return errors


def check_documents(snapshot_path: Path, documents: list[Path]) -> list[str]:
    snapshot = load_headline_metrics(snapshot_path)
    return [error for path in documents for error in check_document(path, snapshot, REQUIRED_PATHS.get(path, set()))]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, default=Path("outputs/headline_metrics.json"))
    parser.add_argument("documents", nargs="*", type=Path, default=list(DEFAULT_DOCUMENTS))
    args = parser.parse_args()
    errors = check_documents(args.snapshot, args.documents)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Document consistency PASS: {len(args.documents)} documents")
    return 0


if __name__ == "__main__": raise SystemExit(main())
