# S5 · lsth-status

Bảng trạng thái T&A, cảnh báo trễ

| | |
|---|---|
| Vòng | 3 |
| Nhóm | Server v1.0 |
| Ưu tiên | Cao |
| Độ khó | Trung bình |
| Phụ thuộc | S2, S4, G1 |
| Chặn bởi | G1 |
| Nghiệm thu | Toàn khối, Sản xuất |
| Miền quyền | `status` |

## Ghi chú thiết kế

Thay việc dò hộp thư 90 phút mỗi ngày. Nhánh 'không có bất thường' quan trọng ngang nhánh cảnh báo: không làm phiền khi không có gì để báo.

## Hợp đồng tool

| Tool | Vào | Ra |
|---|---|---|
| `order_status(po: str)` | po: str | Tiến độ một PO |
| `npl_eta(style: str)` | style: str | Tình trạng NPL của một mã hàng |
| `ta_alerts()` | — | Mã hàng trễ mốc T&A |
| `wip_report(week: str)` | week: str | Báo cáo WIP tuần |

## Trước khi viết dòng code đầu tiên

Theo quy trình dựng sáu bước (chương 12 kiến trúc v1.0), bước 2 — **ngồi cạnh
người làm, ghi lại 20 thao tác thật** — là bước không được rút gọn. JD và khảo sát
không ghi thứ tự ưu tiên khi hai nguồn mâu thuẫn, cũng không ghi trường hợp ngoại
lệ nào phải hỏi khách. Những quy tắc ngầm đó chỉ hiện ra khi ngồi xem người ta làm.

Người ngồi cùng: Toàn khối, Sản xuất.
