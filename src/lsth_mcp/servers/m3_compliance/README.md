# M3 · lsth-compliance

Chứng từ và kiểm nghiệm: COC, RSL, CPSIA, TC, GACC

| | |
|---|---|
| Vòng | 3 |
| Nhóm | MỚI |
| Ưu tiên | Cao |
| Độ khó | Trung bình |
| Phụ thuộc | S1, M4, G4 |
| Chặn bởi | G4 |
| Nghiệm thu | Chị Phạm Hương Vân, Chị Bích Thủy, Chị Ngọc Ánh |
| Miền quyền | `compliance` |

## Ghi chú thiết kế

7,1% quỹ thời gian toàn khối; riêng chị Phạm Hương Vân là 50%. Giá trị kép: vừa giảm giờ vừa giảm rủi ro pháp lý — thiếu chứng nhận CPSIA có thể bị giữ hàng ở hải quan.

## Hợp đồng tool

| Tool | Vào | Ra |
|---|---|---|
| `test_report_fill(manual: str, report: str)` | manual: str, report: str | Tự điền báo cáo test từ manual khách |
| `tc_match(po: str, tc_files: list)` | po: str, tc_files: list | Dò TC vải NCC gửi khớp với từng mã hàng |
| `coc_build(style: str, reports: list)` | style: str, reports: list | Dựng COC từ các báo cáo |
| `cert_expiry_check()` | — | Chứng nhận sắp hết hiệu lực |
| `gacc_package(style: str)` | style: str | Đóng gói hồ sơ GACC |

## Trước khi viết dòng code đầu tiên

Theo quy trình dựng sáu bước (chương 12 kiến trúc v1.0), bước 2 — **ngồi cạnh
người làm, ghi lại 20 thao tác thật** — là bước không được rút gọn. JD và khảo sát
không ghi thứ tự ưu tiên khi hai nguồn mâu thuẫn, cũng không ghi trường hợp ngoại
lệ nào phải hỏi khách. Những quy tắc ngầm đó chỉ hiện ra khi ngồi xem người ta làm.

Người ngồi cùng: Chị Phạm Hương Vân, Chị Bích Thủy, Chị Ngọc Ánh.
