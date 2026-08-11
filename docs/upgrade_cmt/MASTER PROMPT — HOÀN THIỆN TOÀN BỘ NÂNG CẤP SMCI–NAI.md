# MASTER PROMPT — HOÀN THIỆN TOÀN BỘ NÂNG CẤP SMCI–NAI

Bạn đang làm việc trong repository:

`Cuki2910/mobility_capability_study`

Mục tiêu là hoàn thiện toàn bộ gói nâng cấp phương pháp và publication pipeline được mô tả trong ba tài liệu:

1. `agent_prompt_SMCI_geometric_mean(1).md`
2. `De_xuat_nang_cap_chi_so_SMCI_hien_tai(1).docx`
3. `Ke_hoach_nang_cap_phuong_phap_NAI_theo_Bruno.docx`

Không chỉ sửa manuscript. Phải sửa code nguồn, tests, pipeline, outputs, documentation, audit, figures, tables và tất cả canonical artifacts liên quan.

Không được tạo số liệu giả, không được sửa trực tiếp generated output để làm khớp manuscript, và không được tuyên bố một hạng mục đã hoàn thành khi dữ liệu cần thiết chưa tồn tại.

---

# 1. QUYẾT ĐỊNH PHƯƠNG PHÁP BẮT BUỘC

## 1.1. Chuyển SMCI primary sang equal-weight geometric mean

Công thức primary mới:

\[
SMCI_i =
\left(
NAI_{norm,i}\times MAI_{norm,i}\times RAC_{norm,i}
\right)^{1/3}
\]

Định nghĩa chính thức:

> SMCI là equal-weight geometric mean của normalized NAI, MAI và RAC; đây là composite multiplicative, weak-link-sensitive, zero-preserving trên thang 0–1.

Phải giữ các thuộc tính:

- NAI, MAI và RAC vẫn jointly necessary.
- Một component bằng 0 làm SMCI bằng 0.
- Geometric mean là cubic-root transformation của product.
- Thứ hạng cell dương không đổi so với product.
- Dấu của Scenario B minus Scenario A không đổi.
- Zero-SMCI cell set không đổi.
- Product versus geometric mean không phải robustness test độc lập.
- Additive alternative tiếp tục là aggregation robustness chính.
- Minimum-component index được bổ sung như extreme bottleneck diagnostic.

## 1.2. Giữ product để audit và backward traceability

Không xóa product khỏi pipeline.

Tên biến canonical mới:

- `SMCI_A`: geometric-mean SMCI Scenario A.
- `SMCI_B`: geometric-mean SMCI Scenario B.
- `Delta_SMCI`: `SMCI_B - SMCI_A`.

Tên biến legacy/audit:

- `SMCI_product_A`
- `SMCI_product_B`
- `Delta_SMCI_product`

Tên robustness/diagnostic:

- `SMCI_additive_A`
- `SMCI_additive_B`
- `SMCI_min_A`
- `SMCI_min_B`

Bump schema version của `outputs/headline_metrics.json`.

Không duy trì hai định nghĩa khác nhau dưới cùng một tên `SMCI_A` hoặc `SMCI_B`.

## 1.3. Typology primary không được đổi vì thay thang SMCI

Typology primary tiếp tục dựa trên:

- NAI;
- Metropolitan Competitiveness Score, MCS;
- rank-based theory-first split.

SMCI không được dùng trực tiếp để tạo typology primary.

Thêm invariant test xác nhận chuyển product sang geometric mean không làm thay đổi typology primary.

## 1.4. Giữ phạm vi construct

SMCI tiếp tục là framework về place-based sustainable mobility accessibility capability gồm:

- Neighborhood Accessibility Index — NAI;
- Metropolitan Accessibility Index — MAI;
- Relative Accessibility Competitiveness — RAC.

Không đưa trực tiếp safety, affordability, emissions, environment, equity, reliability hoặc mixed traffic thành các trụ cột mới trong phép tổng hợp SMCI.

Các chiều đó phải là:

- audit layer;
- sensitivity;
- supplementary analysis;
- hoặc future-research protocol.

---

# 2. NGUYÊN TẮC THỰC THI

## 2.1. Làm việc trên branch riêng

Tạo branch:

`feat/complete-smci-nai-upgrade`

Không commit trực tiếp lên `main`.

Đọc trước khi sửa:

- `AGENTS.md`
- `CLAUDE.md`
- `README.md`
- `docs/data_sources.md`
- `docs/decisions.md`
- `docs/metrics_reference.md`
- `config/pipeline.json`
- `plan.md`
- `paper/paper_draft.md`
- `proposal/proposal_v7.md`

Kiểm tra `--help` của các scripts trước khi gọi. Không đoán command signature.

## 2.2. Không thay đổi raw data

Không chỉnh sửa thủ công:

- `data/raw/`
- GraphML;
- GeoPackage nguồn;
- GTFS;
- WorldPop raster;
- POI raw downloads.

Mọi derived data phải được tạo bằng script tái lập được.

## 2.3. Không hand-edit generated artifacts

Các file trong `outputs/` phải được tạo lại từ code.

Nếu cần sửa nội dung generated Markdown, phải sửa generator tương ứng trước.

Mỗi generated output quan trọng cần ghi:

- input path;
- input hash;
- config;
- timestamp;
- code/commit SHA nếu pipeline hiện hỗ trợ.

## 2.4. Không bịa dữ liệu

Khi thiếu:

- behavioral validation data;
- current GTFS;
- reliability observations;
- local value-of-time;
- transfer penalty;
- observed mixed-traffic friction;
- West Tay Mo observed magnitude data;

phải:

1. viết code contract hoặc input schema;
2. tạo protocol thu thập dữ liệu;
3. để trạng thái `NOT_RUN_DATA_REQUIRED`;
4. liệt kê chính xác dữ liệu còn thiếu;
5. không sinh ra estimate giả để lấp chỗ trống.

---

# 3. PHASE 0 — BASELINE LOCK VÀ AUDIT

Trước khi sửa code:

1. Ghi current branch và commit SHA.
2. Chạy toàn bộ baseline gates.
3. Lưu test results.
4. Khóa hashes của các canonical inputs và outputs.
5. Tạo baseline report riêng cho upgrade.

Các lệnh tối thiểu:

```bash
python -m pytest tests/ -q
python scripts/agent_gate.py
python scripts/check_document_consistency.py
python scripts/project_self_audit.py
```

Kiểm tra cách dùng và chạy thêm:

```bash
python scripts/freeze_geospatial_baseline.py --help
python scripts/baseline_integrity.py --help
python scripts/graph_health.py --help
```

Tạo:

- `outputs/upgrade/baseline_lock.json`
- `outputs/upgrade/baseline_lock.md`

Baseline report phải ghi ít nhất:

- commit SHA;
- 462 grid cells;
- product-based mean SMCI A/B hiện tại;
- product-based delta groups;
- zero-access cells;
- population exposure;
- typology counts;
- VIF;
- motorcycle validation;
- hashes của grid, metrics, WorldPop, boundaries và networks;
- test/gate status.

Không dùng baseline product values làm geometric-mean values mới.

---

# 4. PHASE 1 — DECISION RECORD VÀ DATA CONTRACT

Thêm một decision record mới trong `docs/decisions.md`.

Decision phải nêu:

- geometric mean được promote thành primary reporting scale;
- product được giữ để legacy audit;
- product và geometric mean có cùng ordinal ranking nhưng khác reporting scale;
- không dùng product-versus-geometric-mean làm robustness;
- additive tiếp tục là aggregation sensitivity;
- minimum component là bottleneck diagnostic;
- tất cả cell-level, summary, boundary và spatial outputs phải được regenerate;
- typology primary không thay đổi vì không phụ thuộc SMCI;
- Local Moran/LISA phải chạy lại vì nonlinear transformation có thể làm thay đổi spatial standardization và local significance.

Cập nhật data contract trong:

- `config/pipeline.json`;
- `src/headline_metrics.py`;
- output schemas;
- test fixtures.

Thêm explicit field mô tả:

```json
{
  "smci_primary_operator": "equal_weight_geometric_mean",
  "smci_legacy_operator": "product",
  "smci_robustness_operator": "additive",
  "smci_bottleneck_operator": "minimum_component"
}
```

---

# 5. PHASE 2 — IMPLEMENT GEOMETRIC-MEAN SMCI

## 5.1. Sửa `src/accessibility.py`

Tổ chức API rõ ràng, không để tên hàm gây nhầm:

```python
compute_smci_product(...)
compute_smci_product_from_normalized(...)

compute_smci_geometric(...)
compute_smci_geometric_from_normalized(...)

compute_smci_additive(...)
compute_smci_additive_from_normalized(...)

compute_smci_min(...)
compute_smci_min_from_normalized(...)
```

Hàm geometric primary phải tương đương:

```python
product = nai_norm * mai_norm * rac_norm
smci = np.cbrt(product)
```

Phải xử lý:

- zero;
- arrays;
- NaN theo policy thống nhất;
- values ngoài `[0,1]`;
- shape mismatch;
- deterministic output.

Không dùng epsilon trong primary formula vì epsilon phá zero-preserving property.

## 5.2. Sửa `src/pilot.py`

Tại mỗi cell, tính:

- normalized NAI;
- shared-normalized MAI A/B;
- shared-normalized RAC A/B;
- product A/B;
- geometric A/B;
- additive A/B;
- minimum A/B;
- các delta tương ứng.

Canonical:

```text
SMCI_A = geometric A
SMCI_B = geometric B
Delta_SMCI = geometric B - geometric A
```

Legacy:

```text
SMCI_product_A
SMCI_product_B
Delta_SMCI_product
```

Phải giữ các raw components và normalized components để audit.

## 5.3. Invariant tests bắt buộc

Thêm tests xác nhận:

1. `SMCI_geometric == cbrt(SMCI_product)` tại từng cell.
2. Zero product tương ứng zero geometric.
3. Positive-cell ordering giữa product và geometric giống nhau.
4. Spearman product versus geometric bằng 1 trong tập positive/non-tied thích hợp.
5. Dấu `Delta_SMCI` giống dấu `Delta_SMCI_product`.
6. Improved/unchanged/declined counts không đổi.
7. Zero-cell set không đổi.
8. Typology A/B không đổi.
9. Geometric values nằm trong `[0,1]`.
10. Không tính geometric mean của summary means.

## 5.4. Update toàn bộ consumers

Tìm tất cả các nơi sử dụng:

- `SMCI_A`
- `SMCI_B`
- `Delta_SMCI`
- `mean_SMCI`
- `product`
- `multiplicative`
- `geometric mean`
- `zero-access`
- `times higher`
- `ratio`
- `boundary`
- `hotspot`
- `scenario`

Cập nhật:

- `src/headline_metrics.py`
- `scripts/build_headline_snapshot.py`
- `scripts/run_pilot_metrics.py`
- `scripts/make_distribution_diagnostics.py`
- `scripts/compute_population_weighted_smci.py`
- `scripts/analyze_boundary_discontinuity.py`
- `scripts/analyze_spatial_autocorrelation.py`
- `scripts/make_pilot_maps.py`
- `scripts/make_combined_interactive_map.py`
- `scripts/make_paper_tables.py`
- `scripts/make_paper_figures.py`
- `scripts/make_supervisor_memo.py`
- `scripts/project_self_audit.py`
- tất cả sensitivity scripts;
- paper/proposal/docs.

## 5.5. Recalculate đúng cấp cell

Không được làm:

```text
cube_root(mean(product_SMCI))
```

Phải làm:

1. cube root ở từng cell;
2. sau đó mới tính mean, median, weighted mean, quantile và boundary summaries.

Tính lại:

- descriptive statistics;
- population-weighted statistics;
- scenario differences;
- positive-cell statistics;
- ratios và percentages;
- inside/outside results;
- boundary-distance bands;
- Global Moran;
- Local Moran/LISA;
- FDR results;
- maps và legends;
- abstract numbers;
- table values;
- figure annotations.

Tất cả “times higher” statements phải được kiểm tra lại. Báo cáo absolute difference kèm ratio hoặc percentage.

## 5.6. Tạo báo cáo chuyển thang

Tạo:

- `outputs/validation/smci_scale_transition.csv`
- `outputs/validation/smci_scale_transition.md`

Bảng old/new phải có:

- product mean A/B;
- geometric mean A/B;
- product delta mean;
- geometric delta mean;
- positive median A/B;
- population-weighted mean A/B;
- boundary inside/outside medians;
- boundary difference;
- scenario ratio;
- zero counts;
- improved/unchanged/declined counts;
- typology counts;
- Moran/LISA summaries;
- rank correlation;
- mọi headline number đã thay đổi.

Tách rõ:

- unchanged ordinal conclusions;
- changed numerical scale;
- spatial statistics cần recalculation;
- interpretation cần sửa.

---

# 6. PHASE 3 — NAI UPGRADE THEO BRUNO

Tạo module mới:

`src/neighborhood_access.py`

Tạo script chính:

`scripts/nai_bruno_robustness.py`

Không thay NAI primary trong vòng sửa này. NAI threshold-count 800 m tiếp tục là primary.

Các chỉ số mới là validation/robustness/supplementary.

## 6.1. Chuẩn hóa taxonomy POI neighborhood

Tạo configuration riêng, ví dụ:

`config/nai_categories.yml`

Mỗi POI phải có một primary neighborhood category.

Không double count một POI vào nhiều category trừ khi có rule được ghi rõ.

Bắt đầu từ taxonomy hiện có trong repo, nhưng phải đối chiếu với NAI definition trong paper và `docs/metrics_reference.md`.

Xuất bảng:

- category name;
- tags/rules;
- POI count;
- source coverage;
- missing/ambiguous count;
- manual-review requirement.

Tạo audit:

- `outputs/validation/nai_category_audit.csv`
- `outputs/validation/nai_category_audit.md`

## 6.2. Category Completeness Score — CCS

Tính:

\[
CCS_i(T)=\frac{1}{C}\sum_{c=1}^{C}I(t^{min}_{ic}\leq T)
\]

Thresholds:

- 600 m;
- 800 m primary;
- 1,000 m;
- 1,200 m.

Báo cáo cutoffs:

- CCS < 0.50;
- 0.50 ≤ CCS < 0.75;
- CCS ≥ 0.75.

Chạy sensitivity với completeness threshold:

- 0.50;
- 0.67;
- 0.75.

Xuất per-cell CCS và population-weighted coverage.

## 6.3. Neighborhood Proximity Time — NPT

Tính thời gian đi bộ đến K POI gần nhất theo category.

Configurations:

- K=3 primary robustness;
- K=1 sensitivity;
- K=5 sensitivity.

Khi category thiếu đủ K POI:

- không loại category khỏi mean;
- dùng predeclared cutoff penalty;
- primary cutoff: 20 phút;
- sensitivity cutoff phải được cấu hình và ghi rõ.

Tính:

- category-level NPT;
- aggregate NPT;
- NPT benefit, hướng “cao hơn là tốt hơn”.

Primary transformation:

```text
NPT_benefit = 1 - normalized_NPT
```

Normalization phải được ghi rõ và kiểm tra độ nhạy. Không để Scenario A/B dùng scale khác nhau.

## 6.4. Population coverage

Tính:

\[
F_{complete}(T,q)
\]

cho toàn bộ tổ hợp chính của:

- T = 600, 800, 1000, 1200 m;
- q = 0.50, 0.67, 0.75.

Tính:

- `F10`
- `F15`
- `F_zero`

Báo cáo song song:

- cell share;
- population share;
- built-cell share;
- built-population share nếu dữ liệu hỗ trợ.

Không diễn giải population coverage là observed walking behavior.

## 6.5. Population-weighted inequality

Triển khai:

- weighted mean NPT;
- weighted median;
- weighted percentiles;
- population-weighted Gini NPT.

Thêm unit tests cho weighted Gini:

- equal values → Gini 0;
- simple two-point case;
- zero/negative weight rejection;
- missing values;
- deterministic behavior.

Không dùng Gini đơn độc để tuyên bố equity. Luôn báo cáo cùng mean, median, coverage và zero-access.

## 6.6. Local-access classification supplementary

Tạo nhãn:

- Zero access;
- Low access;
- Incomplete access;
- Abundant but incomplete;
- Locally complete.

Đây là classification để diễn giải NAI.

Không thay thế typology chính:

- Integrated Capability;
- Fragmented Capability;
- Transit-Dependent;
- Motorcycle Lock-in.

## 6.7. SMCI_NPT robustness

Tính:

\[
SMCI_{NPT,i}
=
NPT_{benefit,i}\times MAI_{norm,i}\times RAC_{norm,i}
\]

Vì SMCI primary mới dùng geometric mean, phải tạo hai supplementary forms rõ ràng:

```text
SMCI_NPT_product
SMCI_NPT_geometric
```

Trong đó geometric supplementary:

\[
SMCI_{NPT}^{GM}
=
(NPT_{benefit}\times MAI_{norm}\times RAC_{norm})^{1/3}
\]

Không nhập nhằng tên.

So sánh với primary:

- Spearman;
- Pearson nếu phù hợp;
- zero-cell count;
- typology agreement khi NPT benefit thay NAI trong supplementary typology;
- changed cells;
- boundary discontinuity;
- spatial clustering;
- population exposure.

## 6.8. Outputs NAI–Bruno

Tạo tối thiểu:

- `outputs/validation/nai_bruno_cells.csv`
- `outputs/validation/nai_bruno_cells.gpkg`
- `outputs/validation/nai_bruno_summary.csv`
- `outputs/validation/nai_bruno_summary.md`
- `outputs/validation/nai_population_coverage.csv`
- `outputs/validation/nai_inequality.md`
- `outputs/validation/smci_npt_robustness.md`

Maps:

- NAI;
- CCS;
- NPT;
- NPT benefit;
- zero/incomplete/complete access;
- SMCI_NPT;
- boundary profiles.

Tạo table và figure outputs tương ứng cho paper.

---

# 7. PHASE 4 — HỢP NHẤT VÀ HOÀN THIỆN SENSITIVITY

Repo đã có nhiều sensitivity phân tán. Phải hợp nhất chúng vào canonical strict-observed specification.

## 7.1. MAI weight sensitivity

Giữ và regenerate:

- default;
- equal;
- job-heavy;
- econ-light;
- service-health-heavy;
- UTM-derived.

Bổ sung deterministic random-weight stress test.

Khuyến nghị:

- fixed seed `2026`;
- uniform simplex/Dirichlet stress test;
- ít nhất 1,000 draws nếu computationally khả thi;
- ghi rõ đây là methodological stress test, không phải behavioral weight distribution.

Không rebuild full network cho mỗi draw nếu có thể tách sẵn domain-level accessibility contributions.

Output:

- distribution của mean SMCI;
- population-weighted mean;
- improved share;
- typology kappa;
- number relabelled;
- per-cell percentile envelope;
- probability cell giữ typology;
- probability cell thuộc zero/low capability.

## 7.2. Time-decay sensitivity

Canonical runs:

- linear 20–40;
- linear 30–60 primary;
- linear 45–90;
- exponential 30–60.

Logistic chỉ bổ sung khi parameterization được giải thích rõ; không bịa behavioral coefficients.

Phải báo cáo:

- absolute levels;
- ranking;
- kappa;
- relabelled cells;
- zero cells;
- scenario improvement;
- population-weighted results.

## 7.3. Normalization sensitivity

Giữ/regenerate:

- min–max primary;
- log;
- percentile/winsor capped.

Anchor-based normalization:

- chỉ chạy nếu có defensible fixed anchors;
- nếu chưa có anchors, tạo schema và protocol;
- trạng thái `NOT_RUN_DATA_REQUIRED`;
- không tự chọn anchor chỉ để hoàn thành bảng.

## 7.4. Aggregation sensitivity

Canonical comparison:

- geometric mean primary;
- additive sensitivity;
- minimum-component diagnostic.

Product được báo cáo là legacy scale, không phải robustness.

Bảng phải giải thích:

- zero preservation;
- compensability;
- ranking behavior;
- typology impact;
- boundary impact;
- distribution impact.

## 7.5. Typology sensitivity

Regenerate:

- primary rank median;
- quantile 0.40;
- quantile 0.45;
- quantile 0.55;
- quantile 0.60;
- defensible absolute thresholds.

Không mô tả bốn typology là natural clusters.

Thêm table chuyển nhóm và map các cell không ổn định.

## 7.6. Sửa stale sensitivity artifacts

Kiểm tra và regenerate hoặc archive:

`outputs/validation/sensitivity_analysis_report.md`

Mọi sensitivity script phải dùng canonical defaults:

- `merged_pois_observed.gpkg`;
- `observed_strict`;
- 800 m NAI;
- RAC_time primary;
- current population weighting;
- current shared normalization;
- geometric SMCI primary.

Không để một script chạy “default” nhưng tái tạo specification cũ.

Tốt nhất mọi script đọc từ `config/pipeline.json` hoặc site config chung thay vì hard-code lại.

---

# 8. PHASE 5 — DATA QUALITY VÀ UNCERTAINTY

## 8.1. Data-quality grade

Tạo grade theo component và cell từ provenance hiện có:

- POI;
- GTFS;
- VinBus pseudo-GTFS;
- motorcycle calibration;
- WorldPop;
- building footprint;
- observed magnitude tiers.

Grade phải có rule rõ ràng, ví dụ:

- A/high;
- B/medium;
- C/low;
- D/missing or model-only.

Không biến grade thành một component SMCI mới.

Xuất:

- per-record provenance;
- per-cell grade;
- component grade;
- combined audit grade;
- map;
- population exposure theo grade.

## 8.2. Scenario envelope

Tổng hợp các scenario hợp lệ:

- motorcycle speed;
- transit impedance;
- MAI weights;
- time decay;
- normalization;
- observed/proxy specification;
- NAI threshold;
- NAI operationalization;
- geometric/additive/min aggregation.

Tạo per-cell envelope:

- p05;
- p25;
- median;
- p75;
- p95;
- min;
- max;
- typology stability;
- improvement probability.

Phân biệt rõ:

- empirical uncertainty;
- model scenario uncertainty;
- methodological sensitivity.

Không gọi scenario envelope là confidence interval nếu không có sampling model phù hợp.

---

# 9. PHASE 6 — RAC, RELIABILITY VÀ MIXED TRAFFIC

## 9.1. RAC_time tiếp tục là primary

Không thay RAC_time primary nếu chưa có evidence mạnh hơn.

Giữ:

- full RAC legacy robustness;
- transit impedance sensitivity;
- motorcycle speed sensitivity;
- headway sensitivity.

## 9.2. Reliability module

Tạo input schema và module cho:

- departure time;
- median travel time;
- p95 travel time;
- buffer time;
- headway variability;
- missed-transfer penalty.

Nếu không có observed or simulated multi-departure data:

- module phải refuse production run;
- output status `NOT_RUN_DATA_REQUIRED`;
- tạo data collection protocol;
- không sinh T95/T50 giả.

## 9.3. Generalized-cost RAC

Tạo code contract cho:

- walking time;
- waiting time;
- in-vehicle time;
- transfer time;
- fare;
- motorcycle operating cost;
- parking;
- value of time;
- discomfort/safety penalty.

Chỉ chạy khi coefficients có provenance hoặc scenario ranges được phê duyệt.

Nếu chưa có local value-of-time và penalties:

- tạo template;
- tạo validation rules;
- không promote vào paper primary;
- ghi là future extension.

## 9.4. Mixed-traffic friction

Thiết kế optional edge-impedance layer cho:

- road class;
- time of day;
- intersection;
- roadside activity;
- market/school influence;
- bus/truck presence;
- obstruction.

Không tạo friction factors giả.

Nếu chỉ có global motorcycle-speed sensitivity, giữ nó là current robustness và tạo protocol thu thập data cho edge-level model.

---

# 10. PHASE 7 — EXTERNAL VALIDATION

Tạo folder hoặc module rõ ràng cho external validation.

Input schemas tối thiểu:

- ridership;
- mode share;
- travel diary;
- perceived accessibility;
- observed OD travel times.

Tạo script:

`scripts/external_validation.py`

Script phải:

- validate schema;
- join observations với cells;
- calculate predefined metrics;
- refuse to run khi thiếu required fields;
- không dùng simulated values thay observed outcome.

Tạo:

- `docs/external_validation_protocol.md`
- `data/raw/external_validation_template.csv`
- `outputs/validation/external_validation_status.md`

Nếu chưa có dữ liệu, trạng thái chính xác phải là:

`NOT_RUN_DATA_REQUIRED`

Không được viết “externally validated”.

---

# 11. PHASE 8 — COMPARISON SITE WEST TAY MO

Đọc:

- `docs/comparison_site_protocol.md`
- `docs/western_extension_protocol.md`
- `config/sites/west_taymo.yml`
- toàn bộ `outputs/west_taymo/`

Kiểm tra có xung đột về site selection hoặc matching protocol hay không. Ghi decision record nếu cần.

Hoàn thiện tối đa có thể:

1. boundary provenance;
2. area and population seed conflicts;
3. planned/unplanned labels;
4. merged observed POI audit;
5. strict opportunity coverage;
6. WorldPop integration;
7. accessibility inputs;
8. metrics;
9. comparison tables;
10. shared-scale normalization;
11. scenario-matched comparison;
12. limitations.

Không promote `observed_strict` nếu `needs_source > 0`.

Nếu thiếu official magnitude data:

- giữ proxy run;
- tạo source acquisition checklist;
- ghi rõ data blockers;
- không gán magnitude giả.

Cross-site comparison phải:

- dùng common metric definition;
- dùng common normalization hoặc defensible fixed scale;
- không so sánh within-site rank-relative values như absolute cross-site difference;
- không đưa causal claim từ n=2 observational design.

---

# 12. PHASE 9 — PUBLICATION VÀ DOCUMENTATION

## 12.1. Paper và proposal

Cập nhật:

- `paper/paper_draft.md`
- `proposal/proposal_v7.md`
- `docs/Research_Proposal_SMCI_v2.md`
- `docs/metrics_reference.md`
- `docs/decisions.md`
- `CLAUDE.md`
- `README.md`

Paper phải giải thích:

- geometric mean primary;
- product legacy;
- additive sensitivity;
- minimum diagnostic;
- CCS/NPT role;
- population coverage;
- inequality;
- model sensitivity;
- data quality;
- external-validation limitation;
- comparison-site status.

Không tuyên bố:

- product versus GM proves robustness;
- spatial hotspot không đổi mà không chạy lại;
- individual capability được đo trực tiếp;
- zero-access đồng nghĩa cư dân không có bất kỳ cơ hội thực tế nào;
- residents sẽ đi bộ vì POI nằm trong threshold;
- boundary difference là causal effect;
- heuristic intervention là global optimum.

## 12.2. Abstract, results và conclusion

Tính lại mọi số SMCI.

Không copy product-based headline numbers sang geometric-mean manuscript.

Kiểm tra tất cả:

- means;
- medians;
- weighted means;
- ratios;
- percentages;
- boundary differences;
- scenario effects;
- map legends;
- captions.

Các cell count bất biến do monotonic transformation vẫn phải được xác nhận bằng test, không ghi theo giả định.

## 12.3. Supervisor memo và self-audit

Sửa `scripts/make_supervisor_memo.py` để không tái sinh caveat lỗi thời.

Không hard-code trạng thái như:

- WorldPop chưa tích hợp;
- Overture chưa được promote;
- POI gate còn chờ;
- RAC_time chưa primary.

Sửa `scripts/project_self_audit.py` để:

- thực sự chạy document consistency;
- kiểm tra output freshness;
- kiểm tra formula mode;
- kiểm tra schema version;
- kiểm tra generated artifact status;
- kiểm tra data-dependent blockers;
- phân biệt blocker và future extension.

## 12.4. Semantic consistency checks

Mở rộng `scripts/check_document_consistency.py`.

Ngoài numeric markers, phải kiểm tra các semantic assertions:

- primary SMCI operator;
- primary RAC operator;
- NAI primary threshold;
- opportunity basis;
- Overture status;
- WorldPop integration;
- GTFS vintage status;
- comparison-site status;
- external-validation status.

Fail nếu manuscript nói khác canonical config hoặc decision log.

---

# 13. PHASE 10 — TESTS VÀ QUALITY GATES

## 13.1. Unit tests mới

Thêm tests cho:

- geometric SMCI;
- product legacy;
- additive;
- minimum;
- zero preservation;
- monotonic relationship;
- scenario-delta sign;
- typology invariance;
- CCS;
- NPT K=1/3/5;
- missing-category cutoff;
- population coverage;
- weighted Gini;
- local-access classification;
- NPT-benefit normalization;
- SMCI_NPT;
- deterministic Monte Carlo;
- scenario envelope;
- provenance grading;
- external-validation schema refusal;
- West Tay Mo strict gate.

## 13.2. Integration tests

Kiểm tra:

- canonical pipeline chạy từ config;
- all outputs generated;
- headline snapshot matches processed cells;
- document markers match snapshot;
- all source files exist;
- no stale generated outputs;
- maps/tables scripts accept new columns;
- old product fields remain available;
- schema migrations are explicit.

## 13.3. Final gates

Chạy:

```bash
python -m pytest tests/ -q
python scripts/agent_gate.py
python scripts/check_document_consistency.py
python scripts/project_self_audit.py
python scripts/graph_health.py
```

Chạy research pipeline theo canonical config.

Không báo hoàn thành nếu:

- tests fail;
- document consistency fail;
- generated outputs stale;
- headline snapshot không khớp processed cells;
- semantic status mâu thuẫn;
- source file thiếu mà output vẫn tuyên bố hoàn thành.

---

# 14. OUTPUTS BẮT BUỘC CUỐI CÙNG

Tạo master completion report:

- `outputs/upgrade/upgrade_completion_report.md`
- `outputs/upgrade/upgrade_completion_report.json`
- `outputs/upgrade/upgrade_status_matrix.csv`

Status matrix phải có từng đề xuất trong ba tài liệu, với các cột:

- source document;
- recommendation;
- priority;
- implementation status;
- files changed;
- tests;
- output artifact;
- evidence;
- remaining blocker;
- paper location;
- final decision.

Trạng thái chỉ được dùng:

- `COMPLETED`
- `COMPLETED_WITH_LIMITATION`
- `CODE_COMPLETE_DATA_REQUIRED`
- `NOT_IMPLEMENTED_WITH_REASON`
- `REJECTED_BY_METHOD_DECISION`

Không dùng trạng thái mơ hồ như “mostly done”.

Completion report phải có:

1. Executive summary.
2. Baseline snapshot.
3. Final methodological decisions.
4. File-by-file implementation summary.
5. Old/new SMCI table.
6. NAI–Bruno results.
7. Sensitivity results.
8. Uncertainty/data-quality results.
9. External-validation status.
10. West Tay Mo status.
11. Tests and gates.
12. Unresolved data blockers.
13. Claims that were weakened or removed.
14. Exact commands to reproduce all outputs.
15. Final list of changed files.
16. Final commit SHAs.

---

# 15. COMMIT STRATEGY

Không tạo một mega-commit duy nhất.

Dùng commit sequence rõ ràng, ví dụ:

1. `chore: lock pre-upgrade baseline`
2. `docs: record geometric SMCI primary decision`
3. `feat: add geometric product additive and minimum SMCI operators`
4. `refactor: migrate canonical pilot metrics to geometric SMCI`
5. `test: add SMCI scale and typology invariants`
6. `feat: add CCS and NPT neighborhood robustness`
7. `feat: add population coverage and weighted NPT inequality`
8. `feat: add SMCI NPT supplementary specification`
9. `refactor: canonicalize MAI and normalization sensitivities`
10. `feat: add scenario uncertainty envelope and data-quality grades`
11. `docs: add external validation and generalized-cost protocols`
12. `fix: regenerate canonical outputs and publication artifacts`
13. `chore: strengthen semantic consistency and final gates`

Mỗi commit phải:

- có scope rõ;
- không trộn raw data;
- không chứa unrelated formatting churn;
- ghi tests đã chạy.

---

# 16. DEFINITION OF DONE

Chỉ coi công việc hoàn tất khi:

- geometric mean là canonical SMCI trong code và manuscript;
- product vẫn tồn tại dưới tên legacy rõ ràng;
- additive là robustness;
- minimum là diagnostic;
- toàn bộ SMCI được recalculated ở cấp cell;
- headline snapshot đã bump schema;
- spatial diagnostics được chạy lại;
- CCS đã triển khai;
- NPT K=1/3/5 đã triển khai;
- population coverage đã triển khai;
- weighted Gini đã triển khai;
- SMCI_NPT đã triển khai;
- MAI weights/time decay/normalization sensitivities được canonicalize;
- stale sensitivity report được regenerate hoặc archive;
- uncertainty envelope và data-quality outputs tồn tại;
- external-validation pipeline không giả dữ liệu;
- West Tay Mo có trạng thái gate trung thực;
- supervisor memo và self-audit không còn caveat lỗi thời;
- semantic document checks hoạt động;
- tests và gates đều pass;
- completion report ánh xạ đầy đủ từng đề xuất trong ba tài liệu;
- không còn generated artifact stale;
- không còn manuscript number lấy từ product scale nhưng được gọi là geometric SMCI.

Không dừng để hỏi các lựa chọn nhỏ. Hãy dùng decision log, source documents và existing project conventions để đưa ra quyết định có thể tái lập.

Chỉ dừng ở hạng mục cần dữ liệu bên ngoài không tồn tại. Khi đó vẫn phải hoàn thành code contract, protocol, validation schema, blocker report và trạng thái `CODE_COMPLETE_DATA_REQUIRED`.

Cuối phiên làm việc, trả về:

- branch;
- commits;
- files changed;
- commands run;
- test results;
- headline old/new table;
- completed items;
- data-blocked items;
- exact reproduction command;
- PR-ready summary.