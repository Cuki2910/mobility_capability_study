# POI Source Merge Summary

OSM input POIs:      250
Overture input POIs: 183
Match distance:      30.0 m

## Source Agreement

| Source label     | Count | % of merged |
|---|---:|---:|
| both (matched)   | 13    | 3.1% |
| osm_only         | 237 | 56.7% |
| overture_only    | 168  | 40.2% |
| **Total**        | **418** | — |

## Interpretation

- `both` POIs have two-source confirmation — highest confidence.
- `osm_only` POIs are in OSM but not Overture — may be very local or recently added.
- `overture_only` POIs are new candidates not in current OSM data — spot-check these first.

## Recommended Next Step

Spot-check the 168 `overture_only` POIs to determine how many are real, relevant,
and missing from the current OSM NAI calculation. If a meaningful share are confirmed,
re-run build_accessibility_inputs.py with merged_pois.gpkg as the POI source.
