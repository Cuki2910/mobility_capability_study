# External Validation Status

Status: `COMPLETED_WITH_LIMITATION`

## Network D Travel-Time Plausibility Check

- Audited Android Google Maps motorcycle OD pairs: 10
- Mean absolute error (MAE): 1.90 min
- Mean absolute percentage error (MAPE): 22.19%
- Mean bias error (MBE): -1.04 min
- Root mean squared error (RMSE): 2.20 min
- Exact OD results: `outputs\validation\external_validation_motorcycle_od.csv`
- Production drive graph: `data\raw\pilot_drive_network.graphml`
- Motorcycle calibration SHA-256: `cbec1e8e261cba4659a4533eb2c4b9098a29ef75d3f5237049a6f97fd9c9e065`

This validates only the Network D modeled motorcycle travel-time layer against a small, manually audited consumer-app sample. It does not externally validate SMCI, typologies, POI opportunity magnitudes, or a causal Scenario B claim.
