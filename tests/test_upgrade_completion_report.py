from scripts.make_upgrade_completion_report import ALLOWED_STATUSES, ROOT, exists


def test_report_checks_artifacts_against_worktree_root():
    assert ROOT.name == "mobility-capability-study-smci-nai-upgrade"
    assert exists("scripts/make_upgrade_completion_report.py")


def test_completion_report_uses_only_declared_statuses():
    assert "PENDING_INTEGRATION_BRANCH" not in ALLOWED_STATUSES
    assert "NOT_IMPLEMENTED_WITH_REASON" in ALLOWED_STATUSES
