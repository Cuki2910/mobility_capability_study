"""Check whether a Hanoi GTFS feed is usable for Network B."""
from __future__ import annotations

import argparse
import json
import zipfile
from datetime import date, datetime
from pathlib import Path

import pandas as pd


REQUIRED_GTFS_FILES = {"routes.txt", "trips.txt", "stops.txt", "stop_times.txt"}
SERVICE_FILES = {"calendar.txt", "calendar_dates.txt"}


def _parse_gtfs_date(value) -> date | None:
    if pd.isna(value):
        return None
    text = str(int(value)) if isinstance(value, float) else str(value)
    try:
        return datetime.strptime(text, "%Y%m%d").date()
    except ValueError:
        return None


def _service_dates(zf: zipfile.ZipFile) -> tuple[date | None, date | None]:
    dates: list[date] = []
    if "calendar.txt" in zf.namelist():
        with zf.open("calendar.txt") as handle:
            calendar = pd.read_csv(handle)
        for col in ("start_date", "end_date"):
            dates.extend(filter(None, (_parse_gtfs_date(v) for v in calendar.get(col, []))))
    if "calendar_dates.txt" in zf.namelist():
        with zf.open("calendar_dates.txt") as handle:
            calendar_dates = pd.read_csv(handle)
        dates.extend(filter(None, (_parse_gtfs_date(v) for v in calendar_dates.get("date", []))))
    if not dates:
        return None, None
    return min(dates), max(dates)


def inspect_gtfs(zip_path: Path, today: date | None = None, stale_years: int = 2) -> dict:
    today = today or date.today()
    if not zip_path.exists():
        return {"status": "missing", "path": str(zip_path), "reason": "GTFS file not found", "network_b_baseline_limited": True}

    with zipfile.ZipFile(zip_path) as zf:
        names = set(zf.namelist())
        missing_required = sorted(REQUIRED_GTFS_FILES - names)
        missing_service = sorted(SERVICE_FILES - names)
        has_service = bool(SERVICE_FILES & names)
        route_count = stop_count = trip_count = None
        if not missing_required:
            with zf.open("routes.txt") as handle:
                route_count = int(len(pd.read_csv(handle)))
            with zf.open("stops.txt") as handle:
                stop_count = int(len(pd.read_csv(handle)))
            with zf.open("trips.txt") as handle:
                trip_count = int(len(pd.read_csv(handle)))
        min_date, max_date = _service_dates(zf) if has_service else (None, None)

    if missing_required or not has_service:
        return {
            "status": "baseline_limited",
            "path": str(zip_path),
            "reason": "missing required GTFS files",
            "missing_required_files": missing_required,
            "missing_service_files": missing_service if not has_service else [],
            "route_count": route_count,
            "stop_count": stop_count,
            "trip_count": trip_count,
            "network_b_baseline_limited": True,
        }
    if max_date is None:
        return {"status": "baseline_limited", "path": str(zip_path), "reason": "no parseable service dates", "network_b_baseline_limited": True}

    age_days = (today - max_date).days
    status = "current" if age_days <= stale_years * 365 else "baseline_limited"
    return {
        "status": status,
        "path": str(zip_path),
        "service_start_date": min_date.isoformat() if min_date else None,
        "service_end_date": max_date.isoformat(),
        "age_days": age_days,
        "route_count": route_count,
        "stop_count": stop_count,
        "trip_count": trip_count,
        "network_b_baseline_limited": status != "current",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gtfs", type=Path, default=Path("data/raw/hanoi_gtfs.zip"))
    parser.add_argument("--output", type=Path, default=Path("data/interim/hanoi_gtfs_status.json"))
    parser.add_argument("--stale-years", type=int, default=2)
    args = parser.parse_args()

    result = inspect_gtfs(args.gtfs, stale_years=args.stale_years)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "current" else 2


if __name__ == "__main__":
    raise SystemExit(main())
