# Lộ trình sáu vòng

| Vòng | Thành phần | Kết quả nhìn thấy được | Điều kiện bắt đầu |
|---|---|---|---|
| **0** · tuần 1–2 | *không dựng gì* | Sửa 2 lỗi ERP · ban hành quy định trách nhiệm dữ liệu · thu lại khảo sát chuẩn hoá | Không có — làm ngay |
| **1** · tuần 2–5 | F1 F2 F3 F4 F5 + S1 + M2 | Bóc được tech pack 48–86 trang ra bảng; dịch được TP/Spec có kiểm soát thuật ngữ | Lấp xong G4, G5, G8 |
| **2** · tuần 5–9 | S2 + S3 | Sinh BOM nháp 202–374 dòng từ bảng vật tư gốc; tra được mã móc/sticker/UPC bằng một câu hỏi | Lấp xong G1, G6 (một phần) |
| **3** · tuần 9–13 | S4 + S5 + M3 + M4 | Bảng trạng thái thay việc dò mail; tự điền báo cáo test; tra được giá và báo cáo mùa trước | S2 chạy ổn định |
| **4** · tuần 13–18 | S6 + M1 | TLĐG và FDW bản nháp; theo dõi vòng đời mẫu | Có đủ file khuôn đã duyệt |
| **5** · sau thoả thuận khách | M5 | Tải PO, book FI, submit layout tự động | Khách đồng ý và cấp tài khoản riêng |

## Vòng lặp sáu bước cho mỗi server

Mỗi vòng 2–3 tuần, kết thúc bằng một năng lực dùng được thật.

| Bước | Nội dung | Thời gian | Sản phẩm |
|---|---|---|---|
| 1 | Chọn một đầu việc trong JD — theo tiêu chí tốn nhiều giờ, quy tắc rõ, ít rủi ro nếu sai. Không chọn theo cái nào dễ code | 1 ngày | Một dòng: cắt việc gì, của ai, hiện tốn bao nhiêu phút |
| 2 | **Ngồi cạnh người làm, ghi lại 20 thao tác thật.** Không hỏi "chị làm thế nào" mà xem chị ấy làm một mã hàng từ đầu đến cuối | 2–3 ngày | Bản ghi thao tác + danh sách quy tắc ngầm |
| 3 | Viết hợp đồng tool. Chưa viết code. Đưa merchandiser xem lại | 2 ngày | Bảng hợp đồng được xác nhận |
| 4 | Dựng server chạy được trên **một** mã hàng. Không làm tổng quát | 4–6 ngày | Server chạy được, có tài liệu cài đặt |
| 5 | Chạy song song năm mã hàng thật. Ghi lại mọi chỗ lệch và nguyên nhân | 3–5 ngày | Bảng so sánh + danh sách lỗi đã sửa |
| 6 | Bàn giao: tài liệu vận hành, hướng dẫn xử lý khi hỏng, **ít nhất hai người biết chạy** | 2 ngày | Tài liệu + buổi bàn giao 60 phút |

Bước 5 chính là thứ `scripts/write_gate.py record` ghi nhận, và bước đó mở cổng
quyền ghi ở nguyên tắc 2.

## Tiêu chí nghiệm thu định lượng

| Server | Đạt khi |
|---|---|
| lsth-techpack | Bóc đúng ≥ 95% trường bắt buộc trên 5 tech pack; **0 trường bịa ra** |
| lsth-drive | Tra đúng mã móc, sticker, UPC ≥ 98% trên 20 trường hợp phủ 4 thị trường |
| lsth-mail | Trích đúng ETD ≥ 90% trên 30 thư; không bỏ sót thư báo trễ |
| lsth-erp | BOM sinh ra khớp **100% dòng** trên 5 mã hàng — lệch một dòng là chưa đạt |
| lsth-packing | TLĐG nháp cần sửa dưới 20% số ô; **sai ở mục an toàn là chưa đạt bất kể tỷ lệ** |
| lsth-status | Bảng khớp thực tế ≥ 95%; cảnh báo trễ trước ít nhất 3 ngày |
| lsth-portal | Tải và book đúng 20 lần liên tiếp; **tự dừng và báo người khi giao diện đổi** |

## Ba điều kiện tiên quyết

Không có ba điều này thì mọi lộ trình ở trên chỉ là giấy.

1. **Quỹ thời gian kỹ thuật được bảo vệ** — toàn thời gian hoặc tối thiểu 60%.
   Đây là rủi ro lớn nhất của chương trình: 17 thành phần cần khoảng 18 tuần với
   một người toàn thời gian; bị kéo sang việc khác thì thành 30 tuần.
2. **Một merchandiser đầu mối, 4 giờ mỗi tuần**, cộng các buổi ngồi cùng theo vòng.
   Không có người nghiệm thu thì server dựng xong cũng không ai dùng.
3. **Quyết định về phạm vi bảo mật trước khi mở rộng công cụ ngoài.** Đội đã tự
   dùng ChatGPT cho tài liệu khách — cần khung trước, không phải sau.
