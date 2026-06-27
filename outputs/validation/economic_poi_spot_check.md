# Economic POI Spot-Check

Total economic candidate POIs to review: **50**

Each row in `economic_poi_spot_check.csv` has a `gmaps_url`. Open it, confirm
the POI is a genuine economic/employment destination, and fill `confirmed`
(yes/no) plus `true_domain` if it should be reclassified.

## Classified domain breakdown

| Domain | Count |
|---|---|
| economic | 34 |
| higher_education | 16 |

## Source breakdown

| Source | Count |
|---|---|
| osm_office | 21 |
| osm_landuse | 19 |
| osm_amenity_econ | 10 |

## Review guidance

- `osm_landuse` industrial polygons (e.g. wastewater plant, bus depot) are
  economic land but low employment density — confirm or downweight.
- `osm_office` with education names should already be higher_education;
  flag any that slipped through as economic.
- `osm_amenity_econ` banks/markets/post offices are usually reliable.