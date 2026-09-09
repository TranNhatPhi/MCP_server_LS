# S2 · lsth-erp

Sinh BOM, dựng PO nháp, kéo việc cần duyệt

| | |
|---|---|
| Vòng | 2 |
| Nhóm | Server v1.0 |
| Ưu tiên | Rất cao |
| Độ khó | Trung bình |
| Phụ thuộc | F2, F3, G1 |
| Chặn bởi | G1 |
| Nghiệm thu | Chị Hằng, Chị Phúc |
| Miền quyền | `erp` |

## Ghi chú thiết kế

Nhóm việc chiếm 30,2% quỹ thời gian toàn khối — nặng nhất. Ra mắt chỉ đọc; quyền ghi mở sau 5 mã hàng đúng.

## Hợp đồng tool

| Tool | Vào | Ra |
|---|---|---|
| `bom_get(style: str)` | style: str | BomLine[] của một mã hàng lấy từ ERP |
| `bom_generate(master: str, colors: list, sizes: list)` | master: str, colors: list, sizes: list | Sinh BOM 202–374 dòng từ 7–22 mã vật tư gốc bằng phép nhân |
| `po_draft(bom_id: str, vendor: str)` | bom_id: str, vendor: str | PO nháp — máy soạn, người bấm nút |
| `fabric_claim_list()` | — | Phiếu bù vải chờ duyệt |
| `balance_check(style: str)` | style: str | Cân đối định mức đã đặt với định mức cần |

## Trước khi viết dòng code đầu tiên

Theo quy trình dựng sáu bước (chương 12 kiến trúc v1.0), bước 2 — **ngồi cạnh
người làm, ghi lại 20 thao tác thật** — là bước không được rút gọn. JD và khảo sát
không ghi thứ tự ưu tiên khi hai nguồn mâu thuẫn, cũng không ghi trường hợp ngoại
lệ nào phải hỏi khách. Những quy tắc ngầm đó chỉ hiện ra khi ngồi xem người ta làm.

Người ngồi cùng: Chị Hằng, Chị Phúc.

## Bản đồ ERP đã có — đọc trước khi viết code

Xem [`docs/ERP_MAP.md`](../../../../docs/ERP_MAP.md) và [`core/erp.py`](../../core/erp.py).
Cẩm nang nội bộ đã cho biết mười module mà server này phải chạm tới, và các ràng
buộc sau **phải nằm trong hợp đồng tool**, nếu không máy sẽ soạn ra thao tác mà
ERP từ chối:

- Luồng BOM có bốn trạng thái: `Import → Save → Submit (chọn người duyệt theo
  MSNV) → Approve/Reject`, rồi mới `Pull BOM type → Pull BOM → Purchase Order`.
- **Chỉ sửa item khi chưa submit hoặc đã bị reject.**
- **Item đã mua thì không xoá khỏi BOM được.**
- Style number khi import BOM khác nhau theo nhãn — dùng
  `domain.identity.erp_style_number()`, đừng viết lại quy tắc.
- Chuỗi duyệt PO là cấu hình theo nhà máy và có tên người cụ thể; phải biết chuỗi
  này mới soạn được PO nháp gửi đúng người.

Lỗi ERP mà người dùng đã nêu ba lần — *báo lỗi BOM lúc Save thay vì lúc Pull* —
nằm đúng ở bước `pull_bom`. Hỏi nhà cung cấp trong cùng cuộc gọi lấp G1.
