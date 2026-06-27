# Economic Feature Merge Summary

Base POIs (merged_pois.gpkg): 161
Economic candidates from OSM landuse/office: 50
Dropped as duplicates (30.0m threshold): 3
Fresh economic POIs added: 47
**Total POIs after merge: 208**

## Domain distribution after merge

| Domain | Count |
|---|---|
| metro_commercial | 88 |
| higher_education | 70 |
| economic | 32 |
| tertiary_healthcare | 18 |

## Source breakdown of added economic POIs

| Source | Count |
|---|---|
| osm_office | 21 |
| osm_landuse | 17 |
| osm_amenity_econ | 9 |

## Next steps

- Spot-check `spot_check_priority=medium` rows (landuse/office synthetic POIs)
- Run `python scripts/build_accessibility_inputs.py --mode network --gtfs-status baseline_limited --pois data/interim/merged_pois_economic.gpkg` to regenerate accessibility inputs
- Compare domain distribution and MAI_B before/after
- If satisfied, rerun with `--promote` to make this the default layer