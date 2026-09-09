# Chuẩn viết tool

Chương 15 kiến trúc v1.0, áp cho mọi server.

## Đặt tên

Mẫu **danh_từ + động_từ**, chữ thường, gạch dưới: `bom_generate`, `etd_extract`,
`sof_lookup`. Không đặt tên mơ hồ kiểu `get_data` hay `process`.

## Khung trả về

Mọi tool trả về cùng một khung. `sources` là **bắt buộc** theo nguyên tắc 4.

```json
{
  "ok": true,
  "data": { },
  "sources": [{"file": "BOM_66P866.xlsx", "sheet": "BOM", "row": 42}],
  "warnings": ["3/202 dòng thiếu trường bắt buộc — cần người điền"],
  "error": null
}
```

Dùng `core.envelope.ok()` và `core.envelope.fail()`, đừng tự dựng dict.

## Lỗi

Lỗi phải nói được người dùng **cần làm gì**:

> ✅ "Không tìm thấy UPC cho style X màu Y size Z trong ổ chung — cần tra trên hệ thống khách"
>
> ❌ "Error 500"

Mọi lỗi kế thừa `core.errors.LsthError` và mang `hint`. Trong `BaseServer.call()`,
lỗi tự động thành envelope — tool cứ ném lỗi, không cần bắt.

## Viết một tool mới

```python
def sof_lookup(self, style: str, market: str) -> Dict[str, Any]:
    """Tra PackingSpec từ SOF theo mã hàng và thị trường."""
    def handler(trace: CallTrace) -> Dict[str, Any]:
        result = read_any(path, trace=trace)      # trace ghi file đã đọc vào nhật ký
        if not hits:
            raise NotFoundError("…", hint="…")     # nguyên tắc 5: dừng, không đoán
        return ok(data, sources=result.sources, warnings=[...])
    return self.call("sof_lookup", {"style": style, "market": market}, handler)
```

`self.call()` lo phần nhật ký sáu trường và đổi lỗi thành envelope. Phần thân chỉ
còn nghiệp vụ.

## Phiên bản

Đánh theo mẫu `v1.0`. **Đổi hợp đồng tool là đổi số đầu**, và phải báo trước cho
người dùng.

## Trước khi viết dòng code đầu tiên

Bước 2 của quy trình dựng — *ngồi cạnh người làm, ghi lại 20 thao tác thật* — là
bước **không được rút gọn**. Không hiểu nghiệp vụ thì không viết nổi hợp đồng tool.

Cám dỗ lớn nhất khi muốn đi nhanh là bỏ bước 2 và code luôn theo tài liệu JD.
JD ghi "lấy thông tin trong DC, LPO, MSRP, SO form, UPC chung, file đặt móc…" —
nhưng không ghi thứ tự ưu tiên khi hai nguồn mâu thuẫn, không ghi trường hợp ngoại
lệ nào phải hỏi khách. Những quy tắc ngầm đó chỉ hiện ra khi ngồi xem người ta làm.
