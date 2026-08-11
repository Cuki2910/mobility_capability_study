# External Validation Protocol

External validation requires an observed outcome with a unit, date, and citable source. Acceptable outcomes include audited travel times, observed transit usage, or independently collected accessibility outcomes. The pipeline refuses to estimate a validation score from model outputs, POI proxies, or empty template rows.

Cell-linked outcomes use `data/raw/external_validation_template.csv`. Audited travel times are an OD-level exception: their origin and destination coordinates must be retained, and the validator must recompute the matching exact OD path on the production network. It must not compare an OD observation to a cell-level opportunity-weighted mean travel time.

Run the generic schema check with `python scripts/external_validation.py`. Run the audited Android motorcycle check with:

```powershell
python scripts/external_validation.py --manual-motorcycle-od outputs/validation/manual_motorcycle_validation_template.csv
```

The audited OD check can support `COMPLETED_WITH_LIMITATION` for Network D travel-time plausibility only. It does not externally validate SMCI, typology, opportunity magnitudes, or a causal Scenario B claim. Until a valid observation source is supplied, the generic cell-linked contract remains `NOT_RUN_DATA_REQUIRED`.
