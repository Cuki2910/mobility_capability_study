import argparse
import sys
from pathlib import Path

import geopandas as gpd
from shapely.geometry import box

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.site_config import add_site_config_argument, apply_site_config, load_site_config
from scripts.label_site_cells import label_cells


def test_west_taymo_config_loads_expected_paths():
    config = load_site_config(Path("config/sites/west_taymo.yml"))

    assert config.site_id == "west_taymo"
    assert config.get("center.lat") == 21.0027
    assert config.path_value("paths.walk_graph") == Path("data/raw/west_taymo_walk_network.graphml")
    assert config.path_value("paths.accessibility_inputs") == Path("data/interim/west_taymo_accessibility_inputs.csv")


def test_site_config_overlay_preserves_explicit_cli_args(tmp_path):
    config_path = tmp_path / "site.yml"
    config_path.write_text(
        "\n".join([
            "site_id: test_site",
            "center:",
            "  lat: 1.0",
            "paths:",
            "  grid: data/interim/site_grid.gpkg",
            "  output: data/interim/site_output.csv",
        ]),
        encoding="utf-8",
    )
    parser = argparse.ArgumentParser()
    add_site_config_argument(parser)
    parser.add_argument("--grid", type=Path, default=Path("data/interim/pilot_grid.gpkg"))
    parser.add_argument("--output", type=Path, default=Path("data/interim/pilot.csv"))

    args = parser.parse_args([
        "--site-config", str(config_path),
        "--output", "custom.csv",
    ])
    apply_site_config(args, parser, {
        "grid": "paths.grid",
        "output": "paths.output",
    })

    assert args.grid == Path("data/interim/site_grid.gpkg")
    assert args.output == Path("custom.csv")


def test_label_site_cells_assigns_planned_organic_transition(tmp_path):
    grid = gpd.GeoDataFrame(
        {"cell_id": [0, 1, 2, 3]},
        geometry=[
            box(0, 0, 1, 1),
            box(1, 0, 2, 1),
            box(2, 0, 3, 1),
            box(3, 0, 4, 1),
        ],
        crs="EPSG:3857",
    ).to_crs("EPSG:4326")
    planned = gpd.GeoDataFrame({"id": [1]}, geometry=[box(0, 0, 1.2, 1)], crs="EPSG:3857").to_crs("EPSG:4326")
    organic = gpd.GeoDataFrame({"id": [1]}, geometry=[box(2, 0, 3, 1)], crs="EPSG:3857").to_crs("EPSG:4326")

    grid_path = tmp_path / "grid.gpkg"
    planned_path = tmp_path / "planned.gpkg"
    organic_path = tmp_path / "organic.gpkg"
    grid.to_file(grid_path, driver="GPKG")
    planned.to_file(planned_path, driver="GPKG")
    organic.to_file(organic_path, driver="GPKG")

    labeled = label_cells(grid_path, planned_path, organic_path, primary_overlap=0.75)

    assert labeled.loc[labeled["cell_id"] == 0, "west_core_label"].item() == "planned_west"
    assert labeled.loc[labeled["cell_id"] == 1, "west_core_label"].item() == "transition"
    assert labeled.loc[labeled["cell_id"] == 2, "west_core_label"].item() == "organic_west"
    assert labeled.loc[labeled["cell_id"] == 3, "west_core_label"].item() == "outside_core"
