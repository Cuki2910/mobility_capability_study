"""Run repository checks selected by the current Git diff and agent policy."""
from __future__ import annotations

import argparse
import json
import hashlib
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "config" / "agent_policy.json"


@dataclass(frozen=True)
class GatePlan:
    changed: tuple[str, ...]
    groups: tuple[str, ...]
    commands: tuple[tuple[str, ...], ...]
    errors: tuple[str, ...]
    warnings: tuple[str, ...]


def normalize_paths(paths: Iterable[str]) -> tuple[str, ...]:
    normalized: set[str] = set()
    for raw in paths:
        path = raw.strip().replace("\\", "/")
        if not path:
            continue
        pure = PurePosixPath(path)
        if pure.is_absolute() or ".." in pure.parts:
            raise ValueError(f"Unsafe repository path: {raw!r}")
        normalized.add(str(pure))
    return tuple(sorted(normalized))


def load_policy(path: Path = POLICY_PATH) -> dict:
    policy = json.loads(path.read_text(encoding="utf-8-sig"))
    required = {"schema_version", "integration_branches", "base_candidates", "canonical_outputs", "groups", "couplings"}
    missing = required - policy.keys()
    if policy.get("schema_version") != 1 or missing:
        raise ValueError(f"Invalid agent policy; missing={sorted(missing)}")
    normalize_paths(policy["canonical_outputs"])
    for name, group in policy["groups"].items():
        if not isinstance(name, str) or set(group) != {"prefixes", "files", "commands"}:
            raise ValueError(f"Invalid group: {name!r}")
        normalize_paths((*group["prefixes"], *group["files"]))
        if not all(isinstance(command, list) and command and all(isinstance(part, str) for part in command) for command in group["commands"]):
            raise ValueError(f"Invalid commands in group: {name}")
    return policy


def _matches(path: str, group: dict) -> bool:
    return path in group["files"] or any(path.startswith(prefix) for prefix in group["prefixes"])


def build_plan(paths: Iterable[str], branch: str = "", policy: dict | None = None, allow_canonical: bool = False, reason: str = "") -> GatePlan:
    policy = policy or load_policy()
    changed = normalize_paths(paths)
    files = set(changed)
    groups = tuple(name for name, group in policy["groups"].items() if any(_matches(path, group) for path in changed))
    commands: list[tuple[str, ...]] = [("git", "diff", "--check")]
    for name in groups:
        for command in policy["groups"][name]["commands"]:
            rendered = tuple(sys.executable if part == "{python}" else part for part in command)
            if rendered not in commands:
                commands.append(rendered)
    errors: list[str] = []
    warnings: list[str] = []
    for coupling in policy["couplings"]:
        if coupling["when"] not in files:
            continue
        missing = [path for path in coupling["require_all"] if path not in files]
        any_ok = not coupling["require_any_prefix"] or any(any(path.startswith(prefix) for prefix in coupling["require_any_prefix"]) for path in changed)
        if missing or not any_ok:
            warnings.append(coupling["message"] + (f"; missing: {', '.join(missing)}" if missing else "") + "; review and request user confirmation")
    canonical = sorted(files & set(policy["canonical_outputs"]))
    if canonical:
        warnings.append(f"Published outputs/status changed: {', '.join(canonical)}; request user confirmation")
    return GatePlan(changed, groups, tuple(commands), tuple(errors), tuple(warnings))


def _git(*args: str, check: bool = True) -> str:
    result = subprocess.run(("git", *args), cwd=ROOT, text=True, errors="replace", capture_output=True, check=False)
    if check and result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip()


def default_base(policy: dict) -> str:
    for ref in policy["base_candidates"]:
        if subprocess.run(("git", "rev-parse", "--verify", "--quiet", ref), cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
            return ref
    raise RuntimeError("No base ref found; pass --base explicitly")


def changed_files(base: str) -> tuple[str, ...]:
    # NUL-delimited Git paths preserve non-ASCII filenames without C-style quoting.
    committed = _git("diff", "--name-only", "-z", f"{base}...HEAD", check=False).split("\0")
    working = _git("diff", "--name-only", "-z", "HEAD", check=False).split("\0")
    untracked = _git("ls-files", "--others", "--exclude-standard", "-z", check=False).split("\0")
    return normalize_paths((*committed, *working, *untracked))


def report(plan: GatePlan, base: str, branch: str) -> dict:
    return {"base": base, "branch": branch, "confirmation": "required" if plan.changed else "not_required", **asdict(plan)}


def write_review(plan: GatePlan, base: str, branch: str, outcome: str, reason: str = "") -> Path:
    """Replace the batch report; a successful check never constitutes user approval."""
    output = ROOT / ".agent/change_review.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    previous = _git("show", f"{base}:config/pipeline.json", check=False)
    before = json.loads(previous.lstrip("\ufeff")).get("analytical_spec", {}) if previous else {}
    current = ROOT / "config/pipeline.json"
    after = json.loads(current.read_text(encoding="utf-8-sig")).get("analytical_spec", {}) if current.exists() else {}
    diff = _git("diff", "--no-ext-diff", "--no-textconv", base, "--", *plan.changed) if plan.changed else ""
    output.with_suffix(".diff").write_text(diff, encoding="utf-8")
    fingerprint = hashlib.sha256(diff.encode())
    for name in plan.changed:
        path = ROOT / name
        fingerprint.update(name.encode())
        if path.is_file(): fingerprint.update(path.read_bytes())
    lines = ["# Change review", "", f"Status: {'PENDING_USER_CONFIRMATION' if plan.changed else 'NO_CHANGES'}", "",
             f"Change ID: `{fingerprint.hexdigest()}`", "",
             f"Git baseline: `{base}`; branch: `{branch or '(detached)'}`. This comparison covers the current Git diff, not an inferred approval history.",
             f"Checks: {outcome}", "", "## Files", "", *[f"- `{p}`" for p in plan.changed],
             "", "## Analytical configuration before / after", "", "| Setting | Before | After |", "| --- | --- | --- |"]
    for key in sorted(before.keys() | after.keys()):
        lines.append(f"| {key} | {before.get(key, '(absent)')} | {after.get(key, '(absent)')} |")
    lines += ["", "## Purpose, impact and limitations", "", reason or "See the agent's user-facing explanation; no approval is inferred."]
    lines += ["", "## Review notes", "", *[f"- {note}" for note in (*plan.warnings, *plan.errors)],
              "", "## Checks selected", "", *[f"- `{subprocess.list2cmdline(command)}`" for command in plan.commands],
              "", "Review the actual file diff and the agent's explanation of intent, effects, risks, and data blockers. Confirm or request revisions in the conversation. Do not restore historical methods merely to pass checks; do not mark this batch accepted without the user's reply.",
              "", "## Tracked file diff", "", "[Open the full diff](change_review.diff)", "",
              "New untracked files are listed above; review their actual contents separately.", ""]
    output.write_text("\n".join(lines), encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--changed-file", action="append", default=[])
    parser.add_argument("--allow-canonical-output-changes", action="store_true")
    parser.add_argument("--reason", default="")
    args = parser.parse_args()
    try:
        policy = load_policy()
        base = args.base or default_base(policy)
        branch = _git("branch", "--show-current", check=False)
        paths = args.changed_file or changed_files(base)
        plan = build_plan(paths, branch, policy, args.allow_canonical_output_changes, args.reason)
    except (RuntimeError, ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"agent-gate: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(report(plan, base, branch), ensure_ascii=False, indent=2))
    else:
        print(f"Base: {base}\nBranch: {branch or '(detached)'}\nGroups: {', '.join(plan.groups) or '(none)'}\nChanged files:")
        print("\n".join(f"  {path}" for path in plan.changed) or "  (none)")
        for warning in plan.warnings: print(f"WARNING: {warning}", file=sys.stderr)
        for error in plan.errors: print(f"ERROR: {error}", file=sys.stderr)
        print("Checks:")
        for command in plan.commands: print("  " + subprocess.list2cmdline(command))
    if args.dry_run: return 0
    if plan.errors:
        write_review(plan, base, branch, "FAIL: " + "; ".join(plan.errors), args.reason)
        return 1
    for command in plan.commands:
        result = subprocess.run(command, cwd=ROOT, check=False)
        if result.returncode:
            write_review(plan, base, branch, f"FAIL ({result.returncode}): {subprocess.list2cmdline(command)}", args.reason)
            return result.returncode
    output = write_review(plan, base, branch, "PASS", args.reason)
    print("Agent gate PASS")
    if plan.changed:
        print(f"Confirmation required: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
