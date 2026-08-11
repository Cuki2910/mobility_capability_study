from pathlib import Path

import pandas as pd

from scripts.west_taymo_readiness import unresolved_observed_opportunities


def test_west_taymo_readiness_script_preserves_strict_gate():
    source = (Path(__file__).resolve().parents[1] / "scripts" / "west_taymo_readiness.py").read_text(encoding="utf-8")
    assert "CODE_COMPLETE_DATA_REQUIRED" in source
    assert "needs_source" in source
    assert "shared normalization" in source
    assert "Observed-strict site metrics" in source
    assert "MATCHING_GATE_FAILED" in source


def test_current_observed_audit_schema_can_pass_the_strict_gate():
    audit = pd.DataFrame({"obs_audit_status": ["verified", "geometry_measured", "exclude_not_destination"]})
    assert unresolved_observed_opportunities(audit) == 0


def test_observed_audit_needs_source_remains_a_blocker():
    audit = pd.DataFrame({"obs_audit_status": ["verified", "needs_source"]})
    assert unresolved_observed_opportunities(audit) == 1
