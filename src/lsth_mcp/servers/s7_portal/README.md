# S7 · lsth-portal

Cổng khách hàng — bản v1.0, nay gộp vào M5

| | |
|---|---|
| Vòng | 5 |
| Nhóm | Server v1.0 |
| Ưu tiên | Thấp |
| Độ khó | Cao |
| Phụ thuộc | G2 |
| Chặn bởi | G2 |
| Nghiệm thu | Chị Hạnh, Chị Phúc |
| Miền quyền | `portal` |

## Ghi chú thiết kế

ĐÃ GỘP VÀO M5. Gói này giữ lại để không gãy tham chiếu từ tài liệu v1.0; code mới viết ở servers/m5_portal.

## Hợp đồng tool

| Tool | Vào | Ra |
|---|---|---|
| `symparel_download(po: str)` | po: str | Tải PO từ Symparel |
| `quonda_book_fi(items: list)` | items: list | Book kiểm hàng cuối |
| `vsn_submit(sample: dict)` | sample: dict | Submit mẫu lên VSN |
| `gacc_upload(dossier: dict)` | dossier: dict | Upload hồ sơ e-filing GACC |

## Trước khi viết dòng code đầu tiên

Theo quy trình dựng sáu bước (chương 12 kiến trúc v1.0), bước 2 — **ngồi cạnh
người làm, ghi lại 20 thao tác thật** — là bước không được rút gọn. JD và khảo sát
không ghi thứ tự ưu tiên khi hai nguồn mâu thuẫn, cũng không ghi trường hợp ngoại
lệ nào phải hỏi khách. Những quy tắc ngầm đó chỉ hiện ra khi ngồi xem người ta làm.

Người ngồi cùng: Chị Hạnh, Chị Phúc.
