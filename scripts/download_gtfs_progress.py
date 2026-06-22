"""Download Hanoi GTFS with real-time progress output (MB + %)."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen

# World Bank Data Catalog (CC-BY 4.0, Jun 2020 — midday peak period)
# Fallback order: midday -> morning -> afternoon
CANDIDATES = [
    {
        "url": "https://datacatalogfiles.worldbank.org/ddh-published/0038236/1/DR0046583/hanoi_gtfs_md.zip",
        "label": "World Bank midday (MD)",
        "dataset_page": "https://datacatalog.worldbank.org/dataset/hanoi-vietnam-general-transit-feed-specification-gtfs",
        "license": "CC-BY 4.0",
        "source_caveat": "Data collected Jun 2020; treat Network B as baseline-limited until currency confirmed.",
    },
    {
        "url": "https://datacatalogfiles.worldbank.org/ddh-published/0038236/1/DR0046582/hanoi_gtfs_am.zip",
        "label": "World Bank morning (AM)",
        "dataset_page": "https://datacatalog.worldbank.org/dataset/hanoi-vietnam-general-transit-feed-specification-gtfs",
        "license": "CC-BY 4.0",
        "source_caveat": "Data collected Jun 2020; AM period; treat Network B as baseline-limited until currency confirmed.",
    },
    {
        "url": "https://datacatalogfiles.worldbank.org/ddh-published/0038236/1/DR0046584/hanoi_gtfs_pm.zip",
        "label": "World Bank afternoon (PM)",
        "dataset_page": "https://datacatalog.worldbank.org/dataset/hanoi-vietnam-general-transit-feed-specification-gtfs",
        "license": "CC-BY 4.0",
        "source_caveat": "Data collected Jun 2020; PM period; treat Network B as baseline-limited until currency confirmed.",
    },
]
OUTPUT = Path("data/raw/hanoi_gtfs.zip")
METADATA = Path("data/interim/hanoi_gtfs_source.json")
CHUNK = 65536  # 64 KB per read


def fmt_mb(n_bytes: int) -> str:
    return f"{n_bytes / 1_048_576:.2f} MB"


def try_download(candidate: dict) -> bool:
    """Try one URL. Returns True on success, False on any error."""
    from datetime import datetime, timezone

    url = candidate["url"]
    print(f"TRYING  [{candidate['label']}]", flush=True)
    print(f"        {url}", flush=True)

    req = Request(url, headers={"User-Agent": "mobility-capability-study/0.1"})
    try:
        with urlopen(req, timeout=60) as resp:
            total = resp.headers.get("Content-Length")
            total_bytes = int(total) if total else None
            total_str = fmt_mb(total_bytes) if total_bytes else "unknown size"
            print(f"CONNECT OK — {total_str}", flush=True)

            downloaded = 0
            t0 = time.time()
            t_last = t0

            with open(OUTPUT, "wb") as f:
                while True:
                    chunk = resp.read(CHUNK)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    now = time.time()
                    if now - t_last >= 1.0:
                        elapsed = now - t0
                        speed = downloaded / elapsed if elapsed > 0 else 0
                        dl_str = fmt_mb(downloaded)
                        speed_str = f"{speed / 1024:.1f} KB/s"
                        if total_bytes:
                            pct = downloaded / total_bytes * 100
                            print(f"PROGRESS  {dl_str} / {total_str}  ({pct:.1f}%)  {speed_str}", flush=True)
                        else:
                            print(f"PROGRESS  {dl_str}  {speed_str}", flush=True)
                        t_last = now

        elapsed_total = time.time() - t0
        final_size = OUTPUT.stat().st_size
        print(f"DONE    {fmt_mb(final_size)} in {elapsed_total:.1f}s", flush=True)

        meta = {
            "source_name": f"Hanoi GTFS — {candidate['label']}",
            "source_url": url,
            "dataset_page": candidate["dataset_page"],
            "license": candidate.get("license", "unspecified"),
            "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
            "output": str(OUTPUT),
            "downloaded_this_run": True,
            "size_bytes": final_size,
            "source_caveat": candidate.get("source_caveat", ""),
            "status": "baseline_limited",
            "network_b_baseline_limited": True,
        }
        METADATA.write_text(json.dumps(meta, indent=2), encoding="utf-8")
        print(f"META    {METADATA}", flush=True)
        return True

    except Exception as exc:
        print(f"FAIL    {exc}", flush=True)
        # Remove partial file so next candidate starts clean
        if OUTPUT.exists():
            OUTPUT.unlink()
        return False


def main() -> int:
    print(f"OUTPUT  {OUTPUT}", flush=True)
    print(f"SOURCES {len(CANDIDATES)} candidates (World Bank CC-BY 4.0)", flush=True)
    print("---", flush=True)

    if OUTPUT.exists():
        size = OUTPUT.stat().st_size
        print(f"SKIP    already exists ({fmt_mb(size)})", flush=True)
        return 0

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    for candidate in CANDIDATES:
        if try_download(candidate):
            return 0
        print("", flush=True)

    from datetime import datetime, timezone
    meta = {
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
        "output": str(OUTPUT),
        "downloaded_this_run": False,
        "download_error": "all candidates failed",
        "status": "missing",
        "network_b_baseline_limited": True,
    }
    METADATA.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print("ERROR   all download candidates failed", flush=True)
    return 2


if __name__ == "__main__":
    sys.exit(main())
