# RESEARCH PROPOSAL

> **Scale migration notice (2026-08-11):** The canonical primary SMCI is now the cell-level equal-weight geometric mean (A=0.1470, B=0.1711, Delta=+0.0242). Product-scale numbers retained in this historical proposal are legacy audit values; use `proposal/proposal_v7.md` and `docs/metrics_reference.md` for current methods.

## Vượt ra ngoài đô thị 15 phút: Khung đánh giá năng lực di chuyển bền vững bị phân mảnh tại Vinhomes Ocean Park, Hà Nội

**Ứng viên:** Đặng Tuấn Kiệt
**Ngày nộp:** 23/07/2026
**Từ khóa:** accessibility; mobility capability; 15-minute city; TOD; xe máy; giao thông công cộng; GIS.

## Tóm tắt

Các khung đô thị 15 phút và phát triển định hướng giao thông công cộng nhấn mạnh sự gần gũi giữa nơi ở, dịch vụ và cơ hội. Tuy nhiên, một khu đô thị có thể đầy đủ tiện ích hằng ngày mà cư dân vẫn phụ thuộc xe máy để tiếp cận việc làm, giáo dục đại học, y tế chuyên sâu và các hoạt động cấp đô thị. Đề xuất này gọi trạng thái đó là năng lực di chuyển bền vững bị phân mảnh. Nghiên cứu phát triển Sustainable Mobility Capability Index (SMCI) để chẩn đoán đồng thời ba điều kiện: tiếp cận nhu cầu hằng ngày bằng đi bộ, tiếp cận cơ hội cấp đô thị bằng đi bộ kết hợp giao thông công cộng, và năng lực cạnh tranh về thời gian của phương thức này so với xe máy.

Nghiên cứu là phân tích mạng lưới GIS theo ô lưới 250 m, giới hạn tại Vinhomes Ocean Park và vùng tiếp cận liên quan. Network A là đi bộ; Network B là đi bộ kết hợp mạng giao thông công cộng hiện có; Network C bổ sung VinBus; Network D là xe máy. Scenario A so sánh A với B, không có VinBus; Scenario B so sánh A với C, có VinBus. Kết quả dự kiến gồm các bản đồ thành phần, SMCI, typology không gian và phân tích độ nhạy. Đóng góp chính là chuyển trọng tâm từ việc một địa điểm có gần tiện ích hay không sang việc các lớp tiếp cận có đồng thời tạo được lựa chọn di chuyển bền vững hay không.

## 1. Bối cảnh, vấn đề và khoảng trống

Accessibility là khả năng tiếp cận hoạt động, không đồng nhất với tốc độ hay lượng di chuyển. Vì vậy, đánh giá chính sách giao thông và sử dụng đất cần xem xét đồng thời cấu trúc cơ hội, chi phí tiếp cận và phương thức sẵn có (Geurs & van Wee, 2004; Handy & Niemeier, 1997). Các diễn giải về đô thị 15 phút nhấn mạnh proximity, đa dạng chức năng và tiếp cận dịch vụ hằng ngày bằng phương thức bền vững (Allam et al., 2022; Caselli, 2021; Moreno et al., 2021). Tổng quan gần đây cũng cho thấy cách vận hành hóa mô hình này khác nhau đáng kể giữa các thành phố (Teixeira et al., 2024).

Tuy vậy, tiếp cận cấp khu ở không bảo đảm tiếp cận cấp đô thị. Bằng chứng từ khu vực quanh ga cho thấy sự gần điểm dừng và kết quả di chuyển địa phương phụ thuộc mạnh vào bối cảnh không gian và điều kiện đi bộ (Chuang et al., 2023). Các thước đo cumulative và gravity-based cũng có thể cho các chẩn đoán khác nhau, nên lựa chọn chỉ số phải phù hợp câu hỏi nghiên cứu và được kiểm tra độ nhạy (Kapatsila et al., 2023).

Vấn đề này đặc biệt quan trọng tại thành phố phụ thuộc xe máy. Xe máy cung cấp hành trình cửa-đến-cửa linh hoạt, tạo chuẩn so sánh thực tế hơn ô tô đối với giao thông công cộng tại Hà Nội. Nghiên cứu tại Hà Nội về tích hợp tiếp cận transit cho thấy first-mile, last-mile và liên kết phương thức là các điều kiện thiết yếu, không phải chi tiết thứ yếu (Hung et al., 2024). Do đó, nghiên cứu không suy luận rằng có tuyến xe buýt đồng nghĩa với lựa chọn bền vững khả thi.

Khoảng trống là thiếu một khung cùng lúc trả lời ba câu hỏi: cư dân có tiếp cận nhu cầu hằng ngày bằng đi bộ không; họ có tiếp cận cơ hội cấp đô thị bằng đi bộ kết hợp transit không; và transit có đủ cạnh tranh với xe máy không. SMCI được đề xuất như công cụ chẩn đoán khoảng trống này, không phải dự báo lựa chọn phương thức hay chỉ số phúc lợi cá nhân.

## 2. Mục tiêu và câu hỏi nghiên cứu

Mục tiêu tổng quát là phát triển khung đánh giá đa cấp về năng lực di chuyển bền vững cho một khu đô thị mới trong bối cảnh phụ thuộc xe máy.

Nghiên cứu sẽ: xây dựng Neighbourhood Accessibility Index (NAI) cho nhu cầu hằng ngày bằng đi bộ; xây dựng Metropolitan Accessibility Index (MAI) cho cơ hội cấp đô thị bằng đi bộ kết hợp transit; xây dựng Relative Accessibility Competitiveness (RAC) với xe máy là benchmark; tích hợp các thành phần thành SMCI; và xác định thay đổi theo Scenario A và B.

Năm câu hỏi nghiên cứu là: (1) Nhu cầu hằng ngày có thể tiếp cận bằng đi bộ khác nhau thế nào trong phạm vi nghiên cứu? (2) MAI thay đổi thế nào khi bổ sung VinBus? (3) Transit cạnh tranh với xe máy ở đâu và ở mức nào? (4) Những typology năng lực di chuyển nào xuất hiện? (5) Kết luận có ổn định trước các giả định về ngưỡng, trọng số, thời gian transit và tốc độ xe máy không?

## 3. Khung khái niệm và phương pháp

### 3.1. Phạm vi và dữ liệu

Nghiên cứu là case study định lượng tại Vinhomes Ocean Park, sử dụng ô lưới 250 m làm đơn vị phân tích. Network B dùng `data/raw/hanoi_gtfs.zip`, là feed World Bank có niên đại tệp 2020 nhưng ngày dịch vụ năm 2018, vì vậy chỉ được diễn giải là baseline lịch sử hạn chế, trước VinBus. Network C dùng pseudo-GTFS VinBus đã được thu thập và kiểm soát chất lượng; đây không phải GTFS chính thức. Mạng đường đi bộ và đường bộ, POI, dấu chân công trình, dữ liệu dân số cùng magnitude cơ hội sẽ được lưu provenance và kiểm tra theo từng nguồn.

Các miền MAI là kinh tế, giáo dục đại học, y tế tuyến cao và thương mại cấp đô thị. Magnitude chỉ dùng khi có nguồn truy nguyên, ví dụ việc làm, quy mô tuyển sinh, giường bệnh hoặc diện tích phục vụ. Điểm đến thiếu magnitude đáng tin cậy sẽ bị loại khỏi đặc tả chính hoặc chỉ xuất hiện trong kiểm tra độ nhạy. Thời gian transit là thời gian cửa-đến-cửa, gồm đi bộ tiếp cận, chờ, thời gian trên xe, chuyển tuyến và đi bộ thoát mạng. Cách tiếp cận này phù hợp với các đo lường accessibility dựa trên thời gian hành trình đầy đủ (Tahmasbi & Haghshenas, 2019).

### 3.2. Neighbourhood Accessibility Index

NAI đo số tiện ích nhu cầu hằng ngày tiếp cận được trên mạng đi bộ, không dùng bán kính đường chim bay. Các nhóm gồm thực phẩm và mua sắm thiết yếu, giáo dục cơ bản, y tế cơ bản, không gian công cộng, và dịch vụ cá nhân cần thiết. Ngưỡng chính là 800 m, một giả định vận hành chứ không phải chuẩn đã được kiểm định tại địa phương. Các ngưỡng 600 m, 1.000 m và 1.200 m được kiểm tra độ nhạy; 1.200 m chỉ là cận trên lạc quan.

Với ô xuất phát i và tiện ích đủ điều kiện j, chỉ số gốc là:

```
NAI_raw,i = sum_j I(d_walk,ij <= D)
```

Trong đó `d_walk,ij` là khoảng cách mạng đi bộ và `D` là ngưỡng đi bộ. Cách tính count-based này được thực thi trong `src/accessibility_inputs.py::build_network_accessibility_inputs`; `src/accessibility.py` chuẩn hóa NAI và tích hợp nó vào SMCI. Đa dạng nhóm chức năng và NAI có giới hạn theo nhóm chỉ được báo cáo như độ nhạy. Ô bằng không phải trải qua zero-access audit với POI, dấu chân công trình và dân số trước khi được diễn giải là thiếu dịch vụ thực tế.

### 3.3. Metropolitan Accessibility Index

MAI dùng trọng số cơ hội và hàm suy giảm thời gian tuyến tính ngưỡng. Với thời gian cửa-đến-cửa `t_ij`, hàm suy giảm là:

```
f(t) = 1                    if t <= 30
     = (60 - t) / 30        if 30 < t <= 60
     = 0                    if t > 60

A_ik = sum_j [M_jk * f(t_ij)]
MAI_raw,i = sum_k [alpha_k * A_ik]
```

Đặc tả mặc định dùng trọng số miền lần lượt: kinh tế 0,40; giáo dục đại học 0,20; y tế tuyến cao 0,20; thương mại cấp đô thị 0,20. Các bộ trọng số bằng nhau, job-heavy, economic-light, service-health-heavy và UTM-derived là độ nhạy. MAI chính là cumulative opportunity có trọng số và suy giảm thời gian tuyến tính; hàm suy giảm mũ là độ nhạy. Lựa chọn và kiểm tra độ nhạy này phản ánh khác biệt đã được ghi nhận giữa các họ thước đo accessibility (Kapatsila et al., 2023).

### 3.4. Relative Accessibility Competitiveness

RAC so sánh transit với xe máy trên cùng tập cơ hội. Đặc tả chính là `RAC_time`, nhằm tránh đưa MAI vào RAC lần nữa. Với thời gian trung bình có trọng số cơ hội của xe máy và transit:

```
RAC_time_raw,i = T_motorcycle,i / T_walk_transit,i
```

Giá trị cao hơn thể hiện transit cạnh tranh hơn. `RAC_time_raw` và chỉ báo phụ `RAC_opp_raw` được chuẩn hóa chung giữa Scenario A và B. RAC tổng hợp từ hai thành phần chỉ được báo cáo như chỉ báo phụ; `RAC_time` là thành phần SMCI chính. MAI và RAC được kiểm tra VIF do đồng biến cấu trúc được kỳ vọng.

Tốc độ Network D là giả định kịch bản minh bạch theo loại đường, dùng hệ số tốc độ từ hiệu chỉnh của dự án, không lấy trực tiếp tốc độ lái xe OSM và không tuyên bố đã hiệu chuẩn từ tài liệu. Kiểm tra plausibility dùng spot-check thủ công trên ứng dụng Google Maps dành cho người dùng, không dùng Google TWO_WHEELER API hàng loạt. Các dải GPS Hà Nội, nếu được dùng làm bối cảnh, không phải bộ tham số hiệu chuẩn.

### 3.5. Chuẩn hóa, SMCI và typology

Tất cả NAI, MAI và RAC phục vụ so sánh Scenario A/B được chuẩn hóa min-max theo giới hạn gộp chung của cả hai scenario:

```
x_norm = (x - min_pool) / (max_pool - min_pool)
```

Giới hạn chung bảo đảm chênh lệch scenario không do thang đo thay đổi. SMCI đặc tả chính là geometric mean trọng số bằng nhau:

```
SMCI_i = (NAI_norm,i * MAI_norm,i * RAC_time_norm,i)^(1/3)
```

Geometric mean nhạy với mắt xích yếu: thành phần bằng không làm SMCI bằng không, dù các thành phần khác cao. Nó vẫn cho phép bù trừ một phần giữa các giá trị dương, do đó không được mô tả là hoàn toàn không bù trừ. Đặc tả cộng chỉ dùng robustness check:

```
SMCI_add,i = (NAI_norm,i + MAI_norm,i + RAC_time_norm,i) / 3
```

Không dùng product như robustness vì đó là biến đổi đơn điệu của geometric mean và không kiểm tra tính ổn định thực chất.

Typology chính là theory-first rank-based median split giữa NAI và Metropolitan Competitiveness Score:

```
MCS_i = sqrt(MAI_norm,i * RAC_time_norm,i)
```

NAI cao và MCS cao tạo **Integrated Capability**; NAI cao, MCS thấp tạo **Fragmented Capability**; NAI thấp, MCS cao tạo **Transit-Dependent**; NAI thấp, MCS thấp tạo **Motorcycle Lock-in**. Median split tạo nhóm so sánh theo thiết kế, không khẳng định dữ liệu có bốn cụm tự nhiên. K-means chỉ là robustness check.

### 3.6. Kiểm định và độ nhạy

Phân tích sẽ thay đổi ngưỡng NAI, hàm suy giảm MAI, trọng số miền cơ hội, thời gian chờ và chuyển tuyến, cùng giả định tốc độ xe máy. Kết quả sẽ báo cáo tương quan Spearman giữa xếp hạng, Cohen's kappa cho độ ổn định typology, zero-access audit, và kiểm tra đa cộng tuyến MAI/RAC cùng độ nhạy RAC_time-only. Mỗi bản đồ tổng hợp luôn đi kèm bản đồ NAI, MAI và RAC; SMCI không thay thế diễn giải các thành phần.

## 4. Kết quả dự kiến, đóng góp và giới hạn

Sản phẩm dự kiến là bản đồ NAI, MAI, RAC_time, SMCI và MCS cho hai scenario; bản đồ thay đổi; phân bố dân số theo typology; cùng phụ lục độ nhạy và provenance. Nghiên cứu kỳ vọng phát hiện các vị trí có NAI cao nhưng MCS thấp. Nếu hiện diện, cấu hình này là bằng chứng không gian cho fragmented capability, không phải bằng chứng nhân quả về hành vi.

Đóng góp lý thuyết là phân biệt local completeness với metropolitan capability. Đóng góp phương pháp là benchmark xe máy, chuẩn hóa chung hai scenario, SMCI multiplicative và typology theory-first. Đóng góp thực tiễn là chẩn đoán can thiệp phù hợp: bổ sung tiện ích gần đối với Transit-Dependent, kết nối vùng và nâng chất lượng transit đối với Fragmented Capability, và gói sử dụng đất-giao thông đối với Motorcycle Lock-in.

Giới hạn cốt lõi là nghiên cứu đo năng lực cấu trúc tại địa điểm, không đo khả năng chi trả, an toàn cảm nhận, nhiệt, sở thích, quyền sở hữu xe máy, trách nhiệm chăm sóc hay hành vi thực tế. Dữ liệu GTFS baseline có giới hạn lịch sử; pseudo-GTFS VinBus cần được diễn giải thận trọng. Khảo sát hành vi hoặc dữ liệu hành trình trong giai đoạn sau có thể kiểm định liên hệ giữa chỉ số với mode share hoặc travel satisfaction, nhưng không thuộc suy luận chính của nghiên cứu này.

## 5. Kế hoạch 36 tháng

Sáu tháng đầu tập trung tổng quan, khung khái niệm và kiểm kê dữ liệu. Tháng 7-12 xây dựng NAI và cơ sở dữ liệu cơ hội. Tháng 13-18 xây dựng MAI, RAC và SMCI. Tháng 19-24 thực hiện phân tích VinBus, typology và độ nhạy. Tháng 25-30 bổ sung kiểm định hành vi nếu có dữ liệu phù hợp. Sáu tháng cuối hoàn thiện luận án, phản biện nội bộ và công bố.

## Tài liệu tham khảo

Abdelfattah, L., Deponte, D., & Fossa, G. (2022). The 15-minute city: Interpreting the model to bring out urban resiliencies. *Transportation Research Procedia, 60*, 330-337. https://doi.org/10.1016/j.trpro.2021.12.043

Allam, Z., Bibri, S. E., Chabaud, D., & Moreno, C. (2022). The theoretical, practical, and technological foundations of the 15-minute city model: Proximity and its environmental, social and economic benefits for sustainability. *Energies, 15*(16), 6042. https://doi.org/10.3390/en15166042

Caselli, B. (2021). From urban planning techniques to 15-minute neighbourhoods. A theoretical framework and GIS-based analysis of pedestrian accessibility to public services. *European Transport/Trasporti Europei, 85*, 1-15. https://doi.org/10.48295/et.2021.85.10

Chuang, I.-T., Beattie, L., & Feng, L. (2023). Analysing the relationship between proximity to transit stations and local living patterns: A study of human mobility within a 15 min walking distance through mobile location data. *Urban Science, 7*(4), Article 105. https://doi.org/10.3390/urbansci7040105

Geurs, K. T., & van Wee, B. (2004). Accessibility evaluation of land-use and transport strategies: Review and research directions. *Journal of Transport Geography, 12*(2), 127-140. https://doi.org/10.1016/j.jtrangeo.2003.10.005

Handy, S. L., & Niemeier, D. A. (1997). Measuring accessibility: An exploration of issues and alternatives. *Environment and Planning A, 29*(7), 1175-1194. https://doi.org/10.1068/a291175

Hung, K. V., Ngoc, A. M., & Thanh, H. H. (2024). Investigation of modal integration for transit-access trips in motorcycle dependent cities: The case study of Hanoi, Vietnam. *Journal of Infrastructure, Policy and Development, 8*(8), Article 5351. https://doi.org/10.24294/jipd.v8i8.5351

Kapatsila, B., Palacios, M. S., Grise, E., & El-Geneidy, A. (2023). Resolving the accessibility dilemma: Comparing cumulative and gravity-based measures of accessibility in eight Canadian cities. *Journal of Transport Geography, 107*, Article 103530. https://doi.org/10.1016/j.jtrangeo.2023.103530

Moreno, C., Allam, Z., Chabaud, D., Gall, C., & Pratlong, F. (2021). Introducing the 15-minute city: Sustainability, resilience and place identity in future post-pandemic cities. *Smart Cities, 4*(1), 93-111. https://doi.org/10.3390/smartcities4010006

Tahmasbi, B., & Haghshenas, H. (2019). Public transport accessibility measure based on weighted door to door travel time. *Computers, Environment and Urban Systems, 76*, 163-177. https://doi.org/10.1016/j.compenvurbsys.2019.05.002

Teixeira, J. F., Silva, C., Seisenberger, S., Buttner, B., McCormick, B., Papa, E., & Cao, M. (2024). Classifying 15-minute cities: A review of worldwide practices. *Transportation Research Part A: Policy and Practice, 189*, Article 104234. https://doi.org/10.1016/j.tra.2024.104234
