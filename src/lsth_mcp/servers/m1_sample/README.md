# M1 · lsth-sample

Vòng đời mẫu: FIT, PP, TOP, photoshoot

| | |
|---|---|
| Vòng | 4 |
| Nhóm | MỚI |
| Ưu tiên | Trung bình |
| Độ khó | Trung bình |
| Phụ thuộc | S1, M2 |
| Chặn bởi | G6 |
| Nghiệm thu | Chị Huỳnh Thị Thúy, Chị Tuyết Như |
| Miền quyền | `sample` |

## Ghi chú thiết kế

Mảng trắng lớn nhất của v1.0. Chị Huỳnh Thị Thúy dành 100% quỹ thời gian ở đây. Con số 4,0% là thấp giả tạo vì file Lucy team không có cột %.

## Hợp đồng tool

| Tool | Vào | Ra |
|---|---|---|
| `sample_request(style: str, kind: str)` | style: str, kind: str | Tạo yêu cầu mẫu |
| `sample_status(style: str)` | style: str | Tiến độ mẫu |
| `hangtag_make(sample: dict)` | sample: dict | Dựng hangtag |
| `sending_list(bill: str, destination: str)` | bill: str, destination: str | Danh sách gửi hàng |
| `comment_sync(customer_system: str)` | customer_system: str | Đồng bộ comment từ hệ thống khách |

## Trước khi viết dòng code đầu tiên

Theo quy trình dựng sáu bước (chương 12 kiến trúc v1.0), bước 2 — **ngồi cạnh
người làm, ghi lại 20 thao tác thật** — là bước không được rút gọn. JD và khảo sát
không ghi thứ tự ưu tiên khi hai nguồn mâu thuẫn, cũng không ghi trường hợp ngoại
lệ nào phải hỏi khách. Những quy tắc ngầm đó chỉ hiện ra khi ngồi xem người ta làm.

Người ngồi cùng: Chị Huỳnh Thị Thúy, Chị Tuyết Như.
