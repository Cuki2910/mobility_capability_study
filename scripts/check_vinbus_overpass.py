"""Check OSM/Overpass for VinBus route relations before manual digitization."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd


DEFAULT_BBOX = (20.85, 105.75, 21.15, 106.05)  # south west north east
DEFAULT_ENDPOINTS = (
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
)
DEFAULT_BACKOFF_SECONDS = (60, 180, 300)


def parse_refs(refs: str | None) -> list[str]:
    if not refs:
        return []
    return [ref.strip() for ref in refs.split(",") if ref.strip()]


def _relation_filters(refs: list[str], bbox: str) -> str:
    if refs:
        lines = []
        for ref in refs:
            safe_ref = ref.replace('"', "")
            lines.append(f'  relation[route=bus][ref="{safe_ref}"]({bbox});')
            lines.append(f'  relation[route=bus][name~"{safe_ref}",i]({bbox});')
        return "\n".join(lines)
    return "\n".join([
        f'  relation[route=bus][operator~"VinBus",i]({bbox});',
        f'  relation[route=bus][name~"^E0[1-9]",i]({bbox});',
        f'  relation[route=bus][ref~"^E0[1-9]",i]({bbox});',
    ])


def build_query(
    south: float,
    west: float,
    north: float,
    east: float,
    geom: bool = False,
    refs: str | None = None,
) -> str:
    out = "out geom;" if geom else "out tags;"
    bbox = f"{south},{west},{north},{east}"
    filters = _relation_filters(parse_refs(refs), bbox)
    return f"""[out:json][timeout:180];
(
{filters}
);
{out}
"""


def fetch_overpass(query: str, endpoint: str) -> dict:
    url = endpoint + "?" + urlencode({"data": query})
    request = Request(url, headers={"User-Agent": "mobility-capability-study/0.1"})
    with urlopen(request, timeout=240) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_with_retry(
    query: str,
    endpoint: str,
    backoff_seconds: tuple[int, ...] = DEFAULT_BACKOFF_SECONDS,
    sleep=time.sleep,
) -> dict:
    attempts = len(backoff_seconds) + 1
    for attempt in range(attempts):
        try:
            return fetch_overpass(query, endpoint)
        except HTTPError as exc:
            if exc.code != 429 or attempt == attempts - 1:
                raise
            sleep(backoff_seconds[attempt])
    raise RuntimeError("unreachable retry state")


def summarize(data: dict) -> list[dict]:
    rows = []
    for element in data.get("elements", []):
        tags = element.get("tags", {})
        members = element.get("members", []) or []
        member_geometry_count = sum(1 for member in members if member.get("geometry"))
        rows.append({
            "type": element.get("type"),
            "id": element.get("id"),
            "name": tags.get("name"),
            "ref": tags.get("ref"),
            "operator": tags.get("operator"),
            "from": tags.get("from"),
            "to": tags.get("to"),
            "has_geometry": bool(element.get("geometry")) or member_geometry_count > 0,
            "member_geometry_count": member_geometry_count,
        })
    return rows


def write_outputs(data: dict, output: Path, summary_csv: Path) -> list[dict]:
    output.parent.mkdir(parents=True, exist_ok=True)
    summary_csv.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    rows = summarize(data)
    pd.DataFrame(rows).to_csv(summary_csv, index=False)
    return rows


def merge_overpass_results(results: list[dict]) -> dict:
    merged = {"version": None, "generator": "merged by check_vinbus_overpass.py", "elements": []}
    seen: set[tuple[str, int]] = set()
    for data in results:
        merged["version"] = merged["version"] or data.get("version")
        for element in data.get("elements", []):
            key = (str(element.get("type")), int(element.get("id", -1)))
            if key not in seen:
                seen.add(key)
                merged["elements"].append(element)
    return merged


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bbox", nargs=4, type=float, default=DEFAULT_BBOX, metavar=("S", "W", "N", "E"))
    parser.add_argument("--endpoint", action="append", default=[])
    parser.add_argument("--geom", action="store_true", help="include relation geometry in Overpass output")
    parser.add_argument("--refs", default=None, help="comma-separated route refs, e.g. E01,E02,E03,E10,OCP1,OCP2")
    parser.add_argument("--split-refs", action="store_true", help="query each --refs value separately, then merge outputs")
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--summary-csv", type=Path, default=Path("data/interim/vinbus_route_summary.csv"))
    args = parser.parse_args()

    output = args.output or Path("data/raw/vinbus_overpass_relations_geom.json" if args.geom else "data/raw/vinbus_overpass_relations.json")
    refs = parse_refs(args.refs)
    endpoints = args.endpoint or list(DEFAULT_ENDPOINTS)
    errors: list[str] = []
    for endpoint in endpoints:
        try:
            if args.split_refs and refs:
                parts = [fetch_with_retry(build_query(*args.bbox, geom=args.geom, refs=ref), endpoint) for ref in refs]
                data = merge_overpass_results(parts)
            else:
                data = fetch_with_retry(build_query(*args.bbox, geom=args.geom, refs=args.refs), endpoint)
            rows = write_outputs(data, output, args.summary_csv)
            print(json.dumps({"endpoint": endpoint, "count": len(rows), "relations": rows}, indent=2, ensure_ascii=True))
            return 0 if rows else 2
        except Exception as exc:  # noqa: BLE001 - CLI should continue across mirrors
            errors.append(f"{endpoint}: {exc}")

    print(json.dumps({"count": None, "errors": errors, "refs": refs, "geom": args.geom}, indent=2))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
