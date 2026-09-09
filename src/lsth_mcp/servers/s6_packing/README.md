# S6 · lsth-packing

TLĐG, FDW, PT8, tính kích túi

| | |
|---|---|
| Vòng | 4 |
| Nhóm | Server v1.0 |
| Ưu tiên | Trung bình |
| Độ khó | Trung bình |
| Phụ thuộc | S1, S3, F4, G4 |
| Chặn bởi | G4 |
| Nghiệm thu | Chị Ly, Chị Hạnh |
| Miền quyền | `packing` |

## Ghi chú thiết kế

Luồng rủi ro cao nhất: TLĐG sai dẫn tới đóng gói sai, hàng bị khách trả. Phải chạy song song ít nhất 5 mã hàng và có người soát 100% trước khi tin. Sai ở mục an toàn (vị trí bắn tag, loại đạn) là chưa đạt bất kể tỷ lệ.

## Hợp đồng tool

| Tool | Vào | Ra |
|---|---|---|
| `tldg_draft(style: str, market: str)` | style: str, market: str | File TLĐG nháp dựng từ khuôn đã duyệt |
| `fdw_build(images: list, specs: dict)` | images: list, specs: dict | FDW nháp |
| `pt8_compose(style: str)` | style: str | Bộ ảnh PT8 |
| `polybag_size(specs: dict, fold_ratio: float)` | specs: dict, fold_ratio: float | Kích thước túi |

## Trước khi viết dòng code đầu tiên

Theo quy trình dựng sáu bước (chương 12 kiến trúc v1.0), bước 2 — **ngồi cạnh
người làm, ghi lại 20 thao tác thật** — là bước không được rút gọn. JD và khảo sát
không ghi thứ tự ưu tiên khi hai nguồn mâu thuẫn, cũng không ghi trường hợp ngoại
lệ nào phải hỏi khách. Những quy tắc ngầm đó chỉ hiện ra khi ngồi xem người ta làm.

Người ngồi cùng: Chị Ly, Chị Hạnh.
