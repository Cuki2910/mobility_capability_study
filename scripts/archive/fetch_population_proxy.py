"""Register or download a GHSL/WorldPop raster for population proxy checks."""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen


def copy_or_download(source: str, output: Path, force: bool = False) -> str:
    if output.exists() and not force:
        return "exists"
    output.parent.mkdir(parents=True, exist_ok=True)
    src_path = Path(source)
    if src_path.exists():
        shutil.copy2(src_path, output)
        return "copied"
    req = Request(source, headers={"User-Agent": "mobility-capability-study/0.1"})
    with urlopen(req, timeout=240) as response:
        output.write_bytes(response.read())
    return "downloaded"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, help="local raster path or URL")
    parser.add_argument("--provider", choices=["worldpop", "ghsl"], default="worldpop")
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--metadata", type=Path, default=Path("data/interim/population_proxy_source.json"))
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    output = args.output or Path("data/raw") / args.provider / Path(args.source).name
    action = copy_or_download(args.source, output, args.force)
    metadata = {
        "provider": args.provider,
        "source": args.source,
        "output": str(output),
        "action": action,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    args.metadata.parent.mkdir(parents=True, exist_ok=True)
    args.metadata.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(metadata, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
