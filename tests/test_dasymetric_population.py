import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin
from shapely.geometry import box

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from dasymetric_population import redistribute_population_to_buildings


def test_dasymetric_allocation_conserves_population_and_uses_footprints(tmp_path):
    raster_path = tmp_path / "population.tif"
    with rasterio.open(
        raster_path, "w", driver="GTiff", width=1, height=1, count=1, dtype="float32",
        crs="EPSG:3857", transform=from_origin(0, 10, 10, 10), nodata=-9999,
    ) as dataset:
        dataset.write(np.array([[100]], dtype="float32"), 1)
    grid = gpd.GeoDataFrame({"cell_id": [1, 2]}, geometry=[box(0, 0, 5, 10), box(5, 0, 10, 10)], crs="EPSG:3857")
    buildings = gpd.GeoDataFrame(geometry=[box(0, 0, 1, 10), box(5, 0, 9, 10)], crs="EPSG:3857")
    grid_path, buildings_path = tmp_path / "grid.gpkg", tmp_path / "buildings.gpkg"
    grid.to_file(grid_path, driver="GPKG")
    buildings.to_file(buildings_path, driver="GPKG")

    result = redistribute_population_to_buildings(raster_path, grid_path, buildings_path)

    assert result["pop_sum_dasymetric"].sum() == pytest.approx(100)
    assert result.loc[result["cell_id"] == 2, "pop_sum_dasymetric"].item() == pytest.approx(80)
    assert result.loc[result["cell_id"] == 1, "pop_sum_dasymetric"].item() == pytest.approx(20)
    assert result["fallback_allocated_population"].iloc[0] == 0


def test_dasymetric_falls_back_to_grid_area_without_footprints(tmp_path):
    raster_path = tmp_path / "population.tif"
    with rasterio.open(
        raster_path, "w", driver="GTiff", width=1, height=1, count=1, dtype="float32",
        crs="EPSG:3857", transform=from_origin(0, 10, 10, 10), nodata=-9999,
    ) as dataset:
        dataset.write(np.array([[100]], dtype="float32"), 1)
    grid = gpd.GeoDataFrame({"cell_id": [1, 2]}, geometry=[box(0, 0, 5, 10), box(5, 0, 10, 10)], crs="EPSG:3857")
    buildings = gpd.GeoDataFrame(geometry=[], crs="EPSG:3857")
    grid_path, buildings_path = tmp_path / "grid.gpkg", tmp_path / "buildings.gpkg"
    grid.to_file(grid_path, driver="GPKG")
    buildings.to_file(buildings_path, driver="GPKG")

    result = redistribute_population_to_buildings(raster_path, grid_path, buildings_path)

    assert result["pop_sum_dasymetric"].sum() == pytest.approx(100)
    assert result["pop_sum_dasymetric"].tolist() == pytest.approx([50, 50])
    assert result["fallback_allocated_population"].iloc[0] == 100
