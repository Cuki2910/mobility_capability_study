"""Create per-cell provenance quality grades without altering SMCI."""
from __future__ import annotations

from pathlib import Path
import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TIER_GRADE = {"observed_point": "A", "official_source": "A", "facility_source": "A", "geometry_measured": "B", "manual_checked": "C", "observed_dasymetric_weak": "D"}
SCORE = {"A": 4, "B": 3, "C": 2, "D": 1}

def main() -> int:
    grid = gpd.read_file(ROOT / "data/interim/pilot_grid.gpkg")
    pois = gpd.read_file(ROOT / "data/interim/merged_pois_observed.gpkg")
    joined = gpd.sjoin(pois.to_crs(grid.crs), grid[["cell_id", "geometry"]], how="left", predicate="within")
    joined["poi_grade"] = joined["obs_source_tier"].map(TIER_GRADE).fillna("D")
    grouped = joined.groupby("cell_id")["poi_grade"].agg(list)
    rows = []
    for cell_id in grid.cell_id:
        grades = grouped.get(cell_id, [])
        grade = min(grades, key=lambda value: SCORE[value]) if grades else "No local POI"
        rows.append({"cell_id": cell_id, "poi_quality_grade": grade, "poi_count": len(grades), "gtfs_quality_grade": "C", "vinbus_quality_grade": "B", "motorcycle_quality_grade": "C", "population_quality_grade": "B"})
    out = pd.DataFrame(rows)
    component_cols = [column for column in out if column.endswith("_quality_grade")]
    out["overall_quality_grade"] = out[component_cols].apply(
        lambda row: min([value for value in row if value in SCORE], key=lambda value: SCORE[value]), axis=1
    )
    output = ROOT / "outputs/validation/data_quality_grades.csv"; output.parent.mkdir(parents=True, exist_ok=True); out.to_csv(output, index=False)
    summary = out.overall_quality_grade.value_counts().sort_index()
    (ROOT / "outputs/validation/data_quality_grades.md").write_text("# Data Quality Grades\n\n" + "\n".join(f"- {grade}: {count} cells" for grade, count in summary.items()) + "\n\nGrades audit provenance; they are not an SMCI component or confidence interval.\n", encoding="utf-8")
    print(f"Wrote {output}")

if __name__ == "__main__": main()
