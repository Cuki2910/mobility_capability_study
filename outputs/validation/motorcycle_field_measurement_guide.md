# Hướng dẫn đo tay — Google Maps Android Motorcycle Mode

**Thời gian cần**: ~15 phút  
**Thiết bị**: Android, Google Maps đã cài, kết nối internet  
**Thời điểm đo**: buổi trưa ngày thường (11h–14h) để khớp với GTFS midday

---

## Cách đo mỗi pair

1. Mở Google Maps → nhấn **Chỉ đường**
2. Ô "Điểm xuất phát": nhập tọa độ gốc (copy từ cột origin_lat, origin_lon)
3. Ô "Điểm đến": nhập tọa độ đích
4. Chọn mode **Xe máy** 🏍 (icon giữa xe hơi và xe buýt)
   - Nếu không thấy icon xe máy → vuốt ngang thanh mode
   - Nếu vẫn không thấy → ghi "N/A" vào cột gmaps_motorcycle_minutes
5. Ghi lại **thời gian hiển thị** (số phút, route đầu tiên)
6. Điền vào cột `gmaps_motorcycle_minutes` trong file CSV

---

## 10 OD Pairs cần đo

| # | Từ | Đến | Tọa độ gốc | Tọa độ đích | Model (min) | GMaps car | **Motorcycle (cần đo)** |
|---|---|---|---|---|---|---|---|
| 0 | VOP Gate | BV Sông Hồng | 20.9929, 105.9451 | 20.9832, 105.9232 | 7.6 | 8 | _____ |
| 1 | VOP Gate | THCS Đa Tốn | 20.9929, 105.9451 | 20.9874, 105.9327 | 6.2 | 6 | _____ |
| 2 | VOP Gate | Brighton College | 20.9929, 105.9451 | 20.9932, 105.9391 | 1.8 | 3 | _____ |
| 3 | VOP Gate | Trạm yt Kiêu Kỵ | 20.9929, 105.9451 | 20.9803, 105.9587 | 5.3 | 6 | _____ |
| 4 | VOP Gate | BV Gia Lâm | 20.9929, 105.9451 | 21.0094, 105.9440 | 5.6 | 8 | _____ |
| 5 | Đa Tốn SE | BV Sông Hồng | 20.9705, 105.9503 | 20.9832, 105.9232 | 10.2 | 10 | _____ |
| 6 | Đa Tốn SE | TH Nông nghiệp | 20.9705, 105.9503 | 21.0045, 105.9386 | 9.2 | 9 | _____ |
| 7 | Kiêu Kỵ NE | Brighton College | 21.0100, 105.9510 | 20.9932, 105.9391 | 5.9 | 12 | _____ |
| 8 | Trâu Quỳ W | Circle K | 21.0046, 105.9226 | 21.0015, 105.9432 | 5.0 | 5 | _____ |
| 9 | Trâu Quỳ W | BV Gia Lâm | 21.0046, 105.9226 | 21.0094, 105.9440 | 7.5 | 8 | _____ |

---

## Sau khi đo xong

Gửi kết quả (10 con số phút) — tôi sẽ tính toán và cập nhật toàn bộ:
- `manual_motorcycle_validation_template.csv` (abs_error, pct_error)
- `outputs/supervisor_memo.md`
- `docs/data_sources.md`
- MAE/RMSE final cho paper

---

## Lưu ý pair đặc biệt

**Pair 2** (VOP Gate → Brighton, ~1km): Nếu Google Maps gợi ý đi bộ thay xe máy, chọn override sang xe máy. Thời gian sẽ rất ngắn.

**Pair 7** (Kiêu Kỵ → Brighton): Car = 12 min, model = 5.9 min — chênh lệch lớn nhất. Cần xem Google Maps motorcycle route đi theo đường nào (trong Vinhomes hay vòng ngoài)?

**Pair 4** (VOP Gate → BV Gia Lâm): Car = 8 min, model = 5.6 min. Kiểm tra route có qua cổng Vinhomes không.
