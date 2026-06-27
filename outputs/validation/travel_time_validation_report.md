# Travel Time Validation Report (Motorcycle Mode)

Validation against manual Google Maps consumer app measurements (two-wheeler mode) in Hanoi/Ocean Park.
Computed over **10** sample Origin-Destination (OD) pairs.

## Overall Error Statistics

| Statistic | Value | Interpretation |
| --- | --- | --- |
| **Mean Absolute Error (MAE)** | 1.90 minutes | Average magnitude of travel time error. |
| **Mean Absolute Percentage Error (MAPE)** | 22.17% | Relative error percentage. |
| **Mean Bias Error (MBE)** | -1.04 minutes | Systematic bias (negative = model is optimistic/faster). |
| **Root Mean Squared Error (RMSE)** | 2.20 minutes | Standard deviation of residuals (penalizes larger errors). |

## Sample Pair Performance Details

| OD ID | Origin | Destination | Model Time (min) | GMaps Time (min) | Abs Error (min) | Bias (min) | Error % |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | Vinhomes Ocean Park | Trạm y tế xã Kiêu Kỵ | 5.30 | 7.00 | 1.70 | -1.70 | 24.3% |
| 1 | Bệnh viện Đa khoa Gia Lâm | Trường THPT Nguyễn Văn Cừ | 9.40 | 11.00 | 1.60 | -1.60 | 14.5% |
| 2 | Brighton College Vietnam | Thế giới di động Đa Tốn | 5.40 | 6.00 | 0.60 | -0.60 | 10.0% |
| 3 | Vincom Mega Mall Ocean Pa | Trường THCS Đa Tốn | 9.60 | 9.00 | 0.60 | +0.60 | 6.7% |
| 4 | Trạm y tế thị trấn Trâu Q | Circle K Ocean Park | 3.40 | 7.00 | 3.60 | -3.60 | 51.4% |
| 5 | Greenfield School | Trường Tiểu học Nông nghi | 10.70 | 10.00 | 0.70 | +0.70 | 7.0% |
| 6 | Trường Tiểu học Đa Tốn | Siêu thị WinMart Ocean Pa | 5.60 | 9.00 | 3.40 | -3.40 | 37.8% |
| 7 | Gốm Sứ Quang Minh / Bat T | AEON MaxValu Ocean Park | 10.40 | 13.00 | 2.60 | -2.60 | 20.0% |
| 8 | VinFast Ocean Park | Công viên mùa Hạ | 13.00 | 10.00 | 3.00 | +3.00 | 30.0% |
| 9 | Trung tâm iTplus | Zmart Ocean Park | 4.80 | 6.00 | 1.20 | -1.20 | 20.0% |

## Verification Verdict

🟢 **PASS:** Mean Absolute Error is below the acceptable research threshold of 3.0 minutes.
