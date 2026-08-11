"""Write the canonical machine-readable headline metric snapshot."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.headline_metrics import build_headline_metrics
from src.provenance import write_json_atomic


def main() -> int:
    output = ROOT / "outputs" / "headline_metrics.json"
    write_json_atomic(output, build_headline_metrics(ROOT))
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
