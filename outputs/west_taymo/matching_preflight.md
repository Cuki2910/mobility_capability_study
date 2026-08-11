# West Tay Mo Matching Preflight

Generated UTC: 2026-08-11T05:37:44.940238+00:00

## Measured Local Context

| Variable | Smart City core | Tay Mo core | Status |
|---|---:|---:|---|
| Boundary area km2 | 1.855 | 4.245 | measured from boundary |
| Network distance to Hoan Kiem |  |  | MATCHING GATE FAILED: at least one west candidate core is outside the preregistered +/-15% tolerance. |

## Network-Distance Matching

| origin | drive_distance_km | ratio_to_ocean_park | within_15pct_of_ocean_park |
| --- | --- | --- | --- |
| smart_city_core | 14.3119 | 0.8888 | True |
| tay_mo_core | 13.1073 | 0.814 | False |
| ocean_park | 16.1025 | 1.0 | True |

## WorldPop by Core Label

| label | cells | population | mean_population_per_cell |
| --- | --- | --- | --- |
| organic_west | 59 | 21213.142 | 359.545 |
| outside_core | 305 | 93279.133 | 305.833 |
| planned_west | 23 | 6076.685 | 264.204 |
| transition | 75 | 21313.404 | 284.179 |

## Next Protocol Step

- Do not promote the current planned/organic pair if the +/-15% M1 gate fails.
- Select a new control core or a pre-specified shifted bbox only with an explicit protocol update; do not tune the analysis results.
