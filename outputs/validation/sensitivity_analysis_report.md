# Sensitivity Analysis Report (MAI and SMCI Parameters)

Sensitivity analysis evaluating the stability of the Metropolitan Accessibility Index (MAI) 
and Sustainable Mobility Capability Index (SMCI) under different domain weights and time-decay thresholds.

## 1. Domain Weight Sensitivity

Comparing different weights across four opportunity domains:
- **default**: Economic (0.40), Education (0.20), Healthcare (0.20), Commerce (0.20)
- **equal**: All domains equal (0.25)
- **job_heavy**: Economic (0.50), Education (0.15), Healthcare (0.15), Commerce (0.20)

| Weight Scenario | Spearman ρ (vs baseline) | Cohen's Kappa (vs baseline) | Mean SMCI_B | Share Improved |
| --- | --- | --- | --- | --- |
| **default** | 1.0000 | 1.0000 | 0.1153 | 76.41% |
| **equal** | 0.9993 | 0.9554 | 0.1131 | 76.41% |
| **job_heavy** | 0.9994 | 0.9680 | 0.1174 | 76.84% |

## 2. Time-Decay Parameter Sensitivity

Comparing linear decay windows representing accessibility thresholds:
- **pessimistic_20_40**: Full access up to 20 mins, zero access after 40 mins.
- **baseline_30_60**: Full access up to 30 mins, zero access after 60 mins.
- **optimistic_45_90**: Full access up to 45 mins, zero access after 90 mins.

| Decay Scenario | Spearman ρ (vs baseline) | Cohen's Kappa (vs baseline) | Mean SMCI_B | Share Improved |
| --- | --- | --- | --- | --- |
| **pessimistic_20_40** | 0.9830 | 0.8451 | 0.1027 | 85.28% |
| **baseline_30_60** | 1.0000 | 1.0000 | 0.1153 | 76.41% |
| **optimistic_45_90** | 0.9862 | 0.9103 | 0.1292 | 52.60% |

## 3. Stability Verdict

A typology Kappa score **>= 0.80** indicates high stability, meaning the classification 
system is robust to minor parameter adjustments. A Spearman rank correlation **>= 0.90** 
indicates that the relative ranking of cells is highly preserved.

🟢 **Weight Stability:** PASS. Typology is robust to alternative domain weights.
🟢 **Decay Stability:** PASS. Typology is robust to alternative time-decay thresholds.
