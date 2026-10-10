"""Offline acquisition regressions; no live API calls."""
import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path


def test_vinbus_reuses_cached_details_and_separates_directions(tmp_path):
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    script = scripts / "scrape_vinbus.py"
    shutil.copy2(Path(__file__).resolve().parents[1] / "scripts/scrape_vinbus.py", script)
    raw = tmp_path / "data/raw/vinbus_raw_json"
    details = raw / "details"
    details.mkdir(parents=True)
    (raw / "route_list_hn.json").write_text(json.dumps([{"routeId": 1, "routeNo": "E01"}]))
    (details / "detail_1.json").write_text(json.dumps({
        "routeId": 1, "headway": "10", "operationTime": "05:00-22:00",
        "stations": [
            {"stationId": 11, "stationDirection": 0, "stationOrder": 0, "lat": 21, "lng": 106},
            {"stationId": 12, "stationDirection": 1, "stationOrder": 0, "lat": 21, "lng": 106},
        ],
    }))
    (details / "._detail_1.json").write_bytes(b"macOS metadata, not JSON")
    result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    with (tmp_path / "data/raw/vinbus_pseudo_gtfs/stop_times.txt").open() as handle:
        rows = list(csv.DictReader(handle))
    assert [(row["direction_id"], row["stop_id"]) for row in rows] == [("0", "11"), ("1", "12")]
    summary = json.loads((raw / "scrape_summary.json").read_text())
    assert summary["calendar_status"] == "synthetic_legacy_2025_not_verified_service_dates"


def test_overture_rejects_invalid_release_before_network():
    script = Path(__file__).resolve().parents[1] / "scripts/fetch_overture_pois.py"
    result = subprocess.run([sys.executable, str(script), "--release", "../bad"], capture_output=True, text=True, timeout=30)
    assert result.returncode == 2
    assert "--release must have the form YYYY-MM-DD.N" in result.stderr
