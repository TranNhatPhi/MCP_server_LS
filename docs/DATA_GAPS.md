# Chín khoảng trống dữ liệu

Xếp theo mức độ chặn: khoảng trống nào không lấp thì thành phần nào không dựng được.
Tám trên chín lấp được bằng cách hỏi đúng người, không cần dựng gì.

| # | Khoảng trống | Cần biết chính xác | Chặn | Mức | Cách lấp | Ai chủ trì | Thời gian |
|---|---|---|---|---|---|---|---|
| **G1** | ERP LSTH có API mở không | Có API đọc/ghi không? Module nào? Xuất file định dạng gì? Ai là đầu mối phía nhà cung cấp? | S2, S5, M4 | **Cứng** | Một cuộc gọi với nhà cung cấp ERP + xin tài liệu kỹ thuật | IT | 2–3 ngày |
| **G2** | Bản đồ hệ thống khách | 9 cổng: Symparel, Quonda, VSN, GACC, Checkpoint VN, Trimco, PLM, OFU/CP, SCOOP. Cổng nào cho export? Cổng nào có API? | M5, S7 | **Cứng** | Lập bảng 9 cổng: ai có tài khoản, đăng nhập thế nào, có nút export không | Kỹ thuật | 3 ngày |
| **G3** | Số đo thời gian thật | Bấm giờ 1 tuần trên 3–5 người. Số tự khai đang lệch: có người tổng 196%, có người 0% | Cam kết KPI | Mềm | Người tự ghi, không ai giám sát | Đầu mối nghiệp vụ | 1 tuần |
| **G4** | File mẫu đầu ra đã duyệt | Mỗi loại 1 file chuẩn: TLĐG, Worksheet, BOM, báo cáo TUV, FDW | S6, M1, M3 | **Cứng** | Xin chị Ly (TLĐG), chị Hạnh (FDW), chị Bích Thủy (TUV) | Kỹ thuật | 2 ngày |
| **G5** | Quy ước tên và cấu trúc ổ chung | Hiện mỗi người một kiểu | S3, F4 | **Cứng** | Chụp lại hiện trạng — dùng `scripts/scan_drive.py` | Kỹ thuật | 2 ngày |
| **G6** | Bản ghi thao tác chi tiết | Mới có 1/5 đầu việc nặng nhất. Còn thiếu: BOM vải, layout nhãn, TLĐG, mẫu | Mọi vòng | **Cứng** | Ngồi cạnh 4 người còn lại, mỗi người 2 buổi 45 phút | Kỹ thuật + BU trưởng | 2 tuần |
| **G7** | Khối lượng nghiệp vụ | Bao nhiêu style mỗi mùa? PO mỗi tháng? Mã mới mỗi tuần? | Bài toán đầu tư | Mềm | Xin file xuất từ PPC | Kỹ thuật | 2 ngày |
| **G8** | Điều khoản bảo mật của 5 khách | Tài liệu nào được đưa lên dịch vụ AI ngoài, tài liệu nào không | Việc dùng công cụ ngoài, M2 | **Cứng** | Rà hợp đồng gia công phần điều khoản bảo mật | BU trưởng | 1 tuần |
| **G9** | Danh sách nhân sự chuẩn | Xác minh trùng tên giữa hai đợt; ai phụ trách mảng nào ở khách nào | Quy mô, phân vai, F3 | Mềm | Xin bảng nhân sự khối BU theo mã nhân viên | Đầu mối | 1 ngày |

## Cập nhật 09/09/2026 — sau khi đọc `Use_guide/`

Chín tài liệu **USE GUIDE ERP VERSION WEB** trong `Use_guide/` là nguồn nội bộ,
đọc được ngay, không phải chờ ai. Chúng đã lấp được một phần bốn khoảng trống:

| Khoảng trống | Trước | Sau khi đọc cẩm nang |
|---|---|---|
| **G1** | Chưa biết ERP có API không | ERP là web app **và có app di động trên App Store + Google Play** → gần như chắc chắn có API HTTP. **19/25 module xuất được Excel** → đường dự phòng chắc chắn dùng được. Bản đồ module đã có ở `ERP_MAP.md` |
| **G9** | Chưa có danh sách nhân sự chuẩn | Mã số nhân viên chính là tên đăng nhập ERP, độ dài theo công ty (LS 5, LK 7, DA 6, TH 8) → xin bảng nhân sự từ ERP là ra |
| **F3** | Chưa biết quy tắc nối mã | **Quy tắc style number đã có văn bản**: Haddad/IFG/Jako/Osaka dùng Contract No, còn lại dùng customer style. Đã cài vào `domain.identity.erp_style_number()` |
| **G5** | Quy ước tên mỗi người một kiểu | ERP đã có sẵn quy ước cho vendor ID, sheet forecast `W{tuần}.{năm}`, số đầu thùng. Lấy làm chuẩn thay vì nghĩ ra cái mới |

**Ba việc mới lộ ra, nên làm trước khi dựng:**

1. **Xem tính năng `Sales Order → Read PDF` của ERP.** Nó đã bóc PDF cho H&M rồi.
   Dựng S1 mà không xem cái này thì dễ làm trùng và tạo hai nguồn sự thật.
2. **Kiểm tra `System → Group Mail`.** ERP đã tự gửi mail theo nhãn và loại đề
   xuất. Một phần của 14,8% quỹ thời gian cho email có thể cắt bằng **cấu hình**,
   không cần dựng gì.
3. **Sáu nhãn khách chưa ai khai workload** — Decathlon, IFG, JO, Goruck, Kmart,
   Puma. Khảo sát mới phủ 6/12 nhãn đang chạy trên ERP.

## Điểm quan trọng về thứ tự

Không nên dựng bất cứ thành phần nào trước khi lấp xong **G1, G4, G5 và ít nhất
một nửa G6**. Đây không phải sự thận trọng thừa: dựng trên dữ liệu chưa rõ nghĩa
thì phải làm lại từ đầu, và làm lại lần hai sẽ mất niềm tin của người dùng.

Ngược lại, ba việc ở **vòng 0** — sửa lỗi ERP, quy định trách nhiệm dữ liệu, chuẩn
hoá file khảo sát — làm được ngay song song với việc lấp khoảng trống, không phụ
thuộc gì cả.

## Khoảng trống nào ánh xạ vào code ở đâu

| Khoảng trống | Lấp xong thì mở được gì |
|---|---|
| G1 | `servers/s2_erp/server.py`, `s5_status` — thay `NotImplementedYetError` bằng lệnh gọi thật; điền `LSTH_ERP_*` trong `.env` |
| G2 | `servers/m5_portal/server.py` — bảng 9 cổng đã có trong README của gói đó |
| G4 | `data/templates/registry.yaml` — đang rỗng, đây là thứ chặn nhiều thành phần nhất |
| G5 | `config/naming.yaml` — chạy `scripts/scan_drive.py` để có số liệu hiện trạng trước |
| G6 | Bước 2 quy trình dựng cho từng server; ghi vào README của gói tương ứng |
| G8 | `config/data_zones.yaml` — bảng vùng hiện là bản dự kiến |
| G9 | `data/identity/identity_map.csv` — F3 |
