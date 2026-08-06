"""Population-preserving WorldPop redistribution constrained by building footprints."""
from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.mask import mask as rasterio_mask
from rasterio.transform import xy
from shapely.geometry import box, mapping


def _pixel_polygon(transform, row: int, column: int):
    left, top = xy(transform, row, column, offset="ul")
    right, bottom = xy(transform, row, column, offset="lr")
    return box(left, bottom, right, top)


def redistribute_population_to_buildings(
    raster_path: Path,
    grid_path: Path,
    buildings_path: Path,
    *,
    cell_id_col: str = "cell_id",
) -> pd.DataFrame:
    """Redistribute source-pixel population by footprint area within each pixel.

    For pixels with no intersecting building footprint, allocation falls back to
    grid-intersection area so that population is conserved rather than silently
    deleted. The output is deliberately an exposure sensitivity: it does not
    alter the primary WorldPop or MAI inputs.
    """
    grid = gpd.read_file(grid_path)
    buildings = gpd.read_file(buildings_path)
    if cell_id_col not in grid or grid[cell_id_col].isna().any() or grid[cell_id_col].duplicated().any():
        raise ValueError(f"grid requires unique, non-null {cell_id_col}")
    if grid.crs is None or buildings.crs is None:
        raise ValueError("grid and buildings require defined CRS")
    metric_crs = grid.estimate_utm_crs()
    if metric_crs is None:
        raise ValueError("unable to estimate metric CRS")
    grid_m = grid[[cell_id_col, "geometry"]].to_crs(metric_crs).copy()
    buildings_m = buildings[["geometry"]].to_crs(metric_crs)
    grid_index = grid_m.sindex
    building_index = buildings_m.sindex
    allocations: dict[object, float] = {cell_id: 0.0 for cell_id in grid_m[cell_id_col]}
    source_population = 0.0
    building_allocated_population = 0.0
    fallback_allocated_population = 0.0
    pixels_used = 0

    with rasterio.open(raster_path) as source:
        grid_raster = grid_m.to_crs(source.crs)
        study_raster = grid_raster.geometry.union_all()
        data, local_transform = rasterio_mask(source, [mapping(study_raster)], crop=True, nodata=source.nodata)
        data = data[0]
        nodata = source.nodata
        for local_row in range(data.shape[0]):
            for local_col in range(data.shape[1]):
                value = data[local_row, local_col]
                if np.ma.is_masked(value) or not np.isfinite(value) or value < 0 or (nodata is not None and value == nodata):
                    continue
                pixel_raster = _pixel_polygon(local_transform, local_row, local_col)
                pixel_m = gpd.GeoSeries([pixel_raster], crs=source.crs).to_crs(metric_crs).iloc[0]
                candidate_cells = list(grid_index.query(pixel_m, predicate="intersects"))
                cell_areas: dict[object, float] = {}
                for index in candidate_cells:
                    cell = grid_m.iloc[index]
                    area = float(pixel_m.intersection(cell.geometry).area)
                    if area > 0:
                        cell_areas[cell[cell_id_col]] = area
                if not cell_areas:
                    continue
                building_areas: dict[object, float] = {cell_id: 0.0 for cell_id in cell_areas}
                for building_index_value in building_index.query(pixel_m, predicate="intersects"):
                    building_piece = pixel_m.intersection(buildings_m.iloc[building_index_value].geometry)
                    if building_piece.is_empty:
                        continue
                    for index in candidate_cells:
                        cell = grid_m.iloc[index]
                        cell_id = cell[cell_id_col]
                        if cell_id in building_areas:
                            building_areas[cell_id] += float(building_piece.intersection(cell.geometry).area)
                weights = building_areas if sum(building_areas.values()) > 0 else cell_areas
                denominator = sum(weights.values())
                source_population += float(value)
                pixels_used += 1
                for cell_id, weight in weights.items():
                    allocated = float(value) * weight / denominator
                    allocations[cell_id] += allocated
                    if weights is building_areas:
                        building_allocated_population += allocated
                    else:
                        fallback_allocated_population += allocated

    baseline_area_km2 = grid_m.geometry.area / 1e6
    frame = pd.DataFrame({cell_id_col: list(allocations), "pop_sum_dasymetric": list(allocations.values())})
    frame = frame.merge(pd.DataFrame({cell_id_col: grid_m[cell_id_col], "cell_area_km2": baseline_area_km2}), on=cell_id_col, validate="one_to_one")
    frame["pop_density_dasymetric_per_km2"] = frame["pop_sum_dasymetric"] / frame["cell_area_km2"]
    frame["source_population_total"] = source_population
    frame["allocated_population_total"] = float(frame["pop_sum_dasymetric"].sum())
    frame["building_allocated_population"] = building_allocated_population
    frame["fallback_allocated_population"] = fallback_allocated_population
    frame["pixels_used"] = pixels_used
    return frame.sort_values(cell_id_col).reset_index(drop=True)
