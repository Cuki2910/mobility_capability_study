# Economic Feature Merge Summary

Base POIs (merged_pois.gpkg): 418
Economic candidates from OSM landuse/office: 37
Dropped as duplicates (30.0m threshold): 37
Fresh economic POIs added: 0
**Total POIs after merge: 418**

## Domain distribution after merge

| Domain | Count |
|---|---|
| metro_commercial | 220 |
| higher_education | 120 |
| tertiary_healthcare | 40 |
| economic | 38 |

## Source breakdown of added economic POIs

| Source | Count |
|---|---|

## Next steps

- Spot-check `spot_check_priority=medium` rows (landuse/office synthetic POIs)
- Run `python scripts/build_accessibility_inputs.py --mode network --gtfs-status baseline_limited --pois data\interim\west_taymo_merged_pois_economic.gpkg` to regenerate accessibility inputs
- Compare domain distribution and MAI_B before/after
- If satisfied, rerun with `--promote` to make this the default layer