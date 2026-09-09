# F5 · Bộ đánh giá chất lượng

Chạy lại bộ này mỗi khi sửa hoặc nâng cấp một server, **trước** khi mở cho người
dùng thật.

## Vì sao cần

Buổi thử ngày 07/09 ghi nhận mô hình giải thích sai 3 thuật ngữ ngành và **bịa 2
từ viết tắt**. Không đo thì không biết đang tốt lên hay xấu đi.

## Vật liệu

- Hạt giống: 36 cặp hỏi đáp trong `erp_pilot.jsonl` — chép vào thư mục này
- Cần bổ sung: 5 mã hàng có BOM và TLĐG đã duyệt làm đáp án (khoảng trống **G4**)
- Ca bẫy: câu hỏi về từ viết tắt không tồn tại, đáp án đúng là "không biết".
  Xem `term-002` trong file mẫu — `expected: null` nghĩa là chỉ cần không bịa.

## Luật chấm

Trả lời không dẫn nguồn là **trượt**, dù nội dung đúng (nguyên tắc 4).

## Chạy

```bash
python scripts/run_eval.py
```
