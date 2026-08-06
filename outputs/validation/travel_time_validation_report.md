# Travel Time Plausibility Report (Motorcycle Mode)

Comparison against manual Google Maps consumer-app measurements (two-wheeler mode) in Hanoi/Ocean Park.
This is a small-sample plausibility check, not external calibration validation.
Computed over **10** sample Origin-Destination (OD) pairs.

## Reproducibility Metadata

- Generated UTC: `2026-07-27T16:33:37.831323+00:00`
- Drive graph: `data\raw\pilot_drive_network.graphml`
- Calibration CSV: `data\raw\motorcycle_speed_calibration.csv`
- Calibration SHA-256: `9876fdbda4bc6693f57cd5ce22fcbdd430c6985595abbf904c3983b9b51ea1b6`
- Route weight: `motorcycle_travel_time_s`
- Model times: regenerated from production routing during this run

## Overall Error Statistics

| Statistic | Value | Interpretation |
| --- | --- | --- |
| **Mean Absolute Error (MAE)** | 1.90 minutes | Average magnitude of travel time error. |
| **Mean Absolute Percentage Error (MAPE)** | 22.19% | Relative error percentage. |
| **Mean Bias Error (MBE)** | -1.04 minutes | Systematic bias (negative = model is optimistic/faster). |
| **Root Mean Squared Error (RMSE)** | 2.20 minutes | Standard deviation of residuals (penalizes larger errors). |

## Sample Pair Performance Details

| OD ID | Origin | Destination | Model Time (min) | GMaps Time (min) | Abs Error (min) | Bias (min) | Error % |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | Vinhomes Ocean Park | Trạm y tế xã Kiêu Kỵ | 5.26 | 7.00 | 1.74 | -1.74 | 24.9% |
| 1 | Bệnh viện Đa khoa Gia Lâm | Trường THPT Nguyễn Văn Cừ | 9.43 | 11.00 | 1.57 | -1.57 | 14.2% |
| 2 | Brighton College Vietnam | Thế giới di động Đa Tốn | 5.43 | 6.00 | 0.57 | -0.57 | 9.6% |
| 3 | Vincom Mega Mall Ocean Pa | Trường THCS Đa Tốn | 9.61 | 9.00 | 0.61 | +0.61 | 6.8% |
| 4 | Trạm y tế thị trấn Trâu Q | Circle K Ocean Park | 3.41 | 7.00 | 3.59 | -3.59 | 51.4% |
| 5 | Greenfield School | Trường Tiểu học Nông nghi | 10.74 | 10.00 | 0.74 | +0.74 | 7.4% |
| 6 | Trường Tiểu học Đa Tốn | Siêu thị WinMart Ocean Pa | 5.59 | 9.00 | 3.41 | -3.41 | 37.9% |
| 7 | Gốm Sứ Quang Minh / Bat T | AEON MaxValu Ocean Park | 10.39 | 13.00 | 2.61 | -2.61 | 20.0% |
| 8 | VinFast Ocean Park | Công viên mùa Hạ | 12.96 | 10.00 | 2.96 | +2.96 | 29.6% |
| 9 | Trung tâm iTplus | Zmart Ocean Park | 4.79 | 6.00 | 1.21 | -1.21 | 20.2% |

## Project-Defined Screening Flag

**Within project screening bound:** MAE is below the internally defined 3.0-minute diagnostic threshold. This threshold is not an external research standard.
