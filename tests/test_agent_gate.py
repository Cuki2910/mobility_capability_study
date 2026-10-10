"""Tests for the policy-driven agent gate."""
import json
import scripts.agent_gate as agent_gate
from scripts.agent_gate import build_plan, load_policy, normalize_paths, report

def names(plan): return {" ".join(command) for command in plan.commands}
def test_docs_select_consistency_only():
    commands = names(build_plan(["docs/agent_workflow.md"]))
    assert any("check_document_consistency.py" in command for command in commands)
    assert not any("pytest" in command for command in commands)
def test_core_selects_full_tests(): assert any("pytest tests/ -v" in command for command in names(build_plan(["src/routing.py"])))
def test_formula_missing_coupled_files_requests_review():
    assert not build_plan(["src/accessibility.py"]).errors
    assert build_plan(["src/accessibility.py"]).warnings
    assert not build_plan(["src/accessibility.py", "proposal/proposal_v7.md", "tests/test_accessibility.py"]).errors
def test_pilot_missing_tests_requests_review(): assert build_plan(["src/pilot.py"]).warnings
def test_canonical_change_requests_confirmation_without_branch_lock():
    assert not build_plan(["outputs/pilot_summary.csv"], "agent/x").errors
    plan = build_plan(["outputs/pilot_summary.csv"], "agent/x", allow_canonical=True, reason="integration regeneration")
    assert not plan.errors and plan.warnings
def test_canonical_allowed_on_integration_branch(): assert not build_plan(["outputs/pilot_summary.csv"], "main").errors
def test_paths_normalized_and_unsafe_rejected():
    assert normalize_paths([r"src\routing.py", "src/routing.py"]) == ("src/routing.py",)
    try: normalize_paths(["../secret"])
    except ValueError: pass
    else: raise AssertionError("unsafe path accepted")
def test_changed_files_preserves_nul_delimited_non_ascii_paths(monkeypatch):
    calls = []
    def fake_git(*args, **kwargs):
        calls.append(args)
        return "docs/upgrade_cmt/kế_hoạch.md\0"
    monkeypatch.setattr(agent_gate, "_git", fake_git)
    assert agent_gate.changed_files("main") == ("docs/upgrade_cmt/kế_hoạch.md",)
    assert all("-z" in call for call in calls)
def test_policy_and_json_report_shape():
    policy = load_policy(); plan = build_plan(["README.md"], "main", policy)
    payload = report(plan, "main", "main")
    assert json.loads(json.dumps(payload))["changed"] == ["README.md"]
    assert payload["confirmation"] == "required"

def test_review_records_new_spec_without_approving_it(tmp_path, monkeypatch):
    monkeypatch.setattr(agent_gate, "ROOT", tmp_path)
    monkeypatch.setattr(agent_gate, "_git", lambda *args, **kwargs: '{"analytical_spec":{"nai_primary_threshold_m":800}}')
    (tmp_path / "config").mkdir()
    (tmp_path / "config/pipeline.json").write_text('{"analytical_spec":{"nai_primary_threshold_m":1000}}')
    path = agent_gate.write_review(build_plan(["config/pipeline.json"]), "main", "agent/new", "PASS")
    text = path.read_text()
    assert "PENDING_USER_CONFIRMATION" in text and "| nai_primary_threshold_m | 800 | 1000 |" in text
    assert "Checks: PASS" in text
    assert path.with_suffix(".diff").is_file()

def test_failed_check_still_writes_pending_review(tmp_path, monkeypatch):
    from types import SimpleNamespace
    monkeypatch.setattr(agent_gate, "ROOT", tmp_path)
    monkeypatch.setattr(agent_gate, "_git", lambda *args, **kwargs: "{}" if args[0] == "show" else "")
    monkeypatch.setattr(agent_gate.subprocess, "run", lambda *args, **kwargs: SimpleNamespace(returncode=7))
    monkeypatch.setattr(agent_gate.sys, "argv", ["agent_gate.py", "--base", "main", "--changed-file", "README.md"])
    assert agent_gate.main() == 7
    text = (tmp_path / ".agent/change_review.md").read_text()
    assert "PENDING_USER_CONFIRMATION" in text and "Checks: FAIL (7)" in text
