from pathlib import Path

import geopandas as gpd
import numpy as np
from shapely.geometry import Polygon

from scripts.make_grid_sensitivity_report import boundary_median_difference, nearest_primary_match


def test_nearest_primary_match_retains_all_alternate_cells():
    primary = gpd.GeoDataFrame({"cell_id": [1], "NAI": [1], "MAI_B": [2.0], "RAC_B": [0.5], "SMCI_B": [0.2], "typology_B": ["Integrated Capability"]}, geometry=[Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])], crs="EPSG:3857")
    alternate = gpd.GeoDataFrame({"cell_id": ["a"], "NAI": [1], "MAI_B": [2.0], "RAC_B": [0.5], "SMCI_B": [0.2], "typology_B": ["Integrated Capability"]}, geometry=[Polygon([(0.1, 0.1), (0.9, 0.1), (0.9, 0.9), (0.1, 0.9)])], crs="EPSG:3857")
    joined = nearest_primary_match(alternate, primary)
    assert len(joined) == 1
    assert joined.loc[0, "primary_cell_id"] == 1


def test_boundary_difference_is_inside_minus_outside_median(tmp_path: Path):
    cells = gpd.GeoDataFrame({"cell_id": [1, 2], "SMCI_B": [0.8, 0.2]}, geometry=[Polygon([(0, 0), (10, 0), (10, 10), (0, 10)]), Polygon([(10, 0), (20, 0), (20, 10), (10, 10)])], crs="EPSG:3857")
    boundary = gpd.GeoDataFrame(geometry=[Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])], crs="EPSG:3857")
    assert np.isclose(boundary_median_difference(cells, boundary), 0.6)
