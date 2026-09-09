# S4 · lsth-mail

Trích ETD, tìm luồng thư, soạn nháp

| | |
|---|---|
| Vòng | 3 |
| Nhóm | Server v1.0 |
| Ưu tiên | Cao |
| Độ khó | Trung bình |
| Phụ thuộc | F1, F3 |
| Chặn bởi | không |
| Nghiệm thu | Chị Quỳnh, Chị Thương |
| Miền quyền | `mail` |

## Ghi chú thiết kế

Email chiếm 14,8% quỹ thời gian. Chỉ đọc và soạn nháp — KHÔNG có quyền gửi (nguyên tắc 1). Nuôi n8n WF-1.

## Hợp đồng tool

| Tool | Vào | Ra |
|---|---|---|
| `thread_search(style: str = '', po: str = '')` | style: str = '', po: str = '' | Luồng thư liên quan |
| `etd_extract(since: str, until: str)` | since: str, until: str | NplItem[] với ETD trích từ thư |
| `draft_reply(thread_id: str, points: list)` | thread_id: str, points: list | Thư nháp |
| `claim_draft(issue: str)` | issue: str | Thư khiếu nại nháp |

## Trước khi viết dòng code đầu tiên

Theo quy trình dựng sáu bước (chương 12 kiến trúc v1.0), bước 2 — **ngồi cạnh
người làm, ghi lại 20 thao tác thật** — là bước không được rút gọn. JD và khảo sát
không ghi thứ tự ưu tiên khi hai nguồn mâu thuẫn, cũng không ghi trường hợp ngoại
lệ nào phải hỏi khách. Những quy tắc ngầm đó chỉ hiện ra khi ngồi xem người ta làm.

Người ngồi cùng: Chị Quỳnh, Chị Thương.
