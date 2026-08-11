import pandas as pd

from src.extended_rac_contracts import CONTRACTS, validate_contract


def test_empty_schema_is_data_required_not_validated():
    frame = pd.DataFrame(columns=CONTRACTS["reliability"].required_columns)
    assert validate_contract(frame, "reliability") == ["no observations"]


def test_missing_required_columns_are_reported():
    assert "missing columns:" in validate_contract(pd.DataFrame(), "mixed_traffic")[0]
