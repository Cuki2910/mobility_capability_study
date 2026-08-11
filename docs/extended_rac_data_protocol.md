# Extended RAC Data Protocol

Reliability, generalized cost, and mixed-traffic friction are not added to SMCI without observed or citable inputs. They remain future RAC extensions and must use the accompanying templates and validator.

## Reliability

Collect repeated OD trips by departure time with `origin_id`, `destination_id`, `departure_time`, `travel_time_min`, `source`, and `observation_date`. Estimate median and p95 travel time only after observations pass the contract. Buffer time is p95 minus median; no headway-variability coefficient is inferred from a single timetable.

## Generalized cost

Collect all columns in `data/raw/generalized_cost_template.csv`. Fare, motorcycle operating cost, parking, and value-of-time inputs require a source/date. Convert money only under a documented, cited value-of-time assumption. Do not fabricate a fare, parking cost, or discomfort coefficient.

## Mixed traffic

Collect the columns in `data/raw/mixed_traffic_friction_template.csv` from an audit or defensible observed dataset. This can diagnose sidewalk discontinuity, conflicts, safety, heat, or accessibility barriers; it does not become a fourth SMCI component.

Run `python scripts/validate_extended_rac_inputs.py <contract> --input <csv> --status <md>` before any estimator is implemented.
