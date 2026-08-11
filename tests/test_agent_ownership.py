"""Tests for local ownership reservations."""
import subprocess
import sys
from pathlib import Path

from scripts.check_agent_ownership import owns, validate

def record(paths=("src/routing.py",), branch="agent/x"):
    return {"task": "x", "branch": branch, "owner": "agent", "paths": list(paths), "canonical_outputs": False}
def test_exact_and_directory_ownership():
    assert owns("src/routing.py", ("src/routing.py",))
    assert owns("src/routing.py", ("src",))
def test_branch_mismatch(): assert validate(record(), ("src/routing.py",), "agent/y")
def test_outside_scope_rejected(): assert validate(record(), ("src/pilot.py",), "agent/x")
def test_valid_reservation(): assert not validate(record(("src",)), ("src/routing.py",), "agent/x")
def test_invalid_path_rejected(): assert validate(record(("../secret",)), (), "agent/x")


def test_ownership_script_runs_directly_from_any_worktree_name():
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "scripts/check_agent_ownership.py", "--help"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
