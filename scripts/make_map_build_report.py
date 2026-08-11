"""Write provenance for the generated interactive map."""
from __future__ import annotations

import hashlib
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    grid_path = ROOT / "data/interim/pilot_grid.gpkg"
    metrics_path = ROOT / "data/processed/pilot_metrics.csv"
    html_path = ROOT / "outputs/maps/ocean_park_interactive.html"
    report_path = ROOT / "outputs/maps/map_build_report.md"
    grid = gpd.read_file(grid_path)
    metrics = pd.read_csv(metrics_path)
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    report = "\n".join([
        "# Interactive Map Build Report",
        "",
        f"- Commit: `{revision}`",
        f"- Timestamp (UTC): {datetime.now(timezone.utc).isoformat()}",
        "- Primary NAI threshold: 800 m",
        "- SMCI form: equal-weight geometric mean",
        f"- Cells: {len(grid)}",
        f"- Zero NAI cells: {int((metrics['NAI'] == 0).sum())}",
        f"- Grid CRS: {grid.crs}",
        f"- Input SHA-256 (grid): `{digest(grid_path)}`",
        f"- Input SHA-256 (metrics): `{digest(metrics_path)}`",
        f"- HTML size: {html_path.stat().st_size:,} bytes",
        "- Map loads the embedded analytical dataset once and restyles layers client-side.",
        "",
    ])
    report_path.write_text(report, encoding="utf-8")
    print(f"Wrote {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
