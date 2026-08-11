"""Input contracts for future RAC extensions that must not fabricate evidence."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class DataContract:
    name: str
    required_columns: tuple[str, ...]
    purpose: str


CONTRACTS = {
    "reliability": DataContract(
        "reliability",
        ("origin_id", "destination_id", "departure_time", "travel_time_min", "source", "observation_date"),
        "Observed repeated departure-time travel records for median/p95 and buffer time.",
    ),
    "generalized_cost": DataContract(
        "generalized_cost",
        ("origin_id", "destination_id", "walk_min", "wait_min", "in_vehicle_min", "transfer_penalty_min", "fare_vnd", "motorcycle_operating_vnd", "parking_vnd", "value_of_time_vnd_per_min", "source", "observation_date"),
        "Observed or cited cost inputs for generalized-minutes RAC; values of time cannot be invented.",
    ),
    "mixed_traffic": DataContract(
        "mixed_traffic",
        ("cell_id", "friction_indicator", "measurement", "source", "observation_date"),
        "Observed pedestrian/mixed-traffic friction measurements; no proxy multiplier is assumed.",
    ),
}


def validate_contract(frame: pd.DataFrame, contract_name: str) -> list[str]:
    """Return validation failures; an empty input is data-required, not evidence."""
    if contract_name not in CONTRACTS:
        raise ValueError(f"Unknown contract: {contract_name}")
    contract = CONTRACTS[contract_name]
    missing = [column for column in contract.required_columns if column not in frame]
    if missing:
        return [f"missing columns: {', '.join(missing)}"]
    if frame.empty:
        return ["no observations"]
    nulls = [column for column in contract.required_columns if frame[column].isna().any()]
    return [f"null required values: {', '.join(nulls)}"] if nulls else []
