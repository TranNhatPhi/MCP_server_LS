# M2 · lsth-translate

Dịch tài liệu kỹ thuật có kiểm soát thuật ngữ

| | |
|---|---|
| Vòng | 1 |
| Nhóm | MỚI |
| Ưu tiên | Cao |
| Độ khó | Thấp |
| Phụ thuộc | F5, G8 |
| Chặn bởi | G8 |
| Nghiệm thu | Chị Bích Thủy, Chị Nhiên |
| Miền quyền | `translate` |

## Ghi chú thiết kế

Đội đã tự dùng ChatGPT cho tài liệu khách — làm sớm vừa giảm workload vừa đóng một lỗ hổng bảo mật. RÀNG BUỘC BẮT BUỘC: chỉ dịch phần chữ, giữ nguyên mọi con số và mã; từ điển thuật ngữ khoá cứng, không cho mô hình tự chọn từ; xuất bản song ngữ để người soát đối chiếu.

## Hợp đồng tool

| Tool | Vào | Ra |
|---|---|---|
| `doc_translate(file: str, glossary: str)` | file: str, glossary: str | Dịch tài liệu, xuất song ngữ |
| `comment_translate(text: str)` | text: str | Dịch comment của khách |
| `glossary_manage(action: str, term: dict = None)` | action: str, term: dict = None | Quản lý từ điển thuật ngữ |
| `spec_table_extract(file: str)` | file: str | Bóc bảng thông số từ ảnh hoặc PDF |

## Trước khi viết dòng code đầu tiên

Theo quy trình dựng sáu bước (chương 12 kiến trúc v1.0), bước 2 — **ngồi cạnh
người làm, ghi lại 20 thao tác thật** — là bước không được rút gọn. JD và khảo sát
không ghi thứ tự ưu tiên khi hai nguồn mâu thuẫn, cũng không ghi trường hợp ngoại
lệ nào phải hỏi khách. Những quy tắc ngầm đó chỉ hiện ra khi ngồi xem người ta làm.

Người ngồi cùng: Chị Bích Thủy, Chị Nhiên.
