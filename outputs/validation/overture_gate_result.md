# Overture POI Gate Result

Input: `data\interim\overture_only_spot_check.csv`

Verdict: **PASS**

## Gate Criteria

- Confirmed threshold: 39/55 (70%)
- Confirmed: 55/55 (100.0%)
- Unchecked: 0
- Severe failed-category bias: no

## Status Counts

| Status | Count |
|---|---:|
| confirmed | 55 |

## Recommendation

Promote `data/interim/merged_pois.gpkg` to primary POI input and rerun primary metrics.
