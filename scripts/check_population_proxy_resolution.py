"""Check whether GHSL/WorldPop resolution is adequate for the pilot grid."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def classify_resolution(resolution_m: float, grid_size_m: float = 250.0) -> dict:
    if resolution_m <= grid_size_m:
        decision = "allow_fine_grained_proxy"
    elif resolution_m <= grid_size_m * 2:
        decision = "allow_with_caution"
    else:
        decision = "contextual_covariate_only"
    return {
        "resolution_m": resolution_m,
        "grid_size_m": grid_size_m,
        "decision": decision,
        "adequate_for_250m_pilot": decision != "contextual_covariate_only",
        "resolution_source": "manual_parameter",
    }


def resolution_from_raster(path: Path) -> float:
    try:
        import rasterio
    except ImportError as exc:  # pragma: no cover - optional runtime dependency
        raise RuntimeError("rasterio is required to inspect raster resolution; pass --resolution-m instead") from exc
    with rasterio.open(path) as src:
        xres, yres = src.res
        if src.crs and src.crs.is_geographic:
            import math

            center_lat = (src.bounds.top + src.bounds.bottom) / 2
            meters_per_degree_lat = 111_320.0
            meters_per_degree_lon = meters_per_degree_lat * math.cos(math.radians(center_lat))
            return float(max(abs(xres) * meters_per_degree_lon, abs(yres) * meters_per_degree_lat))
    return float(max(abs(xres), abs(yres)))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raster", type=Path, default=None)
    parser.add_argument("--resolution-m", type=float, default=None)
    parser.add_argument("--grid-size-m", type=float, default=250.0)
    parser.add_argument("--output", type=Path, default=Path("data/interim/population_proxy_resolution.json"))
    args = parser.parse_args()

    if args.resolution_m is None and args.raster is None:
        raise ValueError("Provide --resolution-m or --raster")
    resolution = args.resolution_m if args.resolution_m is not None else resolution_from_raster(args.raster)
    result = classify_resolution(resolution, args.grid_size_m)
    if args.raster:
        result["raster"] = str(args.raster)
        result["resolution_source"] = "raster_metadata"

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["adequate_for_250m_pilot"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
