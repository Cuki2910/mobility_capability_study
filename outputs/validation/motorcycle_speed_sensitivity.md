# Motorcycle Speed Sensitivity

Scenarios apply global factors to every Network D calibration row; transit and strict-observed POI inputs stay fixed.

```csv
scenario,global_speed_factor,calibration_sha256,poi_path,opportunity_basis,walking_threshold_m,mean_SMCI_B,share_improved,typology_kappa_vs_baseline,cells_relabelled_vs_baseline,mean_moto_opp_time_min,mean_RAC_B
baseline,1.0,9876fdbda4bc6693f57cd5ce22fcbdd430c6985595abbf904c3983b9b51ea1b6,data\interim\merged_pois_observed.gpkg,observed_strict,800.0,0.013289804372247508,0.6082251082251082,1.0,0,7.7717962359242705,0.08194977878809459
global_minus_20pct,0.8,9876fdbda4bc6693f57cd5ce22fcbdd430c6985595abbf904c3983b9b51ea1b6,data\interim\merged_pois_observed.gpkg,observed_strict,800.0,0.01672502214778799,0.6082251082251082,1.0,0,9.584875165035209,0.1019654572232004
global_plus_20pct,1.2,9876fdbda4bc6693f57cd5ce22fcbdd430c6985595abbf904c3983b9b51ea1b6,data\interim\merged_pois_observed.gpkg,observed_strict,800.0,0.011044584582021642,0.6082251082251082,1.0,0,6.563076949850313,0.06886775596634613
```

Interpretation: this is a robustness check for the motorcycle benchmark, not a new observed-speed validation.
