# S3 · lsth-drive

Tra SOF, DC, UPC theo style và thị trường

| | |
|---|---|
| Vòng | 2 |
| Nhóm | Server v1.0 |
| Ưu tiên | Cao |
| Độ khó | Thấp |
| Phụ thuộc | F3, F4, G5 |
| Chặn bởi | G5 |
| Nghiệm thu | Chị Thúy, Chị Ly |
| Miền quyền | `drive` |

## Ghi chú thiết kế

Đòi hỏi chuẩn hoá quy ước đặt tên file trước — đó chính là G5.

## Hợp đồng tool

| Tool | Vào | Ra |
|---|---|---|
| `sof_lookup(style: str, market: str)` | style: str, market: str | PackingSpec tra từ SOF |
| `dc_get(style: str)` | style: str | Tài liệu DC Production kèm bản dịch |
| `upc_find(style: str, color: str, size: str)` | style: str, color: str, size: str | Mã UPC |
| `layout_publish(file: str, style: str)` | file: str, style: str | Đăng layout đã duyệt lên ổ chung |

## Trước khi viết dòng code đầu tiên

Theo quy trình dựng sáu bước (chương 12 kiến trúc v1.0), bước 2 — **ngồi cạnh
người làm, ghi lại 20 thao tác thật** — là bước không được rút gọn. JD và khảo sát
không ghi thứ tự ưu tiên khi hai nguồn mâu thuẫn, cũng không ghi trường hợp ngoại
lệ nào phải hỏi khách. Những quy tắc ngầm đó chỉ hiện ra khi ngồi xem người ta làm.

Người ngồi cùng: Chị Thúy, Chị Ly.
