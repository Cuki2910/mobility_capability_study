# Tóm Tắt Đề Xuất Nghiên Cứu (Bản Dành Cho Giáo Sư)

## Khả Năng Giao Thông Bền Vững Bị Phân Mảnh trong Megaproject "Xanh" Phụ Thuộc Xe Máy
### Khung phân tích hai tầng và cạnh tranh phương thức — Trường hợp Vinhomes Ocean Park, Hà Nội

**Người đề xuất:** Cuki2910
**Khu vực nghiên cứu:** Vinhomes Ocean Park, Gia Lâm, Hà Nội
**Ngày:** Tháng 6 năm 2026
**Trạng thái:** Pilot kiểm chứng phương pháp đã hoàn thành — sẵn sàng mở rộng toàn diện
**Tạp chí mục tiêu:** Journal of Transport Geography

---

## 1. Câu Hỏi Nghiên Cứu

> **Một dự án được quảng bá là "xanh" có thực sự tạo ra khả năng giao thông bền vững không, khi đời sống hàng ngày vẫn phụ thuộc vào xe máy?**

Ocean Park là khu đô thị 250+ hectare, có xe buýt điện VinBus, được tiếp thị là "xanh". Nhưng cư dân vẫn không thể tới đại học, bệnh viện, hay trung tâm việc làm bằng đi bộ + giao thông công cộng **nhanh ngang xe máy**. Nghiên cứu này đo lường chính xác khoảng cách đó.

**Lập luận cốt lõi:** Tiện ích ở gần (đi bộ tới được) **không đủ** để tạo ra giao thông bền vững, nếu giao thông công cộng **không cạnh tranh được với xe máy**.

---

## 2. Đóng Góp Mới

Các khung đo khả năng tiếp cận hiện có đều có một điểm yếu:

| Khung hiện có | Vấn đề | Tài liệu tham khảo |
|---|---|---|
| Walk Score, "thành phố 15 phút" | Quá cục bộ — bỏ qua bất bình đẳng quy mô đô thị | Walkability score: Carr et al. (2010); 15-min city: Moreno et al. (2021) |
| Mô hình tiếp cận việc làm toàn thành phố | Quá tổng hợp — che giấu loại trừ ở cấp khu phố | Gravity models: Hansen (1959); cumulative accessibility: Handy & Niemeier (1997) |
| Đo cạnh tranh so với **ô tô** | Không phù hợp Việt Nam — đối thủ thực sự là **xe máy** | Mode choice models assume car competition: Ben-Akiva & Lerman (1985); Southeast Asia motorcycle dominance: Pucher & Buehler (2008), Moretti & Caferri (2022) |

**Khung của nghiên cứu này** kết hợp ba điều mà chưa khung nào làm cùng lúc:
1. **Hai tầng** — tách rõ tiện ích khu phố (đi bộ) khỏi tiếp cận đô thị (transit).
2. **Cạnh tranh phương thức** — hỏi transit có thay đổi được lựa chọn đi lại không, chứ không chỉ "có tồn tại".
3. **Lấy xe máy làm chuẩn** — phù hợp 1.5 tỷ dân ở Đông Nam Á, Nam Á, Mỹ Latinh.

---

## 3. Bốn Chỉ Số (Cách Đo)

Toàn bộ công thức nằm trong `src/accessibility.py` (đã code, đã test — đây là nguồn chuẩn, không phải prose).

### NAI — Chỉ Số Tiếp Cận Khu Phố
**Hỏi:** Đi bộ tới được bao nhiêu tiện ích hàng ngày?
```
NAI_i = số POI (trường, cửa hàng, phòng khám, công viên) 
        reachable by walking network from grid cell i
        within the 1 km neighborhood threshold
```
Dùng phép **đếm** đơn giản: ở cấp khu phố, có trường gần quan trọng hơn khoảng cách chính xác. Không dùng mô hình hấp dẫn (gravity model) hay suy giảm theo thời gian — chỉ đếm.

### MAI — Chỉ Số Tiếp Cận Đô Thị
**Hỏi:** Bằng đi bộ + transit, tiếp cận được bao nhiêu cơ hội quy mô lớn (việc làm, bệnh viện, đại học)?
```
MAI_i = 0.40 × A_econ + 0.20 × A_edu + 0.20 × A_health + 0.20 × A_commerce

Với mỗi nhóm cơ hội k:
  A_k = Σ (POI trên cùng nhóm) × trọng số POI × f(thời gian tới POI)

Hàm suy giảm f(t):
  f(t) = 1                  nếu t ≤ 30 phút
       = (60−t) / 30        nếu 30 < t ≤ 60 phút
       = 0                  nếu t > 60 phút
```

**Ví dụ:** Từ ô lưới, tới bệnh viện mất 25 phút (f = 1, full value); tới cửa hàng mất 45 phút (f = 0.5, half value); tới trường mất 75 phút (f = 0, loại bỏ). Mỗi cơ hội **tính một lần qua transit**, rồi lại **tính một lần qua xe máy** với cùng công thức để so sánh.

### RAC — Cạnh Tranh Tương Đối (chỉ số then chốt)
**Hỏi:** Transit có cạnh tranh được với xe máy không?
```
RAC_i = √ (RAC_time_i × RAC_opp_i)

Với:
  RAC_time = (thời gian transit) / (thời gian xe máy)  [cao = xe máy nhanh hơn]
  RAC_opp  = (cơ hội qua transit) / (cơ hội qua xe máy) [cao = xe máy tiếp cận nhiều hơn]
  
Cơ hội tính bằng MAI dùng cùng hàm suy giảm f(t) cho cả transit và xe máy.
```

**Giải thích:**
- **RAC_opp = MAI_transit / MAI_motorcycle:** Lấy chỉ số MAI tính từ đi bộ+transit, chia cho MAI tính từ đi bộ+xe máy. Nếu transit tiếp cận được 80 cơ hội mà xe máy 100, RAC_opp = 0.80.
- **Dùng trung bình nhân** √(a×b) để cân bằng: nếu transit nhanh nhưng ít cơ hội, hoặc nhiều cơ hội nhưng chậm, RAC vẫn thấp. Cần vừa nhanh vừa tiếp cận.
- RAC ≫ 1 → xe máy thắng áp đảo
- RAC ≈ 1 → transit cạnh tranh được
- RAC ≪ 1 → transit tốt hơn xe máy (hiếm gặp)

### SMCI — Chỉ Số Khả Năng Giao Thông Bền Vững (kết quả tổng hợp)
```
SMCI = NAI_chuẩn × MAI_chuẩn × RAC_chuẩn
```
Dùng phép **nhân**: yếu ở bất kỳ tầng nào → SMCI = 0. Một nơi cần **đồng thời** đi bộ tốt, tiếp cận đô thị tốt, và transit cạnh tranh.

### Bốn Phân Loại Không Gian (chia theo lý thuyết, không phải clustering)
| Loại | Đặc điểm |
|---|---|
| 🟢 **Khả Năng Tích Hợp** | Cục bộ tốt + đô thị tốt + transit cạnh tranh |
| 🟡 **Khả Năng Rời Rạc** | Đi bộ tốt nhưng transit yếu |
| 🟠 **Phụ Thuộc Transit** | Cục bộ yếu, phải dựa hoàn toàn vào transit |
| 🔴 **Bị Khóa Xe Máy** | Cả hai đều yếu — mắc kẹt với xe máy |

---

## 4. Thiết Kế So Sánh

```
Bốn mạng lưới:
  A: chỉ đi bộ
  B: đi bộ + transit hiện có        (baseline GTFS 2018, trước VinBus)
  C: đi bộ + transit + VinBus       (kịch bản can thiệp)
  D: xe máy                          (chuẩn cạnh tranh)

Hai kịch bản:
  Kịch bản A = mạng A+B (KHÔNG VinBus)
  Kịch bản B = mạng A+C (CÓ VinBus)
  Δ SMCI = SMCI(B) − SMCI(A)        ← dùng chung thang chuẩn hóa A+B
```

---

## 5. Kết Quả Pilot

**Khu vực:** Ocean Park + 2 km vùng đệm · Lưới 250 m × 250 m = **462 ô** · Dân số ~**78,816** (WorldPop 2020)

### 5.1 VinBus cải thiện đáng kể, nhưng không chuyển đổi triệt để

| Chỉ tiêu | Kịch bản A (không VinBus) | Kịch bản B (có VinBus) |
|---|---|---|
| SMCI trung bình | **0.047** | **0.098** |
| Δ SMCI trung bình | — | **+0.050** |
| Ô cải thiện | — | **216 / 462 (46.8%)** |
| Ô suy giảm | — | **0** (VinBus không bao giờ làm hại) |

→ VinBus tăng SMCI ~2 lần, nhưng phần lớn ô vẫn ở tầng thấp.

### 5.2 Phân mảnh không gian tồn tại dai dẳng (Kịch bản B)

| Phân loại | Số ô | % ô | % dân số |
|---|---|---|---|
| 🟢 Khả Năng Tích Hợp | 166 | 35.9% | 30.9% |
| 🟡 Khả Năng Rời Rạc | 65 | 14.1% | 19.2% |
| 🟠 Phụ Thuộc Transit | 65 | 14.1% | 16.2% |
| 🔴 Bị Khóa Xe Máy | 166 | 35.9% | 33.6% |

→ **34% dân số (~26,000 người) vẫn ở vùng Bị Khóa Xe Máy** dù đã có can thiệp transit.

### 5.3 Vùng zero-access là khu dân cư thực, không phải hồ/công viên

- 455/462 ô có dấu chân công trình (dữ liệu VIDA, 41,816 đa giác).
- **162 ô zero-NAI là đất đã xây dựng**, chứa **26,869 dân (34.1%)**.
- → Tiếp cận bằng 0 = khu dân cư thực sự không được phục vụ, **không phải lỗi dữ liệu**.

### 5.4 Cảnh báo công bằng: nơi đông dân lại kém bền vững hơn

- Tương quan Spearman ρ(dân số, SMCI_B) = **−0.11** → ô đông dân thường có SMCI thấp hơn.
- SMCI trung bình theo trọng số dân số (0.083) thấp hơn không-trọng-số (0.098) **15%** → trung bình thô **đánh giá cao** trải nghiệm thực của đa số cư dân.

---

## 6. Kiểm Tra Chất Lượng Dữ Liệu

| Kiểm tra | Kết quả |
|---|---|
| POI spot-check | 20/20: 14 xác nhận, 2 trùng, 2 sai phân loại, 2 thiếu |
| Xác thực thời gian xe máy | 10/10 cặp Google Maps (Android): MAE = **1.9 phút**, lệch −1.04 phút (hơi lạc quan) |
| Độ phân giải WorldPop | 92.77 m — phù hợp lưới 250 m |
| Dấu chân công trình | 41,816 đa giác VIDA (độ tin cậy ≥0.70); 455/462 ô đã xây |
| Độ bền phân loại (RAC chỉ tính thời gian) | κ = **0.845**, chỉ 52/462 ô đổi nhãn → **phát hiện chính bền vững** |

---

## 7. Hạn Chế & Cách Xử Lý (trình bày thẳng)

| Hạn chế | Cách xử lý |
|---|---|
| POI OSM chưa đầy đủ (thiếu đại học, trung tâm việc làm lớn ở Ocean Park) → tầng kinh tế/giáo dục dùng proxy thương mại | Ghi nhận rõ; đã chạy độ nhạy với POI Overture (+55 điểm); khuyến nghị xác minh ở nghiên cứu toàn diện |
| GTFS 2018 (trước VinBus) | Lựa chọn có chủ đích làm baseline tiền can thiệp; hình học trạm vẫn dùng được, chỉ lịch chạy là cũ |
| VinBus dùng proxy hành lang, chưa GTFS đầy đủ | 39 quan hệ VinBus có sẵn trong OSM → có thể nâng cấp lên định tuyến cấp trạm |
| MAI và RAC tương quan cao (VIF > 5) | Đã chạy độ nhạy RAC-chỉ-thời-gian (κ=0.845) → kết quả bền vững; giữ đặc tả RAC đầy đủ kèm cảnh báo |
| 36% ô có NAI = 0 (phân bố lệch) | Dùng thống kê phân vị/hạng + nhóm delta thay vì chỉ dựa vào trung bình |

---

## 8. Hàm Ý Chính Sách

**Cho thiết kế megaproject "xanh":**
- Tiện ích ở gần ≠ giao thông bền vững. Ocean Park đi bộ tốt nhưng ~70% ô vẫn Phụ Thuộc Transit hoặc Bị Khóa Xe Máy.
- Cần **tích hợp transit + quy hoạch sử dụng đất**, không chỉ thêm tuyến buýt.
- 34% dân vẫn ở vùng transit không cạnh tranh nổi xe máy → vấn đề **công bằng không gian**.

**Cho quy hoạch transit:**
- Tần suất quan trọng — VinBus 15 phút cạnh tranh được; buýt thưa thì không.
- Lợi ích tập trung trên hành lang tuyến; cư dân ngoài hành lang hưởng lợi tối thiểu.
- **Lấy xe máy làm chuẩn, không phải ô tô** — mô hình giao thông tiêu chuẩn bỏ qua lợi thế tốc độ xe máy → đánh giá cao quá mức khả năng cạnh tranh của transit.

**Cho nghiên cứu đô thị:**
- Khung **chuyển giao được** sang mọi thành phố phụ thuộc xe máy (TP.HCM, Bangkok, Jakarta, Bangalore).
- Phân loại **diễn giải được** → đội quy hoạch nhắm mục tiêu can thiệp thay vì đọc điểm số thô.
- **Tái lập được** — toàn bộ code, công thức, dữ liệu mã nguồn mở.

---

## 9. Bước Tiếp Theo

**Trước mắt (trước khi mở rộng):**
1. Spot-check 55 POI Overture → quyết định bộ POI hợp nhất làm primary.
2. Nâng cấp định tuyến VinBus từ proxy hành lang lên cấp trạm (dùng 39 quan hệ OSM).
3. Tích hợp trọng số dân số/việc làm vào MAI, hoặc dán nhãn MAI hiện tại là proxy.

**Trung hạn (nghiên cứu toàn diện 6–12 tháng):**
4. Mở rộng lưới + pipeline ra toàn vùng nghiên cứu Hà Nội.
5. Tích hợp GTFS hiện hành khi xác nhận được ngày dịch vụ.
6. Thay proxy POI thương mại bằng vị trí trung tâm việc làm thực.

---

## Phụ Lục: Thuật Ngữ Nhanh

| Viết tắt | Nghĩa | Thang |
|---|---|---|
| **NAI** | Chỉ số tiếp cận khu phố | đếm (0–20+) |
| **MAI** | Chỉ số tiếp cận đô thị | composite (0–5+) |
| **RAC** | Cạnh tranh tương đối transit vs xe máy | tỉ số (>1 = xe máy nhanh hơn) |
| **SMCI** | Chỉ số khả năng giao thông bền vững | tích (0–1) |
| **Δ SMCI** | SMCI(B) − SMCI(A); dương = cải thiện | (0–1) |

---

**Mã nguồn:** `src/` · **Đề xuất đầy đủ:** `proposal/proposal_v7.md` · **Kết quả pilot:** `outputs/pilot_summary.csv`
**Gói xét duyệt:** `outputs/supervisor_package.md` · **Tự kiểm toán:** `outputs/project_self_audit.md`

**Câu hỏi dự kiến từ giáo sư:**
- *Khác gì mô hình tiếp cận việc làm?* → Đo cạnh tranh phương thức, lấy xe máy (không phải ô tô) làm chuẩn.
- *Có mở rộng được không?* → Có; khung chuyển giao sang mọi thành phố phụ thuộc xe máy. Phương pháp pilot đã được kiểm chứng.
