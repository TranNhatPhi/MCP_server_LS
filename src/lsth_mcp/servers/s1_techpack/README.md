# S1 · lsth-techpack

Bóc tech pack PDF (48–86 trang) và BOM xlsx thành JSON chuẩn theo hợp đồng F2.

| | |
|---|---|
| Vòng | 1 |
| Ưu tiên | Rất cao |
| Phụ thuộc | F2 (mô hình dữ liệu), F4 (kho khuôn) |
| Nghiệm thu | Chị Thương, chị Quỳnh |
| Quyền | chỉ đọc — server này không bao giờ cần quyền ghi |

## Hợp đồng tool

| Tool | Vào | Ra |
|---|---|---|
| `techpack_parse(file)` | PDF tech pack | `Style` + trang bóc được từng trường |
| `bom_extract(file, sheet)` | BOM xlsx | `BomLine[]` + danh sách dòng thiếu trường |
| `spec_lookup(file, style, size)` | PDF + mã hàng | đoạn thông số kèm số trang |
| `diff_check(techpack, bom)` | cả hai | danh sách mâu thuẫn giữa hai nguồn |

## Tiêu chí nghiệm thu

Bóc đúng ≥ 95% trường bắt buộc trên 5 tech pack; **0 trường bịa ra**. Vế thứ hai
quan trọng hơn: thà để trống và báo "cần người điền" còn hơn điền sai.

## Còn thiếu để hoàn thiện

`techpack_parse` mới bóc được mã hàng và mùa. Màu, size, khách và bảng thông số
cần bản ghi 20 thao tác của chị Thương và chị Quỳnh (khoảng trống **G6**) — vì
quy tắc đọc tech pack nằm trong đầu người làm, không có trong tài liệu nào.
