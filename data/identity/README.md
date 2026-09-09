# F3 · Bảng ánh xạ định danh

Chép `identity_map.example.csv` thành `identity_map.csv` rồi điền dữ liệu thật.

File là CSV để merchandiser sửa được bằng Excel, không phải qua kỹ thuật.

## Vì sao cần

Mỗi khách một hệ mã riêng. Với 6 nhãn khách thì đây là điều kiện sống còn: chị
Trần Sương đang phải "tạo LS style + cập nhật OD của khách" như một đầu việc
riêng, tốn 120 phút mỗi lần, 2 lần một tuần.

## Cột

| Cột | Nghĩa |
|---|---|
| `ls_style` | Mã style của nhà máy |
| `customer_style` | Mã style của khách |
| `customer` | GARAN, HADDAD, JAKO, H&M, OSAKA, LTD |
| `account` | Account của khách |
| `market` | Thị trường (US, CA, EU…) |
| `upc` | Mã UPC |
| `material_code` | Mã vật tư |

## Trạng thái

Kỹ thuật thấp, **công sức thu thập ban đầu cao**. Chặn bởi khoảng trống **G9** —
cần bảng nhân sự khối BU theo mã nhân viên để biết ai phụ trách mảng nào ở khách nào.
