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
def test_formula_requires_proposal_and_tests():
    assert build_plan(["src/accessibility.py"]).errors
    assert not build_plan(["src/accessibility.py", "proposal/proposal_v7.md", "tests/test_accessibility.py"]).errors
def test_pilot_requires_tests(): assert build_plan(["src/pilot.py"]).errors
def test_canonical_fails_on_feature_branch_and_override_requires_reason():
    assert build_plan(["outputs/pilot_summary.csv"], "agent/x").errors
    assert build_plan(["outputs/pilot_summary.csv"], "agent/x", allow_canonical=True).errors
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
