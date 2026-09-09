# M4 · lsth-archive

Kho lịch sử mùa: giá NPL, báo cáo test, layout, định mức

| | |
|---|---|
| Vòng | 3 |
| Nhóm | MỚI |
| Ưu tiên | Trung bình |
| Độ khó | Thấp |
| Phụ thuộc | F3, F4 |
| Chặn bởi | không |
| Nghiệm thu | Chị Phạm Hương Vân |
| Miền quyền | `archive` |

## Ghi chú thiết kế

Thành phần rẻ nhất nhóm mới — chủ yếu gom file và đánh chỉ mục. Nhưng mỗi mùa trôi qua là mất thêm một lớp dữ liệu, nên đáng làm sớm.

## Hợp đồng tool

| Tool | Vào | Ra |
|---|---|---|
| `price_history(item: str, season: str = '')` | item: str, season: str = '' | Giá NPL các mùa trước |
| `report_history(style: str)` | style: str | Số báo cáo test và ngày ra báo cáo |
| `layout_history(style: str, market: str)` | style: str, market: str | Layout đã duyệt |
| `consumption_history(style: str)` | style: str | Định mức đã dùng |

## Trước khi viết dòng code đầu tiên

Theo quy trình dựng sáu bước (chương 12 kiến trúc v1.0), bước 2 — **ngồi cạnh
người làm, ghi lại 20 thao tác thật** — là bước không được rút gọn. JD và khảo sát
không ghi thứ tự ưu tiên khi hai nguồn mâu thuẫn, cũng không ghi trường hợp ngoại
lệ nào phải hỏi khách. Những quy tắc ngầm đó chỉ hiện ra khi ngồi xem người ta làm.

Người ngồi cùng: Chị Phạm Hương Vân.
