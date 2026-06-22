"""Download the TUMI Hanoi GTFS candidate for Network B."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen


DEFAULT_URL = "https://hub.tumidata.org/dataset/be4bd93d-df74-4836-ad4b-2d9d1504fa70/resource/4b9a9939-ff2a-4fe9-985f-63b927b39655/download/hanoi_gtfs_md.zip"
DATASET_PAGE = "https://hub.tumidata.org/dataset/gtfs-hanoi"


def download_file(url: str, output: Path, force: bool = False) -> bool:
    if output.exists() and not force:
        return False
    output.parent.mkdir(parents=True, exist_ok=True)
    req = Request(url, headers={"User-Agent": "mobility-capability-study/0.1"})
    with urlopen(req, timeout=240) as response:
        output.write_bytes(response.read())
    return True


def write_metadata(output: Path, source_url: str, dataset_page: str, downloaded: bool, metadata_path: Path) -> dict:
    metadata = {
        "source_name": "TUMI GTFS: Hanoi, Midday",
        "source_url": source_url,
        "dataset_page": dataset_page,
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
        "output": str(output),
        "downloaded_this_run": downloaded,
        "license_caveat": "TUMI page says license not specified; verify original source before publication.",
        "source_caveat": "Dataset page last updated 2024-06-04; validate service dates before treating Network B as current.",
    }
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--output", type=Path, default=Path("data/raw/hanoi_gtfs.zip"))
    parser.add_argument("--metadata", type=Path, default=Path("data/interim/hanoi_gtfs_source.json"))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    try:
        downloaded = download_file(args.url, args.output, force=args.force)
        metadata = write_metadata(args.output, args.url, DATASET_PAGE, downloaded, args.metadata)
    except Exception as exc:  # noqa: BLE001 - data fetch should leave a machine-readable blocker
        metadata = write_metadata(args.output, args.url, DATASET_PAGE, False, args.metadata)
        metadata["download_error"] = str(exc)
        args.metadata.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        print(json.dumps(metadata, indent=2))
        return 2
    print(json.dumps(metadata, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
