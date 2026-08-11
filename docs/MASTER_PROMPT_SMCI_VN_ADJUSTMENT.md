# MASTER PROMPT CHO AGENTS  
## Đề xuất điều chỉnh và nâng cấp Sustainable Mobility Capability Index (SMCI) cho điều kiện giao thông hỗn hợp tại Việt Nam

**Tài liệu đầu vào bắt buộc**

1. `proposal_v7(2).md` — proposal hiện tại của dự án.
2. `Sustainable_Urban_Mobility_Indicators (1).docx` — tài liệu tổng hợp các bộ chỉ số giao thông đô thị bền vững hiện có.
3. Toàn bộ dữ liệu, scripts, tests, validation outputs và tài liệu phương pháp hiện có trong repository.

---

# 1. Vai trò của nhóm agents

Các agents phải làm việc như một nhóm nghiên cứu liên ngành gồm:

- Chuyên gia giao thông đô thị bền vững.
- Chuyên gia accessibility và transport geography.
- Chuyên gia mô hình lựa chọn phương tiện và hành vi đi lại.
- Chuyên gia thống kê, xây dựng chỉ số tổng hợp và validation.
- Chuyên gia dữ liệu không gian, GTFS, OSM và network routing.
- Chuyên gia bối cảnh giao thông hỗn hợp tại Việt Nam và Đông Nam Á.
- Red-team reviewer có nhiệm vụ phản biện các giả định, trọng số và tuyên bố đóng góp.
- Academic editor chịu trách nhiệm cập nhật proposal cuối cùng.

Không được xem đây là nhiệm vụ “thêm càng nhiều chỉ báo càng tốt”. Mục tiêu là xây dựng một phiên bản SMCI có cơ sở lý thuyết, bằng chứng thực nghiệm, khả năng triển khai và khả năng bảo vệ trước reviewer.

---

# 2. Mục tiêu tổng thể

Đánh giá, điều chỉnh và nâng cấp SMCI hiện tại để trả lời ba câu hỏi trung tâm:

1. Các bộ chỉ số giao thông đô thị bền vững hiện có lựa chọn chỉ báo, gán trọng số và tổng hợp chỉ số dựa trên evidence mạnh đến mức nào?
2. SMCI mới có điểm ưu việt gì so với các bộ chỉ số trước, và đóng góp đó có thể được chứng minh bằng lý thuyết, dữ liệu và validation hay không?
3. Trong điều kiện giao thông hỗn hợp, phụ thuộc xe máy và có ride-hailing như Việt Nam, SMCI cần bổ sung những khía cạnh nào để phản ánh đúng khả năng di chuyển bền vững?

Kết quả cuối cùng không chỉ là một danh sách đề xuất. Nhóm agents phải tạo ra:

- Một evidence audit có hệ thống.
- Một framework SMCI-VN có cấu trúc rõ ràng.
- Một phương án weighting và validation có thể thực hiện.
- Một lộ trình cập nhật code, dữ liệu và proposal.
- Một bản proposal chỉnh sửa hoàn chỉnh, nhất quán với pipeline thực tế.

---

# 3. Bối cảnh và cấu trúc hiện tại của proposal

Proposal hiện tại nghiên cứu khả năng di chuyển bền vững tại Vinhomes Ocean Park trong bối cảnh Hà Nội phụ thuộc mạnh vào xe máy.

Framework hiện tại gồm:

## 3.1 Neighborhood Accessibility Index — NAI

Đo khả năng tiếp cận các cơ hội hằng ngày bằng đi bộ trong phạm vi khu vực lân cận.

Cấu trúc hiện tại:

```text
NAI_i = số POI đủ điều kiện có thể tiếp cận bằng mạng đi bộ trong ngưỡng quy định
```

Ngưỡng chính hiện tại là 800 m, với các sensitivity thresholds 600 m, 1000 m và 1200 m.

## 3.2 Metropolitan Accessibility Index — MAI

Đo khả năng tiếp cận các cơ hội quy mô đô thị bằng đi bộ và giao thông công cộng.

Bốn nhóm cơ hội hiện tại:

- Economic opportunities: 0.40
- Higher education: 0.20
- Tertiary healthcare: 0.20
- Metropolitan commercial/services: 0.20

Cấu trúc:

```text
A_i,k = sum_j opportunity_weight_j,k × f(t_ij)
```

```text
MAI_i = 0.40 × A_i,economic
      + 0.20 × A_i,education
      + 0.20 × A_i,healthcare
      + 0.20 × A_i,commercial
```

## 3.3 Relative Accessibility Competitiveness — RAC

Đo khả năng cạnh tranh của đi bộ và giao thông công cộng so với xe máy.

Primary specification hiện tại:

```text
RAC_time_raw_i =
motorcycle opportunity-weighted mean travel time
/
walk-transit opportunity-weighted mean travel time
```

Phiên bản RAC dựa trên time được ưu tiên để tránh collinearity với MAI.

## 3.4 Sustainable Mobility Capability Index — SMCI

Cấu trúc hiện tại:

```text
SMCI_i = NAI_norm_i × MAI_norm_i × RAC_norm_i
```

SMCI sử dụng phép nhân nhằm thể hiện nguyên tắc weak-link: một địa điểm chỉ có sustainable mobility capability khi đồng thời có:

- Khả năng tiếp cận tại khu vực lân cận.
- Khả năng tiếp cận cơ hội quy mô đô thị.
- Khả năng cạnh tranh với xe máy.

Đây là nền tảng cần được giữ lại, kiểm định và nâng cấp; không được thay đổi chỉ để tạo cảm giác “mới hơn”.

---

# 4. Ba câu hỏi nghiên cứu điều chỉnh

Agents phải đánh giá và hoàn thiện ba research questions sau:

## RQ1 — Evidence của các bộ chỉ số hiện có

**What theoretical, empirical, institutional and validation evidence supports the selection, weighting and aggregation methods used in existing sustainable urban mobility indicator frameworks?**

Cần phân biệt ít nhất bốn loại evidence:

1. Evidence cho việc lựa chọn indicator.
2. Evidence cho định nghĩa và cách đo indicator.
3. Evidence cho việc gán weight.
4. Evidence cho aggregation rule và khả năng diễn giải composite score.

## RQ2 — Giá trị gia tăng của SMCI

**To what extent does the proposed SMCI provide greater contextual, construct, predictive and policy validity than existing indicator frameworks by incorporating dual-scale accessibility and competitiveness against motorcycles?**

Không được chỉ tuyên bố SMCI “tốt hơn”. Phải xác định chính xác:

- Tốt hơn ở loại validity nào.
- So sánh với framework nào.
- Được chứng minh bằng chỉ báo, test hoặc output nào.
- Phần nào SMCI chỉ bổ sung chứ không thay thế framework cũ.

## RQ3 — Điều chỉnh cho giao thông hỗn hợp Việt Nam

**How should mixed-traffic conditions—including reliability, safety conflicts, pedestrian discontinuity, motorcycle dependency, ride-hailing integration, affordability and climate exposure—be incorporated into a sustainable mobility capability index for Vietnamese cities?**

Không được mặc định mọi yếu tố đều phải đưa trực tiếp vào composite index. Mỗi yếu tố phải được đánh giá xem nên là:

- Thành phần cốt lõi.
- Modifier.
- Stratification variable.
- Diagnostic indicator.
- Robustness test.
- Biến giải thích bên ngoài.

---

# 5. Nhiệm vụ 1 — Evidence audit các bộ chỉ số hiện có

## 5.1 Phạm vi framework tối thiểu

Phải đánh giá ít nhất:

- SUTI — Sustainable Urban Transport Index.
- SUMI — Sustainable Urban Mobility Indicators.
- SUMP Core Indicators.
- SMRI — Sustainable Mobility Readiness Index.
- SDG 11.2.
- Urban Mobility Readiness Index.
- Sustainable Cities Mobility Index.
- Các composite accessibility hoặc sustainable mobility indices có liên quan trực tiếp.
- Các nghiên cứu dùng AHP, Delphi, entropy weighting, PCA, factor analysis, MICMAC, BWM, CRITIC hoặc hybrid weighting.

## 5.2 Evidence matrix bắt buộc

Tạo file:

```text
outputs/evidence/indicator_evidence_matrix.csv
```

Mỗi dòng là một indicator framework hoặc một nghiên cứu weighting. Các cột tối thiểu:

```text
framework_name
year
institution_or_authors
geographic_scope
intended_use
unit_of_analysis
indicator_count
indicator_domains
indicator_selection_method
weighting_method
aggregation_method
normalization_method
empirical_data_used
expert_sample
city_sample
behavioral_validation
predictive_validation
external_validation
sensitivity_analysis
uncertainty_reported
transferability_to_vietnam
main_strength
main_limitation
evidence_strength_selection
evidence_strength_weighting
evidence_strength_aggregation
source
notes
```

## 5.3 Quy tắc đánh giá evidence

Phải chấm riêng ba cấp:

### A. Indicator-selection evidence

- Strong: systematic review, theory, stakeholder validation, multi-city testing.
- Moderate: expert consultation hoặc institutional consensus nhưng thiếu behavioral validation.
- Weak: tác giả tự chọn hoặc mô tả không rõ.

### B. Weighting evidence

- Strong: estimated from observed behavior/outcomes, replicated, out-of-sample validated.
- Moderate: structured multi-expert method, sensitivity tested.
- Weak: equal weights, arbitrary weights hoặc expert weights không có robustness.

Equal weighting không được tự động gọi là sai. Phải mô tả nó là một quyết định normative hoặc parsimonious nếu framework có giải thích hợp lý.

### C. Aggregation evidence

- Strong: aggregation rule phù hợp với construct, có sensitivity và giải thích compensation.
- Moderate: công thức hợp lý nhưng ít validation.
- Weak: cộng hoặc nhân mà không giải thích hệ quả.

## 5.4 Câu hỏi red-team bắt buộc

- Framework có đo outcome hay chỉ đo input/readiness?
- Weight phản ánh social value, revealed demand hay convenience của dữ liệu?
- Có double counting giữa indicators không?
- Có city-size bias hoặc income bias không?
- Có thể chuyển trực tiếp từ châu Âu sang Việt Nam không?
- Composite score có che giấu bất bình đẳng nội đô không?
- Trọng số có ổn định qua thành phố, nhóm dân cư và thời gian không?
- Có confusion giữa indicator dashboard và một index tổng hợp không?

## 5.5 Deliverable

Tạo:

```text
outputs/evidence/evidence_audit.md
```

Tài liệu phải kết luận rõ:

- Evidence cho indicator selection thường mạnh hơn evidence cho exact numerical weights.
- Nhiều framework là monitoring dashboards, không phải behavioral indices.
- Trọng số phổ quát giữa các thành phố thường không được chứng minh đầy đủ.
- Đây là khoảng trống mà SMCI có thể đóng góp, nhưng chỉ khi weighting và validation được thiết kế nghiêm túc.

Không được viết kết luận trước rồi tìm nguồn củng cố. Phải để evidence matrix dẫn đến kết luận.

---

# 6. Nhiệm vụ 2 — Định vị đóng góp khoa học của SMCI

Agents phải xây dựng một positioning statement rõ ràng.

## 6.1 Đóng góp cốt lõi được đề xuất

SMCI không nên được quảng bá như một bộ chỉ số thay thế toàn bộ SUTI, SUMI hoặc SUMP.

Positioning ưu tiên:

> SMCI is a spatially explicit, dual-scale and mode-competitive accessibility index designed to complement existing sustainable mobility indicator systems by measuring whether walking and public transport provide usable and competitive access to daily and metropolitan opportunities in motorcycle-dependent urban environments.

## 6.2 Các ưu điểm cần kiểm chứng

### A. Dual-scale accessibility

SMCI tách:

- Local completeness.
- Metropolitan opportunity reach.

Điều này cho phép phát hiện:

- Khu vực đủ tiện nghi nội bộ nhưng yếu về kết nối đô thị.
- Khu vực có transit reach nhưng yếu về khả năng đi bộ địa phương.
- Green mobility enclave.
- Fragmented capability.

### B. Mode competitiveness

SMCI không chỉ đo transit availability mà đo transit có cạnh tranh được với xe máy hay không.

### C. Spatial distribution

SMCI hoạt động ở cấp grid cell, tránh che giấu bất bình đẳng nội đô bởi một city-level average.

### D. Weak-link logic

Phép nhân thể hiện rằng local access, metropolitan access và competitiveness đều cần thiết.

### E. Policy sensitivity

Có thể đo:

- Before/after.
- Scenario A/B.
- Spatial winners and losers.
- Boundary discontinuity.
- Population affected.

## 6.3 Các giới hạn phải tuyên bố trung thực

SMCI hiện chưa phải một full sustainability index vì chưa trực tiếp đo đầy đủ:

- Road fatalities.
- Emissions.
- Air pollution exposure.
- Affordability.
- Gender and disability equity.
- Governance.
- Fiscal feasibility.
- Freight sustainability.
- Broader land-use and environmental outcomes.

Do đó, proposal phải dùng các cụm:

- “complements existing frameworks”
- “measures sustainable mobility capability”
- “accessibility and mode-competitiveness dimension”
- “context-specific extension for motorcycle-dependent cities”

Không dùng:

- “replaces SUTI/SUMI”
- “complete measure of urban transport sustainability”
- “universally superior index”

## 6.4 Deliverable

Tạo:

```text
outputs/concept/smci_contribution_and_positioning.md
```

Phải có:

- Contribution statement.
- Construct definition.
- Unit of analysis.
- Intended use.
- Claims được phép đưa ra.
- Claims không được phép đưa ra.
- So sánh SMCI với SUTI/SUMI/SUMP/SMRI bằng bảng.

---

# 7. Nhiệm vụ 3 — Thiết kế framework SMCI-VN

Không được ngay lập tức thay công thức hiện tại bằng một công thức lớn hơn. Phải xây dựng nested model strategy.

## 7.1 Model M0 — Current baseline

```text
SMCI_M0_i =
NAI_norm_i
× MAI_norm_i
× RAC_time_norm_i
```

M0 là baseline bắt buộc để so sánh.

## 7.2 Model M1 — Generalized competitiveness

Thay RAC chỉ dựa trên thời gian bằng generalized door-to-door impedance.

Định nghĩa:

```text
GC_i,m =
βT × E(T_i,m)
+ βR × Reliability_i,m
+ βC × MonetaryCost_i,m
+ βX × TransferBurden_i,m
+ βA × AccessEgressBurden_i,m
+ βP × ParkingBurden_i,m
```

Với mode:

```text
m ∈ {motorcycle, walk_transit}
```

Đề xuất:

```text
RAC_GC_raw_i =
GC_i,motorcycle
/
GC_i,walk_transit
```

Sau đó chuẩn hóa:

```text
RAC_GC_norm_i = normalize(RAC_GC_raw_i)
```

M1:

```text
SMCI_M1_i =
NAI_norm_i
× MAI_norm_i
× RAC_GC_norm_i
```

Agents phải kiểm tra hướng tỷ lệ và cách diễn giải để giá trị cao luôn thể hiện transit cạnh tranh tốt hơn.

## 7.3 Model M2 — Mixed-Traffic Feasibility modifier

Chỉ thêm MTF nếu dữ liệu và construct validity đủ mạnh.

Các candidate dimensions:

```text
SafetyConflict
PedestrianContinuity
Reliability
ClimateExposure
UniversalAccess
IntermodalIntegration
```

Cấu trúc thử nghiệm:

```text
MTF_i =
weighted_geometric_mean(
Safety_i,
PedestrianContinuity_i,
Reliability_i,
ClimateResilience_i,
Inclusion_i,
IntermodalIntegration_i
)
```

M2:

```text
SMCI_M2_i =
SMCI_M1_i × MTF_i
```

Không được promote M2 thành primary model nếu:

- Dữ liệu phần lớn là proxy yếu.
- MTF trùng lặp mạnh với RAC_GC hoặc NAI.
- Kết quả quá nhạy với normalization.
- Không cải thiện validity.
- Không thể giải thích rõ cho planner.

## 7.4 Model M3 — Equity-stratified capability

Không nhất thiết thêm equity trực tiếp vào composite.

Ưu tiên tính SMCI riêng cho:

- Low-income residents.
- Women.
- Older adults.
- Persons with disabilities.
- Households without motorcycles.
- Shift workers.
- Students.
- Caregivers.

Cấu trúc:

```text
SMCI_i,g
```

Trong đó `g` là nhóm dân cư.

Sau đó đo:

```text
EquityGap_i =
max_g(SMCI_i,g) - min_g(SMCI_i,g)
```

Hoặc:

```text
PopulationWeightedDisadvantage_g
```

M3 là extension nếu có dữ liệu survey hoặc behavioral parameters theo nhóm.

---

# 8. Nhiệm vụ 4 — Các khía cạnh cần bổ sung cho giao thông hỗn hợp Việt Nam

Mỗi dimension dưới đây phải được đánh giá theo sáu tiêu chí:

1. Theoretical relevance.
2. Evidence in Vietnam/Southeast Asia.
3. Data availability.
4. Spatial measurability.
5. Independence from current constructs.
6. Policy interpretability.

Tạo bảng quyết định:

```text
dimension
construct_definition
why_relevant_in_vietnam
candidate_variables
data_source
spatial_resolution
temporal_resolution
expected_direction
overlap_risk
measurement_quality
recommended_role
include_or_exclude
reason
```

## 8.1 Door-to-door travel burden

Phải đo toàn bộ hành trình:

- Walking access.
- Waiting.
- In-vehicle time.
- Transfers.
- Egress.
- Parking search.
- Parking walk.
- Ride-hailing wait.
- Schedule coordination.

Không dùng chỉ in-vehicle time.

## 8.2 Reliability

Candidate measures:

- P90 travel time.
- Buffer time index.
- Standard deviation.
- Headway regularity.
- On-time arrival probability.
- Peak/off-peak variation.
- Rain-day variation.

Reliability nên vào generalized cost nếu có thể quy đổi sang generalized minutes.

## 8.3 Mixed-traffic safety and conflict exposure

Candidate measures:

- Crash density.
- Motorcycle-related crash rate.
- Pedestrian crash risk.
- Near-miss rate.
- Time-to-collision.
- Post-encroachment time.
- Forced lane-change exposure.
- Bus–motorcycle conflict intensity.
- Intersection crossing risk.

Nếu không có conflict data tốt, giữ safety là diagnostic layer thay vì đưa vào composite.

## 8.4 Pedestrian continuity and usable walkability

Không đồng nhất walking distance với walkability.

Candidate measures:

- Usable sidewalk coverage.
- Sidewalk obstruction rate.
- Effective sidewalk width.
- Safe crossing availability.
- Crossing delay.
- Number of major-road crossings.
- Shade coverage.
- Flood-prone walking segments.
- Lighting.
- Universal access barriers.
- Percentage of route requiring walking in carriageway.

Có thể điều chỉnh impedance:

```text
EffectiveWalkTime =
ObservedWalkTime × WalkPenaltyFactor
```

## 8.5 Motorcycle dependency and behavioral inertia

Candidate variables:

- Motorcycle ownership.
- Habit strength.
- Perceived behavioral control.
- Trip-chaining needs.
- Need to carry children or goods.
- Parking convenience.
- License ownership.
- Social norm.
- Weather protection perception.
- Willingness to transfer.

Không đưa trực tiếp vào spatial index nếu chỉ có survey nhỏ. Có thể dùng để:

- Estimate coefficients.
- Segment latent classes.
- Validate RAC.
- Explain mismatch between accessibility and actual mode choice.

## 8.6 Ride-hailing and motorcycle taxi

Phải phân biệt ba vai trò:

1. Substitute for private motorcycle.
2. Competitor to public transport.
3. First/last-mile feeder to public transport.

Candidate measures:

- Ride-hailing wait time.
- Price.
- Surge variability.
- Pickup/drop-off suitability.
- Integration with transit stations.
- Share of trips connecting to transit.
- Additional vehicle-kilometres.
- Curb conflict.

Không mặc định ride-hailing là sustainable.

## 8.7 Affordability

Candidate measures:

```text
MonthlyMobilityCost / HouseholdIncome
```

Hoặc:

```text
TripCost / DailyIncome
```

Cần tính:

- Bus fare.
- Transfer fare.
- Motorcycle fuel.
- Parking.
- Maintenance.
- Ride-hailing.
- Opportunity cost of time.

Affordability có thể nằm trong generalized cost hoặc báo cáo như equity diagnostic.

## 8.8 Climate and weather exposure

Candidate measures:

- Shade coverage.
- Heat exposure.
- Rain exposure.
- Flood risk.
- Shelter at stops.
- Service disruption during heavy rain.
- Seasonal travel-time penalty.

Không chỉ dùng annual climate averages. Phải xem yếu tố này thay đổi access/egress burden như thế nào.

## 8.9 Accessibility for vulnerable groups

Candidate measures:

- Step-free transit access.
- Barrier-free sidewalks.
- Safe crossing time.
- Seating and shelter.
- Vehicle boarding accessibility.
- Distance tolerance.
- Personal safety perception.
- Night accessibility.

Ưu tiên group-specific impedance thay vì một universal score.

---

# 9. Nhiệm vụ 5 — Thiết kế weighting protocol

## 9.1 Nguyên tắc bắt buộc

Không được coi một bộ weight duy nhất là “true weights”.

Phải phân biệt:

### Normative weights

Phản ánh giá trị xã hội hoặc mục tiêu chính sách.

Ví dụ:

- Economic opportunity không được phép lấn át healthcare chỉ vì số chuyến đi làm nhiều hơn.
- Access for vulnerable groups có thể được ưu tiên dù trip frequency thấp.

### Revealed-demand weights

Phản ánh hành vi đi lại hiện tại.

Rủi ro:

- Nội sinh với cấu trúc đô thị hiện tại.
- Có thể tái tạo motorcycle dependence.
- Nhóm yếu thế có ít chuyến đi vì bị hạn chế tiếp cận, không phải vì nhu cầu thấp.

### Behavioral utility coefficients

Ước lượng trade-off giữa:

- Time.
- Cost.
- Reliability.
- Transfer.
- Walking.
- Safety.
- Comfort.

### Data-driven statistical weights

PCA, factor analysis, entropy hoặc CRITIC chỉ phản ánh cấu trúc dữ liệu, không tự động phản ánh social importance.

## 9.2 Weighting strategy đề xuất

Phải so sánh tối thiểu bốn specifications:

### W0 — Current normative prior

```text
economic = 0.40
higher_education = 0.20
tertiary_healthcare = 0.20
commercial_services = 0.20
```

### W1 — Equal domain weights

```text
0.25 / 0.25 / 0.25 / 0.25
```

### W2 — Trip-purpose-derived weights

Dùng UTM-Hanoi hoặc dữ liệu travel survey, nhưng phải báo cáo rõ mapping và endogenous-demand limitation.

### W3 — Stakeholder/expert weights

Có thể dùng Delphi, AHP hoặc Best-Worst Method, với:

- Nhóm chuyên gia đa dạng.
- Kiểm tra consistency.
- Báo cáo phân tán.
- Không lấy trung bình duy nhất nếu có bất đồng lớn.

### W4 — Hybrid weights

Kết hợp:

```text
HybridWeight =
λ × NormativeWeight
+ (1 - λ) × EmpiricalWeight
```

Phải sensitivity test với nhiều giá trị `λ`, không tự đặt một giá trị duy nhất.

## 9.3 Behavioral coefficient estimation

Nếu có survey stated/revealed preference, ưu tiên:

- Multinomial logit.
- Mixed logit.
- Latent class choice model.
- Hybrid choice model nếu có latent constructs.

Phải ước lượng:

- Value of travel time.
- Reliability ratio.
- Transfer penalty.
- Walking penalty.
- Cost sensitivity.
- Heterogeneity giữa các nhóm.

## 9.4 Weight promotion rules

Một bộ weight chỉ được promote thành primary nếu:

- Có theoretical justification.
- Có evidence phù hợp với Hà Nội hoặc Việt Nam.
- Không tạo domain domination.
- Kết quả ổn định qua bootstrap/sensitivity.
- Không làm giảm interpretability.
- Không tái tạo bất bình đẳng hiện có mà không thảo luận.
- Có performance tốt hơn hoặc ít nhất không kém baseline trong validation.

## 9.5 Deliverable

Tạo:

```text
outputs/methods/weighting_protocol.md
outputs/methods/weight_specifications.csv
```

---

# 10. Nhiệm vụ 6 — Validation framework

Validation phải vượt ra ngoài việc chạy sensitivity đơn giản.

## 10.1 Content validity

- Literature mapping.
- Expert review.
- Stakeholder review.
- Kiểm tra thiếu/trùng construct.

## 10.2 Construct validity

Kiểm tra:

- NAI có thực sự đo local access không?
- MAI có đo metropolitan opportunity reach không?
- RAC có đo competitiveness không?
- MTF có khác với NAI/RAC không?
- SMCI cao có đúng với các khu vực được kỳ vọng là có sustainable mobility capability không?

Dùng:

- Correlation.
- VIF.
- Factor structure nếu phù hợp.
- Known-groups comparison.
- Spatial pattern review.

## 10.3 Criterion validity

So sánh với:

- Observed mode share.
- Transit boarding.
- Motorcycle use.
- Stated willingness to switch.
- Trip frequency.
- Travel satisfaction.
- Actual accessibility complaints.
- Household mobility cost.

## 10.4 Predictive validity

Kiểm tra SMCI có dự báo được:

- Transit adoption.
- Reduced motorcycle use.
- Higher non-motorized mode use.
- Lower generalized travel burden.
- Higher opportunity participation.

Dùng train/test split hoặc cross-validation khi có đủ mẫu.

## 10.5 Policy validity

Kiểm tra chỉ số phản ứng hợp lý trước các interventions:

- Thêm tuyến bus.
- Tăng frequency.
- Cải thiện transfer.
- Cải thiện sidewalk.
- Tăng shade.
- Giảm parking advantage.
- Thêm safe crossing.
- Tích hợp first/last-mile.

## 10.6 Spatial validity

- Boundary discontinuity.
- Moran’s I.
- Local spatial autocorrelation.
- Urban core vs periphery.
- Planned vs unplanned area.
- Data-confidence parity.

## 10.7 Robustness

Bắt buộc kiểm tra:

- 600/800/1000/1200 m NAI thresholds.
- Alternative decay functions.
- Alternative normalization.
- Additive vs multiplicative aggregation.
- Zero-sensitive vs epsilon-adjusted product.
- Weight scenarios W0–W4.
- Motorcycle speed ±20%.
- Transit wait/reliability penalties.
- Proxy vs strict opportunity magnitudes.
- M0 vs M1 vs M2.
- Population weighting.
- Excluding low-confidence destinations.
- Different clipping caps.

## 10.8 Uncertainty

Tạo uncertainty intervals bằng:

- Bootstrap.
- Monte Carlo over uncertain inputs.
- Weight distributions.
- Travel-time variability.
- POI magnitude confidence tiers.

Output:

```text
SMCI_mean
SMCI_p05
SMCI_p95
classification_probability
```

## 10.9 Model comparison table

Tạo:

```text
outputs/validation/model_comparison.csv
```

Các cột:

```text
model
weight_spec
aggregation
mean_score
zero_share
rank_correlation_with_M0
typology_kappa_with_M0
vif_max
predictive_metric
policy_response_metric
spatial_stability
uncertainty_width
interpretability_rating
data_burden
recommended_status
reason
```

---

# 11. Nhiệm vụ 7 — Quy tắc quyết định cấu trúc cuối cùng

Agents phải dùng decision gate.

## Gate A — Có cần thay RAC_time bằng RAC_GC không?

Promote nếu:

- Có dữ liệu cost/reliability/transfer đủ tốt.
- Coefficients có evidence.
- Predictive hoặc criterion validity tốt hơn.
- Không mất interpretability.
- Kết quả không bị một thành phần chi phối.

Nếu chưa đủ, giữ RAC_time là primary và RAC_GC là robustness/future extension.

## Gate B — Có cần thêm MTF vào SMCI không?

Promote nếu:

- MTF đo một construct độc lập.
- Dữ liệu không chủ yếu là weak proxy.
- Cải thiện validity.
- Stable across sensitivity.
- Không double count.

Nếu không, giữ MTF như diagnostic dashboard.

## Gate C — Có cần thay phép nhân không?

Phép nhân được giữ nếu research construct yêu cầu non-compensability.

Phải so sánh:

```text
Product
Geometric mean
Arithmetic mean
Minimum operator
Partially compensatory CES form
```

Lưu ý geometric mean của ba thành phần với số mũ bằng nhau là biến đổi đơn điệu của product khi tất cả giá trị dương; không được xem đó là một robustness hoàn toàn độc lập.

## Gate D — Có nên có một SMCI duy nhất?

Nếu group heterogeneity quá lớn, ưu tiên:

- SMCI core.
- Group-specific profiles.
- Equity dashboard.
- Uncertainty layer.

Không ép mọi vấn đề vào một scalar.

---

# 12. Nhiệm vụ 8 — Cập nhật data pipeline và code

## 12.1 Không phá vỡ reproducibility hiện tại

Trước mọi thay đổi:

- Chạy toàn bộ tests.
- Lưu baseline outputs.
- Ghi commit/hash hoặc timestamp.
- Không overwrite raw/interim files không có versioning.

## 12.2 Cấu trúc module đề xuất

```text
src/
  accessibility/
    nai.py
    mai.py
  competitiveness/
    rac_time.py
    generalized_cost.py
    reliability.py
  mixed_traffic/
    pedestrian_continuity.py
    safety_conflict.py
    climate_exposure.py
    intermodal_integration.py
  weighting/
    normative.py
    empirical.py
    hybrid.py
  validation/
    construct.py
    criterion.py
    predictive.py
    robustness.py
    uncertainty.py
```

Điều chỉnh theo cấu trúc repository thực tế, không tạo duplicate architecture nếu đã có module tương đương.

## 12.3 Configuration

Mọi weight và assumption phải nằm trong config, không hard-code.

Ví dụ:

```yaml
model:
  version: M0

nai:
  threshold_m: 800

mai:
  domain_weights:
    economic: 0.40
    higher_education: 0.20
    tertiary_healthcare: 0.20
    commercial_services: 0.20

rac:
  type: time

generalized_cost:
  beta_time: null
  beta_reliability: null
  beta_cost: null
  beta_transfer: null
  beta_access_egress: null
  beta_parking: null

mixed_traffic:
  enabled: false
```

## 12.4 Audit fields

Mỗi output cell phải có:

```text
model_version
weight_version
normalization_version
data_version
nai_threshold
rac_type
mtf_enabled
uncertainty_run
```

## 12.5 Tests bắt buộc

- Higher transit time must not improve RAC.
- Lower transit wait must improve or preserve RAC.
- Higher motorcycle cost must improve transit competitiveness.
- Removing a reachable opportunity must not increase MAI.
- Improved sidewalk continuity must not reduce effective walk access.
- Identical scenarios must produce zero delta.
- Shared normalization must preserve scenario comparability.
- Weight sums must equal 1 where required.
- No hidden NaN-to-zero conversion.
- No negative accessibility after normalization.
- Classification must be deterministic under fixed inputs.
- Low-confidence exclusion sensitivity must run end to end.

## 12.6 Deliverables kỹ thuật

Tạo hoặc cập nhật:

```text
configs/smci_models.yaml
scripts/run_smci_model_comparison.py
scripts/run_weight_sensitivity.py
scripts/run_uncertainty_analysis.py
scripts/run_construct_validation.py
scripts/run_policy_scenarios.py
tests/test_generalized_cost.py
tests/test_weighting.py
tests/test_model_comparison.py
```

Tên file có thể điều chỉnh theo repository, nhưng chức năng phải được giữ.

---

# 13. Nhiệm vụ 9 — Thiết kế policy scenarios

Phải tạo các scenario có ý nghĩa quy hoạch, không chỉ thay đổi tham số tùy ý.

## Scenario P0 — Baseline

Current conventional transit hoặc pre-intervention baseline.

## Scenario P1 — VinBus/current intervention

Giữ scenario đang có.

## Scenario P2 — Frequency improvement

- Giảm headway.
- Giảm expected wait.
- Kiểm tra distributional benefit.

## Scenario P3 — Sidewalk and crossing improvement

- Giảm access/egress penalty.
- Tăng usable catchment.
- Không thay đổi tuyến bus.

## Scenario P4 — Integrated intervention

- Frequency.
- Sidewalk.
- Transfer.
- Shade/shelter.
- Station access.

## Scenario P5 — Motorcycle advantage reduction

Chỉ dùng như policy sensitivity, ví dụ:

- Tăng parking burden.
- Giảm free curb parking.
- Tăng generalized monetary cost.

Không trình bày như policy recommendation nếu chưa đánh giá equity.

## Scenario P6 — Ride-hailing feeder integration

- Giảm first/last-mile burden.
- Thêm feeder cost.
- Kiểm tra thay thế hay bổ trợ transit.

## Outputs

- Delta SMCI.
- Population benefited.
- Vulnerable-group benefit.
- Cells remaining motorcycle lock-in.
- Cost-effectiveness proxy nếu có.
- Spatial map.
- Uncertainty intervals.

---

# 14. Nhiệm vụ 10 — Cập nhật proposal

Tạo phiên bản:

```text
proposal_v8_smci_vn.md
```

Không sửa proposal chỉ bằng cách chèn thêm một section dài. Phải cập nhật nhất quán toàn bộ:

## Sections cần cập nhật

1. Title nếu cần.
2. Summary.
3. Research problem.
4. Research questions.
5. Contribution.
6. Literature review.
7. Data.
8. Index construction.
9. Weighting rationale.
10. Vietnam mixed-traffic extension.
11. Validation.
12. Robustness.
13. Expected argument.
14. Limitations.
15. Work plan.
16. Reproducibility.
17. References.

## Nội dung mới bắt buộc

### Evidence audit statement

Nêu rõ:

- Existing frameworks have relatively strong evidence for indicator relevance and institutional usability.
- Exact weights are often normative, expert-based or context-specific.
- Universal transfer of weights is not assumed.

### Contribution statement

Nêu rõ SMCI:

- Là spatially explicit.
- Dual-scale.
- Mode-competitive.
- Motorcycle-relative.
- Policy-sensitive.
- Complementary rather than universally substitutive.

### Weighting statement

Nêu rõ:

- Current weights are normative priors.
- UTM-derived weights are sensitivity evidence.
- Trip frequency does not equal social importance.
- Future behavioral estimation is a planned extension.

### Mixed-traffic statement

Nêu rõ:

- Reliability.
- Door-to-door cost.
- Pedestrian continuity.
- Safety conflict.
- Ride-hailing.
- Affordability.
- Climate exposure.

Nhưng phải nói rõ yếu tố nào đã triển khai và yếu tố nào mới là research agenda.

### Validation statement

Phân biệt:

- Plausibility check.
- Calibration.
- Validation.
- Predictive validation.

Không gọi 10 OD pairs là full validation.

---

# 15. Deliverables cuối cùng

Agents phải bàn giao đầy đủ:

```text
outputs/evidence/indicator_evidence_matrix.csv
outputs/evidence/evidence_audit.md
outputs/concept/smci_contribution_and_positioning.md
outputs/concept/smci_vn_framework.md
outputs/methods/weighting_protocol.md
outputs/methods/weight_specifications.csv
outputs/methods/model_specification.md
outputs/validation/model_comparison.csv
outputs/validation/validation_report.md
outputs/validation/uncertainty_report.md
outputs/policy/policy_scenario_report.md
outputs/review/red_team_review.md
outputs/review/decision_log.md
proposal_v8_smci_vn.md
```

Nếu một deliverable chưa thể hoàn thành vì thiếu dữ liệu, không được giả lập kết quả. Phải ghi:

- Dữ liệu còn thiếu.
- Tại sao cần.
- Nguồn khả thi.
- Proxy tạm thời.
- Rủi ro.
- Việc nào vẫn có thể hoàn thành ngay.

---

# 16. Phân công agents đề xuất

## Agent A — Evidence and literature audit

Chịu trách nhiệm:

- Evidence matrix.
- Nguồn primary.
- Weighting and aggregation audit.
- Transferability to Vietnam.

## Agent B — Concept and theory

Chịu trách nhiệm:

- Construct definition.
- Contribution positioning.
- Nested models M0–M3.
- Avoidance of conceptual overclaiming.

## Agent C — Transport modeling

Chịu trách nhiệm:

- Generalized cost.
- Reliability.
- Door-to-door impedance.
- Policy scenarios.
- Motorcycle/transit comparison.

## Agent D — Vietnam mixed-traffic specialist

Chịu trách nhiệm:

- Pedestrian continuity.
- Mixed-traffic safety.
- Ride-hailing.
- Motorcycle dependency.
- Climate and local context.

## Agent E — Statistics and weighting

Chịu trách nhiệm:

- W0–W4.
- Behavioral coefficients.
- Bootstrap.
- Uncertainty.
- Model comparison.

## Agent F — Data and engineering

Chịu trách nhiệm:

- Config-driven implementation.
- Scripts.
- Tests.
- Reproducibility.
- Data provenance.

## Agent G — Red team

Chịu trách nhiệm:

- Tìm double counting.
- Tìm arbitrary assumptions.
- Kiểm tra overclaim.
- Kiểm tra false validation.
- Kiểm tra equity risks.
- Kiểm tra data leakage hoặc circularity.
- Đề xuất rejection criteria.

## Agent H — Proposal editor

Chỉ viết proposal sau khi A–G hoàn tất outputs chính.

Chịu trách nhiệm:

- Đồng bộ số liệu.
- Đồng bộ terminology.
- Giữ claims đúng với evidence.
- Không đưa future work thành completed work.
- Cập nhật references.

---

# 17. Giao thức làm việc giữa agents

Mỗi agent phải trả kết quả theo format:

```text
## Task completed
## Files inspected
## Evidence used
## Decisions made
## Assumptions
## Outputs created
## Tests performed
## Findings
## Risks
## Open issues
## Recommended next action
```

Mọi quyết định phương pháp phải ghi vào:

```text
outputs/review/decision_log.md
```

Mỗi quyết định gồm:

```text
decision_id
date
question
options_considered
selected_option
evidence
reason
risk
reversal_condition
affected_files
```

Không được để các agents tự ý dùng terminology khác nhau. Thuật ngữ chuẩn:

```text
Neighborhood Accessibility Index (NAI)
Metropolitan Accessibility Index (MAI)
Relative Accessibility Competitiveness (RAC)
Generalized-Cost RAC (RAC_GC)
Mixed-Traffic Feasibility (MTF)
Sustainable Mobility Capability Index (SMCI)
```

---

# 18. Tiêu chí nghiệm thu

Công việc chỉ được xem là hoàn thành khi đáp ứng toàn bộ:

## Evidence

- Có audit tách indicator selection, weighting và aggregation.
- Ưu tiên primary/official sources.
- Không có citation không được kiểm chứng.
- Có đánh giá evidence strength.

## Concept

- SMCI được định vị là complementary.
- Đóng góp dual-scale và motorcycle-relative được làm rõ.
- Không overclaim full sustainability.

## Methods

- Có baseline M0.
- Có nested alternatives.
- Có weighting alternatives.
- Có promotion/rejection rules.
- Có uncertainty plan.

## Vietnam relevance

- Mixed traffic được chuyển thành measurable constructs.
- Không chỉ liệt kê vấn đề.
- Ride-hailing không mặc định là sustainable.
- Walking distance không đồng nhất với usable walkability.
- Equity không bị nén tùy tiện vào một weight.

## Engineering

- Config-driven.
- Reproducible.
- Tests pass.
- Outputs versioned.
- Data provenance retained.

## Validation

- Có construct, criterion, policy và robustness checks.
- Không gọi plausibility check là full validation.
- Có model comparison.
- Có uncertainty reporting.

## Proposal

- Proposal mới nhất quán với code và outputs.
- Mọi con số được tái tạo từ pipeline.
- Future work và completed work được phân biệt rõ.
- Limitations được giữ trung thực.

---

# 19. Những điều agents không được làm

- Không tự đặt weights mới rồi gọi là evidence-based.
- Không dùng trip-purpose shares như social-value weights mà không cảnh báo.
- Không thêm quá nhiều chỉ báo để tạo “comprehensiveness”.
- Không double count MAI trong RAC.
- Không gộp safety, affordability, equity và climate vào một modifier nếu thiếu dữ liệu.
- Không thay primary model chỉ vì kết quả đẹp hơn.
- Không xóa baseline M0.
- Không dùng separately normalized scenario scores để tính delta.
- Không biến proxy thành observed data.
- Không gọi pseudo-GTFS là official GTFS.
- Không gọi 10 OD checks là full calibration.
- Không tuyên bố causal effect nếu chỉ có scenario simulation.
- Không coi planned-project performance là urban-scale sustainability.
- Không đồng nhất access với actual use.
- Không viết proposal trước khi hoàn thành evidence và method audit.

---

# 20. Thứ tự thực hiện bắt buộc

```text
Step 1: Freeze and reproduce current baseline.
Step 2: Complete evidence audit.
Step 3: Finalize contribution positioning.
Step 4: Build the candidate-dimension decision table.
Step 5: Specify M0–M3 and W0–W4.
Step 6: Assess data feasibility.
Step 7: Implement only feasible extensions.
Step 8: Run validation and uncertainty.
Step 9: Red-team all claims and methods.
Step 10: Decide the promoted primary specification.
Step 11: Update the full proposal.
Step 12: Generate final supervisor/reviewer package.
```

Không được bỏ qua Step 1 để tránh mất khả năng so sánh với proposal hiện tại.

---

# 21. Kết quả khoa học mong muốn

Phiên bản cuối cùng cần có khả năng đưa ra lập luận sau, nếu evidence thực sự hỗ trợ:

> Existing sustainable urban mobility frameworks provide strong institutional and conceptual guidance on what should be monitored, but their numerical weights and aggregation rules are often normative, expert-based or weakly validated across contexts. The proposed SMCI does not seek to replace these frameworks. Instead, it addresses a specific gap by measuring whether local and metropolitan opportunities are jointly accessible through modes that are competitive with motorcycles. Its Vietnam-specific extension evaluates whether this capability remains feasible under mixed-traffic conditions, unreliable service, discontinuous pedestrian infrastructure, ride-hailing competition, affordability constraints and climate exposure.

Nếu evidence không hỗ trợ toàn bộ lập luận này, agents phải thu hẹp claim thay vì điều chỉnh kết quả để phù hợp với claim.

---

# 22. Lệnh bắt đầu cho nhóm agents

Bắt đầu bằng việc đọc toàn bộ hai tài liệu đầu vào và kiểm tra repository. Sau đó:

1. Tái tạo baseline proposal hiện tại.
2. Tạo evidence audit matrix.
3. Đánh dấu mọi weight, threshold, cap, decay function và aggregation rule trong proposal.
4. Phân loại từng quyết định thành:
   - empirically estimated;
   - institutionally standardized;
   - expert-derived;
   - normative;
   - operational assumption;
   - weak proxy.
5. Lập danh sách các quyết định cần giữ, kiểm tra, thay thế hoặc hạ xuống robustness.
6. Chỉ đề xuất công thức SMCI-VN cuối cùng sau khi evidence audit và data-feasibility assessment hoàn thành.
7. Ghi toàn bộ quyết định vào decision log.
8. Không chỉnh sửa proposal cuối cùng cho đến khi red-team review được hoàn tất.
