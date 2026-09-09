# Kiến trúc — bản đồ từ tài liệu sang code

## Bốn lớp

```
Lớp 1 — Người dùng     Claude Desktop (merchandiser) · Claude Code (IT) · n8n (theo lịch)
                            │
Lớp 2 — Cổng điều phối  src/lsth_mcp/server.py
                        xác thực · phân quyền · nhật ký · giới hạn tần suất
                            │
Lớp 3 — MCP server      src/lsth_mcp/servers/  (S1–S7, M1–M5)
                        mỗi server một miền dữ liệu
                            │
Lớp 4 — Nguồn dữ liệu   ERP · ổ chung · hộp thư · tech pack · cổng khách
                        chủ sở hữu dữ liệu hiện tại, không đổi
```

Tách bốn lớp để khi thay mô hình AI (lớp 1) hoặc đổi hệ thống ERP (lớp 4) thì chỉ
một lớp phải sửa.

## Mười bảy thành phần ↔ tệp trong repo

### Nhóm nền (F1–F5) — không có nhóm này thì bảy server không nối được với nhau

| Mã | Thành phần | Ở đâu |
|---|---|---|
| F1 | Cổng điều phối | `server.py` + `core/permissions.py` + `core/audit.py` |
| F2 | Mô hình dữ liệu chuẩn | `core/models.py` |
| F3 | Bảng ánh xạ định danh | `domain/identity.py` + `data/identity/` |
| F4 | Kho template & quy ước tên | `domain/templates.py` + `data/templates/` + `config/naming.yaml` |
| F5 | Bộ đánh giá chất lượng | `domain/evalset.py` + `data/eval/` |

### Bảy server v1.0 và năm thành phần mới

| Mã | Server | Gói | Vòng |
|---|---|---|---|
| S1 | lsth-techpack | `servers/s1_techpack/` | 1 |
| S2 | lsth-erp | `servers/s2_erp/` | 2 |
| S3 | lsth-drive | `servers/s3_drive/` | 2 |
| S4 | lsth-mail | `servers/s4_mail/` | 3 |
| S5 | lsth-status | `servers/s5_status/` | 3 |
| S6 | lsth-packing | `servers/s6_packing/` | 4 |
| S7 | lsth-portal | `servers/s7_portal/` | 5 — đã gộp vào M5 |
| M1 | lsth-sample | `servers/m1_sample/` | 4 |
| M2 | lsth-translate | `servers/m2_translate/` | 1 |
| M3 | lsth-compliance | `servers/m3_compliance/` | 3 |
| M4 | lsth-archive | `servers/m4_archive/` | 3 |
| M5 | portal đa cổng | `servers/m5_portal/` | 5 |

## Hợp đồng dữ liệu (F2)

Năm thực thể là ngôn ngữ chung. Tên trường lấy đúng theo tên cột trong file BOM
thật để không phải dịch qua lại.

`Style` · `BomLine` · `PurchaseOrder` · `NplItem` · `PackingSpec`

BOM của Garan và Haddad đã dùng chung đúng bộ cột — nên một bộ alias
(`models.BOM_ALIASES`) đủ cho cả hai. Khách mới thì **thêm alias, không sửa model**.

Quy tắc bắt buộc: mỗi giá trị đi kèm nguồn (file, sheet hoặc số trang). Không có
nguồn thì để trống và đánh dấu `needs_human`. Trường thiếu nguồn là **tín hiệu
tốt, không phải lỗi** — nó chỉ đúng chỗ quy trình hiện tại đang dựa vào trí nhớ
của một người.

## Ranh giới MCP và n8n

| | MCP server | n8n |
|---|---|---|
| Ai khởi động | Người hỏi thì máy làm | Đồng hồ hoặc sự kiện |
| Tính chất | Phát sinh, mỗi lần một khác | Lặp lại y hệt, lịch cố định |
| Chứa cái gì | **Năng lực**: đọc dữ liệu, dựng file, tra cứu | **Trình tự**: gọi năng lực nào trước |
| Ví dụ | "Tra giúp mã móc cho style này thị trường Canada" | "6h30 sáng quét mail, so ETD, cảnh báo nếu trễ" |

Quy tắc vàng: **mọi logic nghiệp vụ nằm ở MCP**. n8n chỉ điều phối — để đổi công
cụ điều phối không phải viết lại.

## Ba luồng nghiệp vụ

**Luồng A — đơn hàng mới thành BOM nháp.** Thay chuỗi thao tác đang tốn 60–90
phút mỗi đơn để bóc PDF, cộng thời gian nhân tay 202–374 dòng BOM. Bước 8 là chốt
chặn con người: không có nhánh nào đi vòng qua nó.

**Luồng B — radar ETD hằng ngày.** Cắt trọn 90 phút dò mail mỗi ngày, không đòi
quyền ghi vào bất kỳ hệ thống nào. Nhánh "không có bất thường" quan trọng ngang
nhánh cảnh báo: hệ thống không được làm phiền khi không có gì để báo.

**Luồng C — xưởng tài liệu đóng gói.** Đổi bản chất công việc từ "soạn từ đầu"
thành "soát và sửa" — nguồn tiết kiệm lớn nhất toàn chương trình. Cũng là luồng
rủi ro cao nhất nếu làm ẩu: TLĐG sai dẫn tới đóng gói sai, hàng bị khách trả.
Phải chạy song song ít nhất 5 mã hàng và có người soát 100% trước khi tin.
