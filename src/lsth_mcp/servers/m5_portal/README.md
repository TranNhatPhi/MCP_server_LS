# M5 · lsth-portal-multi

Cổng khách đa hệ thống — 9 cổng

| | |
|---|---|
| Vòng | 5 |
| Nhóm | MỚI |
| Ưu tiên | Thấp |
| Độ khó | Rất cao |
| Phụ thuộc | G2, thoả thuận khách |
| Chặn bởi | G2 |
| Nghiệm thu | Chị Hạnh, Chị Phúc |
| Miền quyền | `portal` |

## Ghi chú thiết kế

Thành phần tốn công nhất và dễ hỏng nhất toàn danh mục. Chín cổng, phần lớn không có API, mỗi cổng một cách đăng nhập. BẮT BUỘC: xin phép khách trước, dùng tài khoản riêng cho tự động hoá, và server phải TỰ DỪNG BÁO NGƯỜI khi giao diện đổi thay vì đoán bừa. Tự động hoá không làm cổng khách nhanh lên — nó chỉ giúp người không phải ngồi chờ.

## Hợp đồng tool

| Tool | Vào | Ra |
|---|---|---|
| `portal_list()` | — | 9 cổng và trạng thái tài khoản từng cổng |
| `portal_download(portal: str, ref: str)` | portal: str, ref: str | Tải tài liệu từ một cổng |
| `portal_submit(portal: str, payload: dict)` | portal: str, payload: dict | Nộp lên cổng — cần người bấm nút |
| `portal_health(portal: str = '')` | portal: str = '' | Kiểm cổng còn đúng giao diện đã biết không |

## Trước khi viết dòng code đầu tiên

Theo quy trình dựng sáu bước (chương 12 kiến trúc v1.0), bước 2 — **ngồi cạnh
người làm, ghi lại 20 thao tác thật** — là bước không được rút gọn. JD và khảo sát
không ghi thứ tự ưu tiên khi hai nguồn mâu thuẫn, cũng không ghi trường hợp ngoại
lệ nào phải hỏi khách. Những quy tắc ngầm đó chỉ hiện ra khi ngồi xem người ta làm.

Người ngồi cùng: Chị Hạnh, Chị Phúc.

## Chín cổng khách hàng

| Hệ thống | Của khách | Dùng để làm gì |
|---|---|---|
| Symparel | Garan | Tải PO draft/final, submit layout, book xuất |
| Quonda | Haddad | Book kiểm hàng cuối (FI) |
| VSN | Haddad | Submit mẫu, cập nhật thông tin |
| Hệ thống Haddad (DC) | Haddad | Tải DC Production và comment |
| GACC | Hải quan Trung Quốc | Upload hồ sơ e-filing |
| Checkpoint VN | JAKO, Osaka | Đặt tem RFID |
| Trimco VN / HK | JAKO | Đặt nhãn |
| PLM | H&M | Tải tài liệu mẫu |
| OFU + CP | H&M | Tải OD, tách cảng, forecast |
| SCOOP | H&M | Theo dõi vải |
