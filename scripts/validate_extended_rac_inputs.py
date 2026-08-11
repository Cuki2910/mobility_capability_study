"""Validate future RAC extension inputs and emit data-required status when absent."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.extended_rac_contracts import CONTRACTS, validate_contract


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", choices=sorted(CONTRACTS))
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--status", type=Path, required=True)
    args = parser.parse_args()
    frame = pd.read_csv(args.input)
    failures = validate_contract(frame, args.contract)
    args.status.parent.mkdir(parents=True, exist_ok=True)
    if failures:
        args.status.write_text(
            f"# {args.contract.replace('_', ' ').title()} Status\n\nStatus: `NOT_RUN_DATA_REQUIRED`\n\n- " + "\n- ".join(failures) + "\n",
            encoding="utf-8",
        )
        print("NOT_RUN_DATA_REQUIRED")
        return 0
    args.status.write_text(
        f"# {args.contract.replace('_', ' ').title()} Status\n\nStatus: `READY_TO_RUN`\n\nValidated {len(frame)} rows; this does not itself estimate RAC.\n",
        encoding="utf-8",
    )
    print("READY_TO_RUN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
