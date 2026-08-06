# Giải Thích Dễ Hiểu Về Toàn Bộ Metrics

File này là bản giải thích bằng tiếng Việt, để đọc nhanh và dùng khi trình bày với supervisor/reviewer. Nếu cần công thức chính xác và citation đầy đủ, xem `docs/metrics_reference.md`. Nếu hai file lệch nhau, code và `metrics_reference.md` là source of truth.

Dự án đang đo câu hỏi trung tâm:

> Sống ở mỗi ô lưới quanh Ocean Park, nếu không dựa vào xe máy, người dân có thực sự có khả năng tiếp cận tiện ích gần nhà, cơ hội cấp đô thị, và transit có cạnh tranh được với xe máy không?

Nói theo framing rộng hơn: Ocean Park có thể được đọc như một **green megaproject / mega green city** có yếu tố **TOD-like** vì có quy hoạch lớn, tiện ích nội khu, hình ảnh xanh, và VinBus. Nhưng bài này không mặc định rằng "có bus điện" hoặc "có branding xanh" là đã bền vững. Các metrics bên dưới dùng để kiểm tra xem lời hứa đó có thật sự chuyển thành khả năng di chuyển bền vững hay không.

TOD/green city ở đây là **giả thuyết cần kiểm chứng**, không phải kết luận sẵn:

```text
Green/TOD claim -> phải qua 3 kiểm tra:
1. Có tiện ích gần nhà để đi bộ không?          -> NAI
2. Có với được cơ hội cấp đô thị bằng transit không? -> MAI
3. Transit có cạnh tranh được với xe máy không? -> RAC
```

Nếu cả ba cùng mạnh thì mới gọi là `Integrated Capability`. Nếu chỉ có tiện ích nội khu nhưng transit yếu so với xe máy, đó là `Fragmented Capability`, tức green/TOD ở hình thức nhưng mobility capability chưa trọn vẹn.

## Tóm Tắt Một Dòng

| Metric | Hỏi điều gì? | Đọc đơn giản |
|---|---|---|
| `NAI` | Gần nhà có gì để đi bộ tới không? | Local walkability |
| `MAI` | Đi bộ + transit có với được cơ hội lớn của đô thị không? | Metropolitan opportunity access |
| `RAC_time` | Transit có nhanh gần bằng xe máy không? | Time competitiveness |
| `RAC_opp` | Transit với được bao nhiêu cơ hội so với xe máy? | Opportunity competitiveness |
| `RAC` | Transit cạnh tranh với xe máy đến mức nào? | Primary hiện nay = `RAC_time` |
| `MCS` | Sức mạnh metropolitan tổng hợp của một ô | MAI + RAC, dùng cho typology |
| `SMCI` | Khả năng di chuyển bền vững tổng hợp | NAI x MAI x RAC |
| `Delta_SMCI` | VinBus làm tốt hơn hay tệ hơn? | Scenario B - Scenario A |
| `Typology` | Ô này thuộc loại mobility nào? | 4 nhóm: Integrated, Fragmented, Transit-Dependent, Motorcycle Lock-in |

## Bối Cảnh Networks Và Scenarios

Dự án có 4 network:

| Network | Nghĩa là gì? | Dùng để làm gì? |
|---|---|---|
| Network A | Đi bộ | Đo local walking access |
| Network B | Đi bộ + transit hiện hữu trước VinBus | Scenario A baseline |
| Network C | Đi bộ + transit + VinBus | Scenario B intervention |
| Network D | Xe máy | Benchmark cạnh tranh |

Có 2 scenario:

| Scenario | Nghĩa |
|---|---|
| Scenario A | Không có VinBus, chỉ có walking + transit baseline |
| Scenario B | Có VinBus |

`Delta_SMCI = SMCI_B - SMCI_A`.

Nếu `Delta_SMCI > 0`, ô đó tốt lên sau VinBus. Nếu bằng 0, gần như không đổi. Nếu nhỏ hơn 0, điểm giảm nhẹ theo cách tính time-competitiveness.

## 1. NAI Là Gì?

`NAI` = Neighborhood Accessibility Index.

Nói đơn giản:

> NAI đo quanh nhà có bao nhiêu điểm đến hằng ngày có thể đi bộ tới trong 15 phút.

NAI trả lời câu hỏi:

> "Từ ô này, trong tầm đi bộ 15 phút, có bao nhiêu trường, shop, clinic, park, dịch vụ hằng ngày?"

Công thức dễ hiểu:

```text
NAI = số POI nằm trong 1200 m network walk
```

Ngưỡng hiện tại:

```text
1200 m trên mạng đường đi bộ
~ 15 phút nếu đi 80 m/phút
```

Vì sao dùng count, không dùng size?

Ở cấp neighborhood, điều quan trọng là "có hay không có" tiện ích hằng ngày gần nhà. Một cửa hàng nhỏ và một siêu thị lớn đều có thể làm nhiệm vụ "có chỗ mua đồ gần nhà". Vì vậy NAI đếm presence, không weight theo quy mô.

Đọc NAI:

| Giá trị NAI | Nghĩa |
|---:|---|
| 0 | Không có POI được map trong tầm đi bộ 15 phút |
| Thấp | Gần nhà ít tiện ích |
| Cao | Gần nhà nhiều tiện ích hằng ngày |

Kết quả hiện tại:

```text
Mean NAI = 13.47
Zero-NAI = 33 / 462 cells
```

Cảnh báo:

`NAI = 0` không chứng minh ngoài đời không có tiện ích. Nó chỉ nói trong data hiện có, trên walking network và POI layer hiện có, không tìm thấy POI trong ngưỡng 1200 m.

## 2. MAI Là Gì?

`MAI` = Metropolitan Accessibility Index.

Nói đơn giản:

> MAI đo từ mỗi ô, nếu đi bộ + transit, có thể tiếp cận bao nhiêu cơ hội cấp đô thị trong thời gian hợp lý.

MAI khác NAI:

| NAI | MAI |
|---|---|
| Gần nhà có gì không? | Ra ngoài khu nhà có với được cơ hội lớn không? |
| Đi bộ | Đi bộ + transit |
| Đếm POI | Weight theo quy mô cơ hội |
| Daily/local | Metropolitan/regional |

MAI trả lời câu hỏi:

> "Nếu sống ở ô này và không đi xe máy, mình có tiếp cận được việc làm, trường/campus lớn, bệnh viện, thương mại/dịch vụ lớn bằng walk + transit không?"

### MAI Đo Những Nhóm Nào?

MAI gồm 4 domain:

| Domain | Nghĩa | Weight |
|---|---|---:|
| Economic | Việc làm, office, industrial, khu kinh tế | 40% |
| Higher education | Trường/campus/cơ sở giáo dục lớn | 20% |
| Healthcare | Bệnh viện, y tế cấp cao | 20% |
| Commercial/services | Retail, service, park/leisure, thương mại dịch vụ lớn | 20% |

Công thức dễ hiểu:

```text
MAI = 40% economic access
    + 20% education access
    + 20% healthcare access
    + 20% commercial/service access
```

### Mỗi POI Trong MAI Không Bằng Nhau

MAI không coi 1 kiosk = 1 bệnh viện = 1 khu công nghiệp.

Mỗi điểm đến có `magnitude`:

| Loại điểm đến | Magnitude dùng để weight |
|---|---|
| Hospital/clinic | Số giường hoặc sức chứa y tế |
| School/campus | Enrollment/capacity |
| Economic site | Jobs |
| Retail/service | GLA hoặc diện tích dịch vụ |
| Park/leisure | Diện tích polygon/service area |

Ví dụ:

- Bệnh viện 300 giường nặng hơn clinic nhỏ.
- Khu công nghiệp nhiều jobs nặng hơn office nhỏ.
- Mall lớn nặng hơn shop nhỏ.

### MAI Tính Cho Một Ô Như Thế Nào?

Với mỗi cell `i`:

1. Lấy tất cả destination/cơ hội `j`.
2. Tính thời gian đi từ cell `i` tới destination `j` bằng walk + transit.
3. Lấy quy mô của destination đó.
4. Giảm trọng số nếu thời gian đi lại xa.
5. Cộng lại theo 4 domain.

Decay thời gian:

```text
0-30 phút: tính 100%
30-60 phút: giảm dần
>60 phút: tính 0
```

Ví dụ:

```text
Bệnh viện 300 giường
- tới trong 25 phút -> tính full
- tới trong 45 phút -> tính một phần
- tới trong 70 phút -> không tính
```

### Observed Strict MAI Là Gì?

Hiện project dùng `observed_strict`.

Nghĩa là:

> MAI chỉ dùng destination có magnitude có nguồn/audit, hoặc nếu không đo được và không phải destination thật thì exclude.

Không còn cách:

```text
tag=hospital -> tự gán weight mặc định
```

Mỗi included POI cần có:

```text
obs_magnitude
obs_unit
obs_source_tier
obs_confidence
obs_audit_status
```

Nếu không đo được magnitude, POI bị loại khỏi MAI với lý do rõ ràng.

Định nghĩa ngắn gọn để đưa vào paper:

> MAI measures the amount of source-backed metropolitan opportunity reachable from each grid cell by walking and transit, weighting destinations by observed magnitude and discounting them by travel time.

Tiếng Việt:

> MAI đo lượng cơ hội cấp đô thị mà mỗi ô có thể tiếp cận bằng đi bộ và transit, trong đó mỗi điểm đến được weight theo quy mô quan sát được và bị giảm trọng số theo thời gian di chuyển.

## 3. RAC Là Gì?

`RAC` = Relative Accessibility Competitiveness.

Nói đơn giản:

> RAC đo walk + transit có cạnh tranh được với xe máy không.

Tại Hà Nội/Ocean Park, chỉ biết "transit có tồn tại" là chưa đủ. Câu hỏi thật là:

> "Transit có đủ nhanh và đủ hữu ích để người dân không bị khóa vào xe máy không?"

RAC có 2 thành phần logic:

| Metric | Hỏi điều gì? | Trạng thái |
|---|---|---|
| `RAC_time` | Transit có nhanh gần bằng xe máy không? | Primary |
| `RAC_opp` | Transit với được bao nhiêu cơ hội so với xe máy? | Diagnostic/legacy robustness |

## 4. RAC_time Là Gì?

Nói đơn giản:

> RAC_time so sánh thời gian đi bằng xe máy với thời gian đi bằng walk + transit tới cùng một tập cơ hội.

Công thức ý tưởng:

```text
RAC_time = motorcycle mean time / walk-transit mean time
```

Nếu transit chậm hơn xe máy nhiều, RAC_time thấp.

Nếu transit gần bằng xe máy, RAC_time cao.

Đọc dễ hiểu:

| RAC_time | Nghĩa |
|---:|---|
| Gần 0 | Transit rất kém cạnh tranh về thời gian |
| Trung bình | Transit có ích nhưng vẫn thua xe máy |
| Cao | Transit bắt đầu cạnh tranh với xe máy |

Hiện nay primary `RAC = RAC_time`, vì nó reviewer-safe hơn. Lý do: `RAC_opp` dùng lại MAI_transit nên dễ gây collinearity với MAI.

## 5. RAC_opp Là Gì?

Nói đơn giản:

> RAC_opp so sánh lượng cơ hội mà transit với được với lượng cơ hội mà xe máy với được.

Công thức ý tưởng:

```text
RAC_opp = MAI_transit / MAI_motorcycle
```

Nếu `RAC_opp` cao, transit với được gần nhiều cơ hội như xe máy.

Nếu thấp, xe máy vẫn vượt trội về opportunity reach.

Tại sao không dùng làm primary?

Vì `RAC_opp` có `MAI_transit` ở tử số. Trong khi SMCI đã có MAI. Nếu đưa `RAC_opp` vào primary, MAI bị lặp lại trong cả MAI và RAC, làm VIF cao. Vì vậy nó được giữ làm robustness/diagnostic.

## 6. RAC_full Là Gì?

`RAC_full` là công thức RAC cũ/legacy:

```text
RAC_full = sqrt(RAC_time * RAC_opp)
```

Ý tưởng:

> Transit phải vừa nhanh vừa với được cơ hội thì mới thật sự cạnh tranh.

Nhưng vì VIF cao, bản primary hiện nay không dùng `RAC_full`. Nó vẫn được giữ để so sánh robustness:

```text
RAC_full_A
RAC_full_B
SMCI_B_full_rac_legacy
```

Kết quả audit:

```text
Legacy full-RAC max VIF = 10.04
Primary RAC_time max VIF = 3.82
Kappa = 0.9116
28 / 462 cells relabelled
```

Nghĩa là đổi sang RAC_time làm primary giảm collinearity mạnh, nhưng typology vẫn gần như giữ nguyên.

## 7. MCS Là Gì?

`MCS` = Metropolitan Competitiveness Score.

Nói đơn giản:

> MCS gom MAI và RAC lại thành một trục "sức mạnh metropolitan".

Công thức:

```text
MCS = sqrt(MAI_norm * RAC_norm)
```

MCS không phải headline result. Nó chỉ dùng để chia typology.

Tại sao cần MCS?

Typology cần 2 trục:

```text
Trục 1: NAI = local neighborhood access
Trục 2: MCS = metropolitan opportunity + competitiveness
```

Nếu không gom MAI và RAC thành MCS, typology sẽ khó đọc hơn.

## 8. SMCI Là Gì?

`SMCI` = Sustainable Mobility Capability Index.

Nói đơn giản:

> SMCI đo một ô có đồng thời 3 điều kiện của mobility capability hay không: gần nhà có tiện ích, ra được cơ hội cấp đô thị, và transit có cạnh tranh với xe máy.

Công thức:

```text
SMCI = NAI_norm * MAI_norm * RAC_norm
```

Đọc bằng ngôn ngữ đời thường:

```text
SMCI = local access
     x metropolitan access
     x transit competitiveness
```

Đây là weakest-link index. Nghĩa là chỉ cần một thành phần gần 0, SMCI sẽ gần 0.

Ví dụ:

| NAI | MAI | RAC | Kết quả |
|---|---|---|---|
| Cao | Cao | Cao | SMCI cao |
| Cao | Cao | Thấp | Vẫn bị fragment vì transit không cạnh tranh xe máy |
| Cao | Thấp | Cao | Gần nhà tốt nhưng không với được cơ hội đô thị |
| Thấp | Cao | Cao | Có transit/metropolitan access nhưng local access yếu |
| Thấp | Thấp | Thấp | Motorcycle Lock-in |

Kết quả hiện tại:

```text
Mean SMCI_A = 0.0091
Mean SMCI_B = 0.0168
Mean Delta = 0.0077
```

SMCI_B lớn hơn SMCI_A nghĩa là Scenario B có VinBus tốt hơn trung bình.

## 9. Delta_SMCI Là Gì?

`Delta_SMCI` đo thay đổi sau VinBus:

```text
Delta_SMCI = SMCI_B - SMCI_A
```

Đọc dễ hiểu:

| Delta_SMCI | Nghĩa |
|---:|---|
| > 0 | Ô đó tốt lên sau VinBus |
| = 0 | Không đổi rõ |
| < 0 | Giảm nhẹ theo cách tính competitiveness |

Kết quả hiện tại:

```text
Improved = 297 / 462 cells
Unchanged = 33 / 462 cells
Declined = 132 / 462 cells
```

Quan trọng: declined không nhất thiết là "VinBus làm tệ đi ngoài đời". Nó có thể xảy ra vì RAC_time tính opportunity-weighted mean time: khi transit mở thêm cơ hội xa/chậm hơn motorcycle, average time competitiveness có thể giảm nhẹ.

## 10. Typology Là Gì?

Typology chia mỗi cell vào 1 trong 4 nhóm bằng 2 trục:

```text
Trục 1: NAI cao hay thấp?
Trục 2: MCS cao hay thấp?
```

Bảng 4 nhóm:

| NAI | MCS | Typology | Nghĩa dễ hiểu |
|---|---|---|---|
| Cao | Cao | Integrated Capability | Gần nhà tốt, metropolitan/transit cũng tốt |
| Cao | Thấp | Fragmented Capability | Gần nhà có tiện ích nhưng không kết nối tốt với cơ hội đô thị |
| Thấp | Cao | Transit-Dependent | Local yếu nhưng metropolitan/transit khá |
| Thấp | Thấp | Motorcycle Lock-in | Cả local và sustainable metropolitan access đều yếu |

Kết quả Scenario B hiện tại:

```text
Integrated Capability = 172 cells
Fragmented Capability = 59 cells
Transit-Dependent = 59 cells
Motorcycle Lock-in = 172 cells
```

Lưu ý:

Typology dùng rank-based median split, nên số cell hai phía high/low được cân bằng theo thiết kế. Đừng đọc typology như "natural cluster" tự động. Hãy đọc nó như khung lý thuyết 2x2 để diễn giải không gian.

## 11. Normalization Là Gì?

Nhiều metric có đơn vị khác nhau:

- NAI = count
- MAI = weighted opportunity score
- RAC = ratio/time competitiveness

Trước khi nhân với nhau, chúng được chuẩn hóa về 0-1:

```text
norm = (x - min) / (max - min)
```

Trong Scenario A/B, project dùng shared normalization bounds. Nghĩa là A và B dùng chung thang đo, để `Delta_SMCI` thật sự là thay đổi giữa hai scenario, không phải do đổi thang đo.

## 12. SMCI_additive Là Gì?

`SMCI_additive` là robustness check:

```text
SMCI_additive = (NAI_norm + MAI_norm + RAC_norm) / 3
```

Nó cho phép điểm mạnh bù điểm yếu. Khác với SMCI primary, là weakest-link.

Tại sao không dùng geometric mean để robustness?

Vì:

```text
(NAI * MAI * RAC)^(1/3)
```

chỉ là biến đổi monotonic của product. Rank sẽ gần như y hệt, nên không test được gì mới. Additive mới là contrast thật.

## 13. VIF Là Gì?

`VIF` = Variance Inflation Factor.

Nói đơn giản:

> VIF kiểm tra các biến có bị trùng lặp quá nhiều không.

Trong project này, rủi ro lớn là MAI và RAC bị lặp, vì RAC_opp có MAI_transit bên trong.

Ngưỡng:

```text
VIF > 5 = cảnh báo
```

Kết quả hiện tại:

```text
Primary RAC_time:
VIF(MAI) = 3.82
VIF(RAC) = 1.92
=> OK

Legacy full-RAC:
VIF(MAI) = 10.04
VIF(RAC) = 9.89
=> high
```

Vì vậy primary dùng RAC_time.

## 14. Kappa Và Spearman Là Gì?

Hai metric này dùng để xem đổi công thức có làm kết quả đảo lớn không.

`Cohen's kappa`:

> Đo mức độ typology labels giống nhau giữa hai specification.

`Spearman rho`:

> Đo ranking SMCI có giữ gần giống nhau không.

Kết quả RAC_time vs full-RAC:

```text
Kappa = 0.9116
Spearman rho = 0.9824
Relabelled = 28 / 462 cells
```

Nghĩa là đổi sang RAC_time làm primary giảm VIF nhưng không phá kết quả chính.

## 15. Population-Weighted SMCI Là Gì?

Đây là sensitivity/equity check, không phải formula primary.

Nói đơn giản:

> Thay vì tính trung bình mỗi cell bằng nhau, ta tính trung bình theo dân số trong cell.

Hỏi:

> "Kết quả trung bình có đại diện cho nơi có nhiều người sống không?"

Kết quả hiện tại:

```text
Mean SMCI_B unweighted = 0.0168
Mean SMCI_B population-weighted = 0.0157
Bias = -6.5%
```

Nghĩa là khu đông dân có SMCI_B hơi thấp hơn trung bình cell, nhưng chênh lệch không quá lớn.

## 16. Zero-Access Audit Là Gì?

Zero-access audit kiểm tra:

> Ô có NAI = 0 có phải chỉ là hồ/park/open space không?

Dùng building footprints + population để kiểm tra.

Kết quả hiện tại:

```text
Zero-NAI cells = 33 / 462
Zero-SMCI_B cells = 34 / 462
Built zero-NAI cells = 30
Population in built zero-NAI cells ~ 3,466
```

Nghĩa là zero-access không thể bị bỏ qua như lỗi hồ/không gian mở. Nhưng sau khi đổi sang 15 phút/1200m, zero-access đã giảm nhiều so với ngưỡng 800m cũ.

## 17. Đọc Dashboard/Map Như Thế Nào?

Nếu xem interactive map:

| Layer | Cách đọc |
|---|---|
| NAI | Màu nóng/cao = nhiều POI gần nhà hơn |
| MAI_B | Màu cao = tiếp cận được nhiều cơ hội metropolitan hơn sau VinBus |
| RAC_B | Màu cao = walk+transit cạnh tranh với xe máy tốt hơn |
| SMCI_B | Màu cao = tổng hợp capability tốt hơn |
| Delta_SMCI | Dương/cao = VinBus làm tốt lên; âm/thấp = điểm giảm |
| Typology | 4 nhóm mobility capability |

## 18. Một Cách Nhớ Toàn Bộ Framework

Có thể nhớ bằng 3 câu hỏi:

```text
NAI: Gần nhà có gì không?
MAI: Đi transit có với được cơ hội lớn không?
RAC: Transit có cạnh tranh được với xe máy không?
```

Và headline:

```text
SMCI = NAI x MAI x RAC
```

Nếu cả 3 cùng tốt -> Integrated Capability.

Nếu NAI tốt nhưng MAI/RAC yếu -> Fragmented Capability.

Nếu NAI yếu nhưng MAI/RAC tốt -> Transit-Dependent.

Nếu cả 2 trục đều yếu -> Motorcycle Lock-in.

## 19. Số Hiện Tại Nên Nhớ

| Chỉ số | Giá trị hiện tại |
|---|---:|
| Grid cells | 462 |
| POIs | 208 |
| Included MAI destinations | 201 |
| Excluded non-destination/service points | 7 |
| Mean NAI | 13.47 |
| Zero-NAI cells | 33 |
| Mean SMCI_A | 0.0091 |
| Mean SMCI_B | 0.0168 |
| Mean Delta_SMCI | 0.0077 |
| Improved cells | 297 / 462 |
| Unchanged cells | 33 / 462 |
| Declined cells | 132 / 462 |
| Integrated Capability | 172 |
| Fragmented Capability | 59 |
| Transit-Dependent | 59 |
| Motorcycle Lock-in | 172 |
| Primary VIF(MAI/RAC) | 3.82 / 1.92 |
| Legacy full-RAC VIF(MAI/RAC) | 10.04 / 9.89 |

## 20. Cách Nói Ngắn Gọn Trong Paper/Presentation

Bản tiếng Anh:

> The framework separates local walkability (NAI), metropolitan opportunity accessibility by walking and transit (MAI), and transit competitiveness relative to motorcycles (RAC). SMCI multiplies the normalized components to identify cells where all three dimensions are simultaneously present.

Bản tiếng Việt:

> Khung đo tách riêng khả năng đi bộ gần nhà (NAI), khả năng tiếp cận cơ hội cấp đô thị bằng đi bộ và transit (MAI), và mức độ transit cạnh tranh với xe máy (RAC). SMCI nhân ba thành phần đã chuẩn hóa để xác định nơi nào có đầy đủ cả ba điều kiện của mobility capability.

## 21. Ví Dụ Tính Cụ Thể Cho Một Ô

Ví dụ này lấy trực tiếp từ `data/processed/pilot_metrics.csv`, ô `cell_id = 456`.

Mục tiêu là thấy toàn bộ pipeline đi từ số thô đến `NAI`, `MAI`, `RAC`, `MCS`, `SMCI`, `Delta_SMCI`, và `typology`.

### 21.1. Dữ Liệu Thô Của Ô 456

```text
cell_id = 456

NAI = 9

MAI_A = 22.405661
MAI_B = 22.405661

moto_mean_opp_time_min = 6.6658
wt_A_mean_opp_time_min = 38.7165
wt_B_mean_opp_time_min = 24.9458

RAC_opp_A_raw = 0.536646
RAC_opp_B_raw = 0.536646
```

Đọc nhanh:

- `NAI = 9`: trong tầm đi bộ 15 phút / 1200 m, ô này có 9 POI neighborhood.
- `MAI_A = MAI_B`: VinBus không làm tăng tổng lượng opportunity reachable của ô này.
- `wt_B_mean_opp_time_min` thấp hơn `wt_A_mean_opp_time_min`: sau VinBus, thời gian walk+transit tới cùng tập opportunity nhanh hơn.

### 21.2. Tính NAI_norm

Trong toàn bộ pilot:

```text
NAI_min = 0
NAI_max = 54
```

Chuẩn hóa min-max:

```text
NAI_norm = (NAI - NAI_min) / (NAI_max - NAI_min)
         = (9 - 0) / (54 - 0)
         = 0.166667
```

Nghĩa là ô này có local neighborhood access thấp hơn nhiều ô khác trong pilot.

### 21.3. Tính MAI_norm

Scenario A/B dùng shared normalization bounds, tức cùng một min/max cho cả A và B.

```text
MAI_min_shared = 4.393315
MAI_max_shared = 36.540771
```

Scenario A:

```text
MAI_A_norm = (MAI_A - MAI_min_shared) / (MAI_max_shared - MAI_min_shared)
           = (22.405661 - 4.393315) / (36.540771 - 4.393315)
           = 0.560304
```

Scenario B:

```text
MAI_B_norm = (MAI_B - MAI_min_shared) / (MAI_max_shared - MAI_min_shared)
           = (22.405661 - 4.393315) / (36.540771 - 4.393315)
           = 0.560304
```

Vì `MAI_A = MAI_B`, nên `MAI_A_norm = MAI_B_norm`.

### 21.4. Tính RAC_time_raw

Primary `RAC` hiện nay là `RAC_time`.

Công thức raw:

```text
RAC_time_raw = motorcycle opportunity-weighted mean time
             / walk-transit opportunity-weighted mean time
```

Scenario A:

```text
RAC_time_A_raw = 6.6658 / 38.7165
               = 0.172170
```

Scenario B:

```text
RAC_time_B_raw = 6.6658 / 24.9458
               = 0.267213
```

Đọc dễ hiểu:

- Scenario A: walk+transit mất khoảng `38.7` phút, xe máy mất `6.7` phút -> transit rất kém cạnh tranh.
- Scenario B: walk+transit giảm còn `24.9` phút -> transit vẫn chậm hơn xe máy, nhưng cạnh tranh hơn Scenario A.

### 21.5. Tính RAC_time Normalized

Shared bounds cho `RAC_time_raw` trong cả Scenario A/B:

```text
RAC_time_raw_min_shared = 0.092086
RAC_time_raw_max_shared = 2.038509
```

Scenario A:

```text
RAC_time_A = (0.172170 - 0.092086) / (2.038509 - 0.092086)
           = 0.041145
```

Scenario B:

```text
RAC_time_B = (0.267213 - 0.092086) / (2.038509 - 0.092086)
           = 0.089974
```

Vì primary `RAC = RAC_time`, nên:

```text
RAC_A = 0.041145
RAC_B = 0.089974
```

Trong file, hai cột `RAC_A_norm` và `RAC_B_norm` cũng bằng chính hai giá trị này:

```text
RAC_A_norm = 0.041145
RAC_B_norm = 0.089974
```

### 21.6. RAC_opp Và RAC_full Của Ô Này

`RAC_opp` không phải primary, nhưng vẫn được giữ để audit/legacy robustness.

Raw:

```text
RAC_opp_A_raw = 0.536646
RAC_opp_B_raw = 0.536646
```

Sau min-max normalization:

```text
RAC_opp_A = 0.560304
RAC_opp_B = 0.560304
```

Legacy `RAC_full`:

```text
RAC_full = sqrt(RAC_time * RAC_opp)
```

Scenario A:

```text
RAC_full_A = sqrt(0.041145 * 0.560304)
           = 0.151834
```

Scenario B:

```text
RAC_full_B = sqrt(0.089974 * 0.560304)
           = 0.224528
```

Lưu ý: `RAC_full` không còn là primary. Primary hiện nay dùng:

```text
RAC_A = RAC_time_A
RAC_B = RAC_time_B
```

### 21.7. Tính MCS

`MCS` dùng để chia typology, không phải headline metric.

Công thức:

```text
MCS = sqrt(MAI_norm * RAC_norm)
```

Scenario A:

```text
MCS_A = sqrt(0.560304 * 0.041145)
      = 0.151834
```

Scenario B:

```text
MCS_B = sqrt(0.560304 * 0.089974)
      = 0.224528
```

Đọc nhanh: `MCS_B > MCS_A`, tức sau VinBus trục metropolitan competitiveness của ô này tốt hơn.

### 21.8. Tính SMCI

Công thức primary:

```text
SMCI = NAI_norm * MAI_norm * RAC_norm
```

Scenario A:

```text
SMCI_A = 0.166667 * 0.560304 * 0.041145
       = 0.003842
```

Scenario B:

```text
SMCI_B = 0.166667 * 0.560304 * 0.089974
       = 0.008402
```

Đọc nhanh: SMCI tăng vì `RAC` tăng. `NAI` và `MAI` không đổi trong ví dụ này.

### 21.9. Tính Delta_SMCI

```text
Delta_SMCI = SMCI_B - SMCI_A
           = 0.008402 - 0.003842
           = 0.004560
```

Vì `Delta_SMCI > 0`, ô 456 được tính là cải thiện sau VinBus.

### 21.10. Typology Của Ô 456

Typology dùng rank-based median split:

```text
Trục 1: NAI high/low
Trục 2: MCS high/low
```

Với `cell_id = 456`:

```text
NAI rank = low
MCS_A rank = low
MCS_B rank = high
```

Nên:

```text
typology_A = Motorcycle Lock-in
typology_B = Transit-Dependent
```

Diễn giải:

> Trước VinBus, ô này vừa yếu về tiện ích gần nhà vừa yếu về metropolitan competitiveness, nên là `Motorcycle Lock-in`. Sau VinBus, local access vẫn thấp, nhưng metropolitan competitiveness vượt lên phía high, nên ô chuyển thành `Transit-Dependent`.

Nói đời thường:

> Ô này vẫn thiếu tiện ích gần nhà, nhưng VinBus làm khả năng đi ra các cơ hội cấp đô thị bằng walk+transit tốt hơn rõ rệt. Vì vậy nó chưa thành `Integrated Capability`, nhưng đã thoát khỏi nhóm khóa chặt vào xe máy.

## 22. Thời Gian Di Chuyển Có Đáng Tin Không?

Câu trả lời ngắn:

> Có, đủ đáng tin để so sánh accessibility tương đối giữa các ô lưới. Nhưng không nên đọc nó như thời gian GPS/real-time chính xác tuyệt đối cho từng chuyến đi.

Cách gọi chuẩn:

```text
network-based estimated travel time
```

Tiếng Việt:

```text
thời gian di chuyển ước tính theo mô hình mạng
```

Không nên gọi đơn giản là "thời gian thật" hoặc "ground truth".

### 22.1. Vì Sao Cách Tính Này Đáng Tin?

Vì thời gian không được bịa thủ công. Nó được tính từ các lớp dữ liệu và giả định có kiểm soát:

| Thành phần | Cách tính | Mức tin cậy |
|---|---|---|
| Đi bộ | Shortest path trên OSM walking network, theo tốc độ đi bộ | Tốt cho so sánh không gian |
| Xe máy | Shortest path trên OSM driving network, dùng tốc độ xe máy đã hiệu chỉnh | Tốt cho benchmark tương đối |
| Transit baseline | Hanoi GTFS 2018 pre-VinBus, dùng làm Scenario A | Hợp lý cho baseline, không phải current service |
| VinBus | Pseudo-GTFS đã QC, stop routing, wait time, linehaul, walk access/egress | Tốt hơn corridor proxy, nhưng không phải official GTFS |
| Validation | 10 OD pairs Google Maps Android motorcycle | MAE = 1.90 phút |

Cách hiểu:

```text
Không phải: đo GPS mọi chuyến đi thật
Mà là: mô hình hóa thời gian đi lại trên mạng đường và transit data
```

### 22.2. Motorcycle Time Được Kiểm Tra Như Thế Nào?

Xe máy là benchmark quan trọng nhất vì Hà Nội/Ocean Park là bối cảnh phụ thuộc xe máy.

Project không dùng raw OSM car speed. Network D dùng tốc độ xe máy đã hiệu chỉnh theo literature, sau đó kiểm tra chéo bằng Google Maps Android motorcycle/two-wheeler mode.

Kết quả validation hiện tại:

```text
Sample = 10 OD pairs
MAE = 1.90 phút
MAPE = 22.17%
MBE = -1.04 phút
RMSE = 2.20 phút
Verdict = PASS, vì MAE < 3.0 phút
```

Đọc dễ hiểu:

- `MAE = 1.90 phút`: trung bình mô hình lệch khoảng 1.9 phút so với Google Maps motorcycle.
- `MBE = -1.04 phút`: mô hình hơi optimistic, tức thường nhanh hơn Google Maps khoảng 1 phút.
- Sai số này chấp nhận được cho accessibility comparison, vì mục tiêu là so sánh tương đối giữa cell, không dự báo chính xác từng chuyến đi.

### 22.3. Transit Time Được Tính Như Thế Nào?

Transit time là tổng của nhiều thành phần:

```text
walk access to stop
+ waiting time
+ bus linehaul time
+ walk egress to destination
```

Với VinBus, project dùng pseudo-GTFS:

```text
176 routes
5,631 stops
headway 5-48 phút
median headway 15 phút
```

Với Scenario A, project dùng Hanoi GTFS 2018 như pre-VinBus baseline. Đây là lựa chọn phương pháp luận: baseline trước khi VinBus xuất hiện, không phải dữ liệu current-service.

### 22.4. Giới Hạn Cần Nói Rõ

Cách tính này đáng tin cho research model, nhưng có giới hạn:

- Không có GPS observed trips hàng loạt cho mọi OD pair.
- Google Maps check mới có 10 OD pairs, dùng để spot-check, không phải full validation.
- VinBus là pseudo-GTFS, chưa phải official GTFS.
- Network B là GTFS 2018 pre-VinBus, không đại diện hoàn toàn cho dịch vụ bus hiện tại.
- Traffic theo giờ/ngày chưa được mô hình hóa đầy đủ.

Vì vậy, kết luận đúng là:

```text
Reliable enough for comparative accessibility analysis,
not for exact trip-time prediction.
```

Tiếng Việt:

```text
Đủ đáng tin để so sánh accessibility tương đối,
không phải để dự báo chính xác tuyệt đối thời gian từng chuyến đi.
```

### 22.5. Câu Nên Nói Khi Trình Bày

Bản tiếng Anh:

> Travel times are network-based model estimates, not observed trip durations for every OD pair. They are defensible for comparative accessibility analysis because they use OSM network routing, calibrated motorcycle speeds, GTFS/pseudo-GTFS transit inputs, and external motorcycle spot-checks against Google Maps Android two-wheeler mode.

Bản tiếng Việt:

> Thời gian di chuyển trong nghiên cứu là thời gian ước tính theo mô hình mạng, không phải thời gian quan sát GPS cho mọi cặp OD. Cách tính này đủ đáng tin để so sánh accessibility tương đối giữa các ô lưới, vì dựa trên routing theo mạng OSM, tốc độ xe máy đã hiệu chỉnh, GTFS/pseudo-GTFS cho transit, và kiểm tra chéo bằng Google Maps Android motorcycle mode.
