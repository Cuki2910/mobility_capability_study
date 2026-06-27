# Motorcycle Speed Sensitivity

Scenarios vary only Network D motorcycle speed calibration; transit/POI inputs stay fixed.

```csv
scenario,mean_SMCI_B,share_improved,typology_kappa_vs_baseline,cells_relabelled_vs_baseline,mean_moto_opp_time_min,mean_RAC_B
baseline,0.043455337111906765,0.645021645021645,1.0,0,7.723028606166125,0.19291430753595995
slow_congestion,0.04856378600014661,0.645021645021645,0.9938351503182503,2,9.393653978069917,0.21458056100368322
fast_lane_splitting,0.04096390705859583,0.645021645021645,0.9938351503182503,2,6.969177209842298,0.1826109826722038
```

Interpretation: this is a robustness check for the motorcycle benchmark, not a new observed-speed validation.
