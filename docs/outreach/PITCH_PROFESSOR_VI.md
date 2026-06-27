# Pitch gửi Professor

## Khả năng giao thông bền vững bị phân mảnh trong megaproject “xanh” phụ thuộc xe máy
### Khung tiếp cận hai tầng và cạnh tranh phương thức — trường hợp Vinhomes Ocean Park, Hà Nội

**Mục tiêu:** thuyết phục professor rằng đề tài không chỉ là “đo accessibility ở Ocean Park”, mà là một đóng góp phương pháp có khoảng trống rõ trong literature.

**Tạp chí mục tiêu:** *Journal of Transport Geography*  
**Trạng thái:** pilot đã chạy end-to-end; phương pháp có dữ liệu, code, kiểm định, bản đồ, robustness.

---

## 1. Vấn đề nghiên cứu

Các megaproject “xanh” ở Việt Nam thường được đánh giá bằng ba dấu hiệu dễ nhìn thấy:

1. Có tiện ích nội khu: trường học, cửa hàng, công viên, phòng khám.
2. Có hình ảnh môi trường: hồ, cây xanh, xe buýt điện.
3. Có kết nối giao thông công cộng: VinBus hoặc bus thường.

Nhưng ba điều này **không chứng minh** rằng cư dân có khả năng di chuyển bền vững trong đời sống hàng ngày.

Lý do: ở Hà Nội, phương thức cạnh tranh thực sự của transit không phải ô tô, mà là **xe máy**. Xe máy nhanh, linh hoạt, len lỏi được trong đô thị đông, và ăn sâu vào thói quen đi lại. Một tuyến bus có thể “tồn tại”, nhưng nếu đi bus + đi bộ vẫn chậm hơn nhiều so với xe máy, cư dân vẫn sẽ phụ thuộc xe máy.

Vì vậy, câu hỏi trung tâm là:

> **Một khu đô thị được quảng bá là xanh có thật sự tạo ra khả năng giao thông bền vững không, nếu cư dân vẫn phải dùng xe máy để tiếp cận cơ hội đô thị?**

Trường hợp Vinhomes Ocean Park phù hợp vì nó có đầy đủ nghịch lý này: quy hoạch mới, thương hiệu xanh, tiện ích nội khu, VinBus điện, nhưng vẫn nằm trong môi trường giao thông Hà Nội phụ thuộc xe máy.

---

## 2. Khoảng trống trong literature

Literature hiện có đo accessibility rất mạnh, nhưng thường rơi vào một trong bốn nhóm. Mỗi nhóm giải quyết một phần vấn đề, nhưng chưa giải quyết đúng bài toán của thành phố phụ thuộc xe máy.

| Nhóm literature | Cách đo chính | Đóng góp | Giới hạn với bài toán này |
|---|---|---|---|
| **Walkability / 15-minute city** | Đo tiện ích gần nhà, có thể đi bộ tới | Cho biết khu phố có “đầy đủ” hay không | Quá cục bộ; không biết cư dân có tiếp cận được việc làm, bệnh viện, đại học ở quy mô đô thị không |
| **Cumulative / gravity accessibility** | Đếm cơ hội đô thị reachable trong ngưỡng thời gian hoặc theo hàm suy giảm | Đo tiếp cận cơ hội tốt hơn chỉ nhìn khoảng cách | Thường gộp thành một bề mặt accessibility; dễ che giấu khác biệt giữa “nội khu tốt” và “kết nối đô thị yếu” |
| **Transit-vs-car competitiveness** | So sánh thời gian hoặc cơ hội bằng transit với ô tô | Đưa yếu tố cạnh tranh phương thức vào accessibility | Benchmark là ô tô; không phù hợp Hà Nội, nơi xe máy mới là đối thủ thực tế |
| **Green megaproject / new town evaluation** | Đánh giá thiết kế, hạ tầng, hình ảnh xanh, đôi khi TOD | Phù hợp bối cảnh megaproject | Thường không kiểm tra liệu transit có cạnh tranh được với phương thức cư dân thật sự dùng hay không |

Nói ngắn gọn: literature hiện có trả lời từng câu hỏi riêng:

- “Có tiện ích gần không?”
- “Có tiếp cận được cơ hội đô thị không?”
- “Transit có tốt hơn ô tô không?”
- “Dự án có hạ tầng xanh không?”

Nhưng nghiên cứu này hỏi một câu khác:

> **Đi bộ + transit có tạo thành một lựa chọn đủ mạnh để thay thế xe máy trong megaproject xanh không?**

Đó là khoảng trống phương pháp.

---

## 3. Giải pháp đề xuất: khung hai tầng + cạnh tranh xe máy

Nghiên cứu đề xuất một framework gồm ba thành phần chính, sau đó kết hợp thành một chỉ số tổng hợp.

### 3.1 NAI — Neighborhood Accessibility Index

**Câu hỏi:** cư dân có đi bộ tới được tiện ích hàng ngày không?

NAI đo số POI có thể tiếp cận bằng mạng đi bộ từ từng ô lưới. Đây là tầng **local / neighborhood**.

Ý nghĩa: một khu đô thị xanh trước hết phải có tiện ích gần nhà. Nhưng NAI chỉ nói về quy mô khu phố, chưa nói về kết nối toàn đô thị.

---

### 3.2 MAI — Metropolitan Accessibility Index

**Câu hỏi:** cư dân có tiếp cận được cơ hội quy mô đô thị bằng đi bộ + transit không?

MAI đo cơ hội trong bốn nhóm:

- kinh tế / thương mại,
- giáo dục,
- y tế,
- dịch vụ đô thị.

Cơ hội được tính bằng hàm suy giảm thời gian: full value nếu ≤30 phút, giảm tuyến tính từ 30–60 phút, bằng 0 nếu >60 phút.

Ý nghĩa: một khu có thể có nhiều tiện ích nội khu nhưng vẫn yếu nếu không tiếp cận được trung tâm việc làm, bệnh viện, đại học, dịch vụ lớn.

---

### 3.3 RAC — Relative Accessibility Competitiveness

**Câu hỏi then chốt:** đi bộ + transit có cạnh tranh được với xe máy không?

RAC gồm hai phần:

```text
RAC_time = motorcycle_travel_time / walk_transit_travel_time
RAC_opp  = MAI_transit / MAI_motorcycle
RAC      = sqrt(RAC_time × RAC_opp)
```

Điểm mới nằm ở benchmark: **xe máy**, không phải ô tô.

Điều này quan trọng vì trong bối cảnh Hà Nội, một hệ thống transit chỉ có ý nghĩa hành vi nếu nó đủ cạnh tranh với lựa chọn mặc định của cư dân: xe máy.

---

### 3.4 SMCI — Sustainable Mobility Capability Index

Ba thành phần được kết hợp thành chỉ số tổng hợp:

```text
SMCI = NAI_norm × MAI_norm × RAC_norm
```

Dùng phép nhân vì đây là logic “weakest link”:

- nếu local access yếu → không bền vững;
- nếu metropolitan access yếu → không bền vững;
- nếu transit không cạnh tranh xe máy → không bền vững.

Một khu chỉ có capability cao khi **cả ba điều kiện cùng tồn tại**.

---

## 4. Bốn typology dễ diễn giải cho quy hoạch

Thay vì chỉ tạo một score khó đọc, framework tạo bốn loại không gian:

| Typology | Điều kiện | Diễn giải |
|---|---|---|
| **Integrated Capability** | NAI cao + MCS cao | Cục bộ tốt, kết nối đô thị tốt, transit cạnh tranh |
| **Fragmented Capability** | NAI cao + MCS thấp | Nội khu tốt nhưng kết nối đô thị bền vững yếu |
| **Transit-Dependent** | NAI thấp + MCS cao | Phụ thuộc transit vì nội khu thiếu tiện ích |
| **Motorcycle Lock-in** | NAI thấp + MCS thấp | Bị khóa vào xe máy; cả local và metro đều yếu |

Trong đó MCS = geometric mean của MAI và RAC.

Điểm mạnh: typology này **theory-first**, không phải clustering tùy ý. Nó trực tiếp trả lời câu hỏi quy hoạch: khu nào cần thêm tiện ích local, khu nào cần nâng transit, khu nào bị lock-in.

---

## 5. So sánh trực tiếp với các hướng nghiên cứu trước

Phần này nên trình bày với professor như một **positioning table**: mỗi dòng literature đã làm được gì, còn thiếu gì, và framework này thêm gì.

### 5.1 Bảng so sánh nhanh

| Dòng nghiên cứu | Paper tiêu biểu | Method chính | Paper đo được gì | Khoảng trống còn lại | Framework này thêm gì |
|---|---|---|---|---|---|
| **Accessibility theory** | Hansen (1959); Handy & Niemeier (1997); Geurs & van Wee (2004) | Potential / cumulative / gravity accessibility | Cơ hội reachable theo không gian-thời gian | Không tách rõ local walkability và metropolitan transit capability trong cùng một typology; không xét đối thủ xe máy | Tách **NAI** và **MAI**, rồi thêm **RAC** để đo cạnh tranh phương thức |
| **15-minute city / walkability** | Moreno et al. (2021); Pozoukidou & Chatziyiannaki (2021) | Tiếp cận dịch vụ hàng ngày trong bán kính/thời gian ngắn | Local completeness, tiện ích gần nhà | Có thể bỏ qua metropolitan opportunity: việc làm, đại học, bệnh viện lớn | Giữ local layer qua **NAI**, nhưng không cho local access thay thế metro access |
| **Transit-vs-car competitiveness** | Liao et al. (2020) | So sánh travel time giữa car và transit trên nhiều đô thị | Transit disadvantage so với ô tô; bất bình đẳng theo không gian-thời gian | Benchmark là **car**, không phải motorcycle; không phù hợp hoàn toàn với Hà Nội | Đổi benchmark sang **motorcycle** qua Network D và RAC |
| **Transport equity / accessibility planning indicators** | Boisjoly & El-Geneidy (2017); Pereira et al. (2017) | Accessibility indicators, equity/distributive justice framing | Accessibility dùng để đánh giá công bằng giao thông | Thường chưa gắn vào bài toán megaproject xanh phụ thuộc xe máy | Dùng SMCI + typology để chỉ ra nhóm **Motorcycle Lock-in** và population exposure |
| **Motorcycle-dependent cities** | Khuat (2006); Vu Anh Tuan (2015); Nguyen & Nguyen (2018); JICA HAIDEP (2010) | Mode choice, traffic management, speed/operation calibration | Vì sao xe máy thống trị; tốc độ/đặc điểm vận hành xe máy ở Hà Nội | Chưa chuyển motorcycle dominance thành một **accessibility competitiveness index** ở cấp ô lưới | Dùng literature này để xây Network D và tính **transit-vs-motorcycle RAC** |
| **Green megaproject / new town sustainability** | Literature về eco-city/new town/megaproject cần bổ sung thêm nguồn chuyên biệt trước khi submit | Đánh giá thiết kế xanh, hạ tầng, TOD, branding | Dự án có yếu tố xanh/hạ tầng transit hay không | Có bus điện/green branding không chứng minh cư dân có sustainable mobility capability | Đánh giá “green” bằng outcome: local access + metro access + mode competitiveness |

---

### 5.2 So với 15-minute city / walkability

Moreno et al. (2021) đưa ra khái niệm 15-minute city: cư dân nên tiếp cận các chức năng thiết yếu trong khoảng thời gian ngắn quanh nơi ở. Pozoukidou & Chatziyiannaki (2021) cũng phân tích 15-minute city như một mô hình quy hoạch dựa trên proximity, mixed-use và local service access.

Đây là nền tảng trực tiếp cho **NAI**: Ocean Park cần được kiểm tra xem cư dân có đi bộ tới trường, shop, phòng khám, công viên không.

Nhưng 15-minute city không đủ cho case này. Một megaproject ngoại vi có thể “đủ tiện ích nội khu” nhưng vẫn yếu nếu cư dân phải đi xa để tiếp cận việc làm, đại học, bệnh viện tuyến cao, hoặc trung tâm đô thị. Vì vậy, nếu chỉ dùng walkability/15-minute framing, ta dễ kết luận quá sớm rằng Ocean Park “xanh” hoặc “tốt”.

**Nghiên cứu này bổ sung:** NAI chỉ là tầng local. Tầng metropolitan được đo riêng bằng **MAI**, và câu hỏi mode choice được đo bằng **RAC**.

---

### 5.3 So với cumulative / gravity accessibility

Hansen (1959) đặt nền móng cho accessibility như quan hệ giữa cơ hội và trở kháng không gian. Handy & Niemeier (1997) hệ thống hóa các lựa chọn đo accessibility, gồm cumulative opportunity và gravity-type measures. Geurs & van Wee (2004) là review cốt lõi trong *Journal of Transport Geography*, phân loại accessibility measures và nhấn mạnh vai trò của land-use + transport interaction.

Framework này kế thừa trực tiếp logic đó trong **MAI**: cơ hội metropolitan được tính bằng trọng số cơ hội và hàm suy giảm thời gian.

Nhưng nếu chỉ dùng một accessibility surface, nghiên cứu sẽ không phân biệt được ba trạng thái rất khác nhau:

- local tốt nhưng metro yếu → **Fragmented Capability**;
- local yếu nhưng transit corridor giúp metro access → **Transit-Dependent**;
- cả local và metro đều yếu → **Motorcycle Lock-in**.

**Nghiên cứu này bổ sung:** thay vì một score đơn, framework tạo cấu trúc hai tầng **NAI × MCS**, trong đó MCS kết hợp MAI và RAC. Nhờ vậy, accessibility được chuyển thành typology quy hoạch.

---

### 5.4 So với transit-vs-car competitiveness

Liao et al. (2020) là paper gần nhất về logic “relative accessibility”: họ so sánh chênh lệch thời gian đi lại giữa car và transit ở nhiều đô thị, chỉ ra transit thường chịu bất lợi so với car và bất lợi này phân bố không đều theo không gian-thời gian.

Đây là tiền lệ quan trọng vì nó cho thấy absolute transit accessibility không đủ; cần hỏi transit cạnh tranh với phương thức thay thế tốt đến đâu.

Tuy nhiên, ở Hà Nội, benchmark **car** có thể sai. Lựa chọn thực tế của nhiều cư dân không phải “bus hay car”, mà là “bus hay xe máy”. Xe máy có ưu thế riêng: linh hoạt, len lỏi trong tắc nghẽn, chi phí thấp, đỗ gần điểm đến, và đã là mode mặc định.

**Nghiên cứu này bổ sung:** giữ logic relative competitiveness của Liao et al. (2020), nhưng thay denominator từ car sang **motorcycle**. Đây là bước chuyển từ car-centric accessibility sang motorcycle-centric accessibility.

---

### 5.5 So với transport equity / accessibility planning indicators

Boisjoly & El-Geneidy (2017) phê bình cách các metropolitan transport plans sử dụng accessibility objectives và indicators: nhiều kế hoạch nói về accessibility nhưng indicator chưa đủ rõ hoặc chưa gắn tốt với mục tiêu công bằng. Pereira et al. (2017) nhấn mạnh accessibility là công cụ để phân tích công bằng phân phối trong giao thông.

Framework này tiếp thu hướng equity đó bằng cách không chỉ báo mean SMCI, mà còn báo:

- typology distribution,
- population exposure theo typology,
- built-cell zero-access audit,
- nhóm **Motorcycle Lock-in**.

**Nghiên cứu này bổ sung:** công bằng không chỉ là ai có nhiều accessibility hơn, mà là ai bị kẹt trong trạng thái không có local access và cũng không có transit cạnh tranh với xe máy.

---

### 5.6 So với nghiên cứu motorcycle-dependent cities

Khuat (2006) đặt nền cho khái niệm motorcycle-dependent cities. Vu Anh Tuan (2015) phân tích hành vi lựa chọn phương thức và khả năng chuyển dịch sang public transport ở Hà Nội. JICA HAIDEP (2010), Nguyen & Nguyen (2018), và Vu Anh Tuan et al. (2016) cung cấp cơ sở về tốc độ và đặc điểm vận hành xe máy ở Hà Nội/Việt Nam.

Các nghiên cứu này rất quan trọng vì chứng minh xe máy không phải yếu tố phụ; nó là cấu trúc nền của hệ thống giao thông đô thị.

Nhưng phần lớn literature này dừng ở mô tả/mô hình hóa mode choice, traffic management, hoặc speed calibration. Nó chưa biến motorcycle dependence thành một chỉ số accessibility cạnh tranh ở cấp ô lưới.

**Nghiên cứu này bổ sung:** dùng literature xe máy để xây **Network D**, sau đó đưa Network D vào công thức **RAC_time** và **RAC_opp**. Như vậy, motorcycle dependence không chỉ nằm trong phần bối cảnh; nó nằm trong chính method.

---

### 5.7 So với green megaproject / new town evaluation

Với green megaprojects, literature thường đánh giá qua thiết kế, mật độ, mixed use, hạ tầng xanh, TOD, hoặc hình ảnh bền vững. Đây là các tiêu chí cần thiết nhưng chưa đủ.

Một dự án có bus điện không tự động tạo ra sustainable mobility. Bus điện có thể cải thiện phát thải trên mỗi chuyến, nhưng nếu cư dân vẫn phải dùng xe máy cho phần lớn tiếp cận metropolitan, capability vẫn bị phân mảnh.

**Nghiên cứu này bổ sung:** đánh giá “green” bằng outcome giao thông có thể đo được: **local access + metropolitan access + motorcycle competitiveness**. Đây là cách kiểm tra tuyên bố xanh bằng accessibility thực tế, không chỉ bằng hạ tầng hoặc branding.

**Ghi chú cần làm trước khi submit:** phần này cần bổ sung 3–5 references chuyên biệt về eco-city/new town/green megaproject ở châu Á. Hiện contribution chính vẫn đứng vững vì paper định vị trong accessibility/motorcycle-dependent transport geography, nhưng framing về megaproject nên được củng cố thêm.

---

## 6. Bằng chứng pilot: framework không chỉ là ý tưởng

Pilot đã chạy trên 462 ô lưới 250 m tại Ocean Park + vùng đệm.

Dữ liệu sử dụng:

- OSM walking network,
- OSM driving network,
- merged OSM + Overture POIs: 161 POIs,
- Hanoi GTFS 2018 làm baseline trước VinBus,
- VinBus pseudo-GTFS từ API: 176 routes, 5,631 stops, headway 5–48 phút,
- WorldPop 2020,
- VIDA building footprints,
- 10 OD pairs Google Maps Android để kiểm chứng xe máy.

Kết quả chính:

| Chỉ tiêu | Kết quả pilot |
|---|---:|
| Số ô lưới | 462 |
| Mean SMCI Scenario A, không VinBus | 0.0449 |
| Mean SMCI Scenario B, có VinBus | 0.0920 |
| Mean ΔSMCI | +0.0471 |
| Ô cải thiện | 288/462 = 62.34% |
| Ô không đổi | 174/462 = 37.66% |
| Ô suy giảm | 0 |
| Motorcycle validation MAE | 1.90 phút |
| Spearman rho multiplicative vs additive SMCI | 0.824 |

Diễn giải: VinBus cải thiện capability rõ ràng, nhưng không triệt tiêu phụ thuộc xe máy. Đây chính là logic “fragmented capability”: có can thiệp xanh, có cải thiện, nhưng hệ thống chưa đủ tích hợp.

---

## 7. Typology Scenario B

| Typology | Số ô | Diễn giải |
|---|---:|---|
| Integrated Capability | 167 | Local + metro + competitiveness cùng mạnh |
| Motorcycle Lock-in | 167 | Cả local access và metropolitan competitiveness yếu |
| Fragmented Capability | 64 | Local tốt nhưng metro/competition yếu |
| Transit-Dependent | 64 | Local yếu nhưng metro/competition tương đối tốt |

Điểm quan trọng: **Motorcycle Lock-in vẫn là nhóm lớn**, chiếm 167/462 ô. Theo WorldPop, nhóm này chứa khoảng **34.2% dân số** trong pilot.

Vì vậy, claim không phải “VinBus thất bại”. Claim chính xác hơn:

> VinBus cải thiện accessibility, nhưng cải thiện đó không đủ để tạo integrated sustainable mobility capability trên toàn không gian. Megaproject xanh vẫn tạo ra phân mảnh capability.

---

## 8. Vì sao professor có thể tin phương pháp này?

### 8.1 Không chỉ lý thuyết — đã có pipeline chạy được

Toàn bộ công thức nằm trong code, có test. Pipeline đã tạo:

- accessibility inputs,
- pilot metrics,
- validation outputs,
- maps,
- robustness checks,
- supervisor memo.

### 8.2 Biết rõ hạn chế và đã kiểm tra

| Rủi ro | Cách xử lý |
|---|---|
| OSM POIs thiếu | Bổ sung Overture; 55/55 Overture-only POIs được xác nhận; merged layer làm primary |
| GTFS cũ | Dùng có chủ đích làm baseline trước VinBus |
| VinBus không có GTFS chính thức | Tạo pseudo-GTFS từ API công khai; 176 routes, 5,631 stops, observed headways |
| Motorcycle speed không chắc | Calibrate bằng literature Việt Nam; kiểm chứng 10 OD pairs Google Maps, MAE 1.90 phút |
| MAI/RAC collinearity | Báo VIF; chạy RAC_time-only sensitivity, κ = 0.871 |
| SMCI phụ thuộc phép nhân | So với additive index, Spearman ρ = 0.824 |
| Zero-access có thể là hồ/công viên | VIDA footprints cho thấy 112/116 zero-NAI cells là built cells |

### 8.3 Có đóng góp rõ cho Journal of Transport Geography

Bài không chỉ là case study địa phương. Nó đóng góp framework có thể áp dụng cho các thành phố phụ thuộc xe máy khác:

- Hà Nội,
- TP.HCM,
- Bangkok,
- Jakarta,
- Phnom Penh,
- Bengaluru,
- các đô thị Nam Á và Đông Nam Á.

Điểm chuyển giao là logic phương pháp: thay car benchmark bằng motorcycle benchmark.

---

## 9. Luận điểm chính để trình bày với professor

Nếu cần nói trong 2 phút:

> Literature hiện có đo walkability, đo metropolitan accessibility, hoặc đo transit competitiveness so với ô tô. Nhưng trong Hà Nội, vấn đề không phải transit có tồn tại hay không, cũng không phải transit có cạnh tranh với ô tô hay không. Vấn đề là transit có cạnh tranh với xe máy hay không. Em đề xuất framework tách local access và metropolitan access, rồi thêm RAC — chỉ số cạnh tranh đi bộ+transit so với xe máy. Khi kết hợp thành SMCI, framework cho thấy Ocean Park có cải thiện nhờ VinBus nhưng vẫn còn phân mảnh: một phần lớn ô lưới và dân số vẫn ở trạng thái Motorcycle Lock-in. Vì vậy, đóng góp của đề tài là một khung accessibility phù hợp cho motorcycle-dependent green megaprojects, không chỉ một đánh giá riêng của Ocean Park.

---

## 10. Cách đóng khung novelty trong proposal

Có thể viết novelty thành ba câu:

1. **Scale novelty:** nghiên cứu tách neighborhood accessibility khỏi metropolitan accessibility, thay vì gộp vào một chỉ số.
2. **Mode novelty:** nghiên cứu benchmark transit với motorcycle, không phải car.
3. **Planning novelty:** nghiên cứu chuyển score thành typology để nhận diện Integrated, Fragmented, Transit-Dependent, và Motorcycle Lock-in areas.

Một câu chốt:

> The framework reveals that a green megaproject may be locally accessible but metropolitanly and modally fragmented.

Bản tiếng Việt:

> Khung này cho thấy một megaproject “xanh” có thể tốt ở tầng tiện ích nội khu nhưng vẫn thất bại ở tầng tiếp cận đô thị và cạnh tranh phương thức.

---

## 11. References nền tảng cần dùng trong bản proposal/paper

Danh sách dưới đây nên được kiểm tra lại format/DOI trước khi nộp chính thức.

### Accessibility theory

- Hansen, W. G. (1959). How accessibility shapes land use. *Journal of the American Institute of Planners*.
- Handy, S. L., & Niemeier, D. A. (1997). Measuring accessibility: An exploration of issues and alternatives. *Environment and Planning A*.
- Geurs, K. T., & van Wee, B. (2004). Accessibility evaluation of land-use and transport strategies. *Journal of Transport Geography*.

### 15-minute city / local accessibility

- Moreno, C., Allam, Z., Chabaud, D., Gall, C., & Pratlong, F. (2021). Introducing the 15-Minute City. *Smart Cities*.
- Pozoukidou, G., & Chatziyiannaki, Z. (2021). 15-minute city: Decomposing the new urban planning eutopia. *Sustainability*.

### Mode-competitive accessibility

- Liao, Y., Gil, J., Pereira, R. H. M., Yeh, S., & Verendel, V. (2020). Disparities in travel time between car and transit. *Scientific Reports*.
- Boisjoly, G., & El-Geneidy, A. (2017). How to get there? A critical assessment of accessibility objectives and indicators in metropolitan transportation plans. *Transport Policy*.
- Pereira, R. H. M., Schwanen, T., & Banister, D. (2017/2019). Distributive justice and equity in transportation / accessibility inequality literature.

### Motorcycle-dependent cities / Vietnam

- Khuat, V. H. (2006). *Traffic management in motorcycle dependent cities*. Doctoral dissertation.
- Vu Anh Tuan. (2015). Mode choice behavior and modal shift to public transport in developing countries — The case of Hanoi city.
- Nguyen, X. L., & Nguyen, H. T. (2018). Operating speed of motorcycles on urban streets in Hanoi.
- JICA. (2010). *HAIDEP: The comprehensive urban development programme in Hanoi capital city*.

### Green megaproject / new town framing

- Use this section carefully: cần bổ sung thêm sources chuẩn về Asian new towns, eco-cities, green urbanism, and megaproject critique before submission.
- Current project can still proceed because empirical contribution is accessibility-methodological, not primarily urban-design theory.

---

## 12. Kết luận pitch

Đề tài thuyết phục vì nó có một câu hỏi rõ, một gap rõ, một framework mới, và pilot đã chứng minh framework chạy được.

**Vấn đề:** megaproject xanh có thể tạo tiện ích nội khu nhưng không tạo mobility bền vững nếu transit không cạnh tranh được với xe máy.

**Giải pháp:** đo ba điều kiện cùng lúc — NAI, MAI, RAC — rồi kết hợp thành SMCI và typology.

**Đóng góp:** chuyển accessibility research từ car-centric sang motorcycle-centric trong bối cảnh Đông Nam Á.

**Thông điệp chính:** Ocean Park không đơn giản là “tốt” hay “xấu”. Nó là một ví dụ của **fragmented mobility capability**: xanh ở hình ảnh và có cải thiện transit, nhưng vẫn chưa đủ để giải phóng cư dân khỏi phụ thuộc xe máy.
