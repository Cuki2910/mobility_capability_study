# Roadmap nghiên cứu

Các mục dưới đây là ý tưởng hoặc việc còn thiếu, **chưa được áp dụng**. Roadmap
không khóa phương pháp, phạm vi, ngưỡng hay công thức; hướng mới của người dùng
được ưu tiên. Triển khai từng thay đổi thành bản nháp, kiểm tra và báo cáo theo
`docs/agent_workflow.md` trước khi xác nhận áp dụng.

## Việc cần xử lý trước khi dùng dữ liệu tải lại

- Review POI OSM/Overture mới, đặc biệt các điểm Overture-only chưa kiểm tra.
  Kết quả kiểm tra lịch sử không chứng nhận dữ liệu tải lại.
- Hoàn thiện nguồn cho jobs, beds, enrollment và commercial floor area;
  phân biệt quan sát tại cơ sở với ước lượng theo chuẩn hoặc diện tích.
- Khi được yêu cầu chạy lại, tính từ mạng và POI mới; phân biệt kết quả mới
  với bảng accessibility khôi phục từ bản đồ đã công bố.
- Đồng bộ tài liệu giải thích metrics với code/config hiện hành, sửa công thức
  SMCI và số liệu lịch sử đang được trình bày như kết quả hiện tại.

Trạng thái dữ liệu: `docs/data_sources.md`, `docs/data_recovery.md`.

## Evidence audit và đóng góp của SMCI

- So sánh SUTI, SUMI, SUMP, SMRI, SDG 11.2, Urban Mobility Readiness Index,
  Sustainable Cities Mobility Index và các chỉ số accessibility liên quan.
- Lập evidence matrix: nguồn/năm, mục đích, đơn vị phân tích, cách chọn chỉ báo,
  trọng số, tổng hợp, chuẩn hóa, dữ liệu/mẫu, validation, sensitivity,
  uncertainty, khả năng chuyển sang Việt Nam, điểm mạnh và hạn chế.
- Đánh giá riêng bằng chứng cho lựa chọn chỉ báo, trọng số và phép tổng hợp;
  phân biệt dashboard, readiness, capability và hành vi di chuyển thực tế.
- Kiểm tra double counting, city-size/income bias, compensation, đóng góp
  dual-scale/mode-competitive và độ ổn định giữa các nhóm dân cư.
  Kết luận theo bằng chứng, không đặt sẵn kết quả review.

## Các phương án SMCI-VN cần nghiên cứu

- **M0:** baseline đọc từ `config/pipeline.json` và code hiện hành; không sao
  chép công thức product cũ làm mặc định mới.
- **M1:** generalized competitiveness, gồm thời gian door-to-door, reliability,
  chi phí, transfer, access/egress và parking; cần dữ liệu và hệ số có nguồn.
- **M2:** mixed-traffic feasibility, gồm safety/conflict, pedestrian continuity,
  climate/shade, universal access và intermodal/ride-hailing integration.
  Đánh giá vai trò modifier, diagnostic hay thành phần; kiểm tra trùng lặp,
  validity và sensitivity trước khi đề xuất đưa vào SMCI.
- **M3:** capability theo nhóm thu nhập thấp, phụ nữ, người cao tuổi, người
  khuyết tật, hộ không có xe máy, lao động ca, sinh viên và người chăm sóc;
  cần survey hoặc tham số theo nhóm, báo cáo equity gaps.
- So sánh normative, equal, trip-purpose-derived, expert/stakeholder và hybrid
  weights. Tách social value, revealed demand và behavioral coefficients;
  thống kê PCA/entropy/CRITIC không tự chứng minh mức quan trọng xã hội.
- Nếu có dữ liệu choice survey, ước lượng time/cost/reliability/transfer/walking
  penalties và heterogeneity; kiểm tra ngoài mẫu. So sánh compensation của
  additive/minimum/CES nếu phù hợp; product và geometric mean cùng số mũ
  là scale audit, không phải hai kiểm định thứ hạng độc lập.

## Dữ liệu thực địa, validation và policy

- Thu thập OD lặp lại theo giờ, fare/operating cost/parking/value of time,
  sidewalk/crossing/friction, safety, heat và shade. Protocol hiện có:
  `docs/extended_rac_data_protocol.md`, `docs/external_validation_protocol.md`.
- Kiểm tra thực địa các crossing/gate quan trọng quanh ranh giới Ocean Park;
  OSM topology và thiếu barrier tags không chứng minh đi lại tự do thực tế.
- Bổ sung outcome độc lập và content/construct/criterion/predictive/policy
  validation. Kiểm tra 10 OD xe máy lịch sử chỉ hỗ trợ plausibility Network D,
  không chứng nhận toàn bộ SMCI, typology hoặc tác động nhân quả.
- Xem xét policy scenarios: frequency, sidewalk/crossing, transfer/shade/station
  access, can thiệp tích hợp, parking/cost và ride-hailing feeder. Báo cáo Delta,
  dân số/nhóm hưởng lợi, lock-in còn lại, chi phí nếu có và uncertainty;
  chính sách giảm lợi thế xe máy cần đánh giá equity.
- Site comparison là hướng mở rộng. Đo matching, boundary/spillover, data parity
  và dùng shared-scale normalization. Tây Mỗ hiện có báo cáo
  `outputs/west_taymo/readiness_status.md` ghi `MATCHING_GATE_FAILED`;
  chọn lại control hoặc đề xuất sửa thiết kế với lý do, không tự áp dụng.
  Xem hai protocol comparison-site và western-extension hiện có.

## Lịch sử và bàn giao

Geometric SMCI, Bruno CCS/NPT, map, grid robustness và uncertainty đã có code
và artifact lịch sử trong `outputs/upgrade/upgrade_status_matrix.csv`.
Các artifact đó không chứng nhận dữ liệu mới hay mặc nhiên hoàn thành mọi ý
tưởng SMCI-VN. Kiểm tra evidence thực tế khi tiếp tục công việc.

Prompt, proposal phụ và kế hoạch cũ được bỏ khỏi workspace; bản gốc còn trong
Git tại `d0e8ab14f3834e9b151434d1140b891b17e29508` (các tài liệu trước đây ở
`docs/upgrade_cmt/`, prompt SMCI-VN, phản hồi giảng viên, proposal v2 và hai file
gốc `plan.md`, `walkthrough.md`). Chỉ giữ proposal `proposal/proposal_v7.md`;
nâng cấp proposal hiện hành khi được yêu cầu, không tạo thêm bản cạnh tranh.
