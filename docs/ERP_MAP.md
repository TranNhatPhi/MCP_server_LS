# Bản đồ ERP LSTH

Rút từ 9 tài liệu **USE GUIDE ERP VERSION WEB** (2024–2026) trong `Use_guide/`.
Code tương ứng: [`core/erp.py`](../src/lsth_mcp/core/erp.py).

Đây là nguồn nội bộ, đọc được ngay, và nó trả lời được kha khá phần mà khoảng
trống **G1** đang chờ nhà cung cấp.

## Ba hệ thống, không phải một

| Hệ thống | Địa chỉ | Dùng cho |
|---|---|---|
| ERP chính | `https://erp-app.erpleadingstar.com/` | SO, BOM, PO, kho, sản xuất |
| Cổng vào | `https://erpleadingstar.com/` | trang chủ, điều hướng |
| Internal Purchasing | `https://internalpurchasing.erpleadingstar.com/` | mua sắm nội bộ (PR-PO), tài khoản riêng |

**Và có app di động**: [iOS](https://apps.apple.com/vn/app/ls-erp/id6756703497) ·
Android `com.company.erpmobile`. App dùng để quét QR/barcode báo sản lượng ép,
thêu, giao nhận thùng vớ.

> **Đây là phát hiện đáng giá nhất.** Một app di động buộc phải nói chuyện với
> một API HTTP. Câu hỏi G1 vì thế đổi từ *"ERP có API không"* thành *"xin được
> tài liệu và tài khoản cho API mà app di động đang dùng không"* — một câu hỏi
> dễ được trả lời "có" hơn nhiều.

## Đăng nhập

Tên đăng nhập là **mã số nhân viên**, độ dài theo công ty: LS 5 ký tự, LK 7, DA 6,
TH 8 (kể cả số 0 ở đầu). Dùng để kiểm tra chéo khi nhận bảng nhân sự chuẩn (G9).

> ⚠️ **Cẩm nang ghi mật khẩu mặc định là `123456` và chỉ *khuyến nghị* đổi.**
> Trước khi xin tài khoản riêng cho tự động hoá, nên hỏi IT còn bao nhiêu tài
> khoản đang để mật khẩu mặc định. Việc này không nằm trong chương trình giảm
> workload, nhưng đã thấy thì nên nói.

## Mười hai nhãn khách — khảo sát mới phủ sáu

Có trong ERP: `DE` Decathlon · `HA` Haddad\* · `GA` Garan\* · `IFG` · `LTD`\* ·
`H&M`\* · `JK` Jako\* · `JO` · `Osaka`\* · `Goruck` · `Kmart` · `Puma`

(\*) = có dữ liệu khảo sát. **Sáu nhãn còn lại — Decathlon, IFG, JO, Goruck,
Kmart, Puma — chưa có ai khai workload.** Đây là vùng mù mà cả hai đợt khảo sát
đều không chạm tới, và nó ảnh hưởng tới con số quy mô ở Phần A tài liệu v2.0.

## Quy tắc mã hoá đã có tài liệu — nguyên liệu trực tiếp cho F3

| Quy tắc | Nội dung | Nguồn |
|---|---|---|
| Style number khi import BOM | Haddad, IFG, Jako, Osaka → **Contract No (Ref#)**. Các nhãn khác → **customer style**. Cột B file BOM luôn là customer style | SO-BOM-PURCHASE, mục Import BOM |
| Sinh LS style | Để **trống** cột `ls style` khi Update SO thì ERP tự tạo LS style mới | mục Update SO JK |
| ID vendor | Viết liền, không dấu, **chữ hoa** | mục Tạo Vendor |
| UPC define | 4 loại code: `ContractNo`, `Colorcode`, `Gender`, `Size` | IN NHÃN OSAKA |
| Sheet forecast | `W{tuần}.{năm}`, ví dụ `W1.2025` | mục Import FC |
| Số đầu thùng vớ | 2 số cuối năm + 2 số tháng + 4–5 số tăng, ví dụ `26060001` | SOCK-THÊU |
| Loại đề xuất vải | `FB` vải chính · `FBO` vải bù · `FBS` viền | QUY TRINH XUAT-NHAP KHO |

Quy tắc style number đã được cài vào `domain.identity.erp_style_number()` — thiếu
trường cần dùng thì nó **báo lỗi**, không lặng lẽ lấy trường kia.

## Module và đường dữ liệu ra vào

**19 trên 25 module xuất được Excel.** Đường dự phòng qua file xuất/nhập mà kiến
trúc v1.0 dự trù là chắc chắn dùng được, kể cả khi không xin được API.

| Module | Đường trong menu | Import | Export | Server dùng |
|---|---|---|---|---|
| Sales Order | `Sales Order` | ✅ mỗi nhãn một template | ✅ | S2, S5 |
| **Read PDF** | `Sales Order → Read PDF` | ✅ | ✅ | **S1**, S2 |
| Master BOM | `Master BOM` | ✅ | ✅ | S2 |
| Pull BOM | `Sales Order → Pull BOM type → Pull BOM` | — | — | S2 |
| Purchase Order | `Purchase Order` | — | ✅ | S2 |
| Purchase Request | `Purchase Request` | — | ✅ | S2 |
| Material Packing | `Purchase → Material Packing` | — | ✅ | S2, S6 |
| FCR Master | `System → FCR Master` | ✅ | — | S5 |
| Forecast Report | `Forecast Report` | ✅ | ✅ | S5 |
| Vendor | `System → Vendor` | — | ✅ | S2 |
| Group Mail | `System → Group Mail` | — | — | S4 |
| UPC define | `System Setup → System → UPC define` | — | — | S3 |
| Storage Summary | `Inventory → Organization → Storage Summary` | — | ✅ | S5 |
| Receipt Entry | `Inventory → Receipt Entry` | ✅ | ✅ | S5 |
| Issued List | `Inventory → Issued → Issued List` | — | ✅ | S5 |
| Fabric Request | `Production → Cutting → FB Request` | ✅ | ✅ | S2, S4 |
| Production Schedule | `Production Schedule` | ✅ | ✅ | S5 |
| Final Result | `Final Result` | ✅ | ✅ | S5 |
| Shipping Plan | `Shipping Plan` | ✅ | ✅ | S5 |
| Kmart WIP | `Kmart WIP` | — | ✅ | S5 |

## Ba điều làm đổi cách dựng

### 1. ERP đã có sẵn tính năng đọc PDF

`Sales Order → Read PDF` bóc PDF của H&M ra file update SO. **Xem kỹ tính năng
này trước khi dựng S1** — có thể phần việc bóc PDF đã có sẵn một phần, và trùng
lặp thì vừa phí công vừa tạo hai nguồn sự thật (vi phạm nguyên tắc 3).

Việc cần làm: nhờ người dùng H&M mở màn hình đó, xem nó bóc được những trường gì.

### 2. Luồng BOM có bốn trạng thái, không phải một nút

```
Import BOM → Save → Submit (chọn người duyệt theo MSNV) → Approve / Reject
                                                              ↓
                                    Pull BOM type → Pull BOM (từ SO hoặc FC)
                                                              ↓
                                                      Purchase Order
```

Ràng buộc: **chỉ sửa item khi chưa submit hoặc đã bị reject**; item đã mua thì
không xoá khỏi BOM được. Hai ràng buộc này phải nằm trong hợp đồng tool của S2,
nếu không máy sẽ soạn ra thao tác mà ERP từ chối.

Đây cũng là chỗ có lỗi mà người dùng đã nêu ba lần: *báo lỗi BOM lúc Save thay vì
lúc Pull*. Hỏi nhà cung cấp trong cùng cuộc gọi lấp G1.

### 3. ERP đã tự gửi mail

`System → Group Mail` cấu hình To/CC/BCC theo nhãn hàng và loại đề xuất; ERP tự
gửi khi phòng cắt đề xuất vải và khi BU approve. Department: `CUTTING_FABRICREQUEST`,
`CUTTING`, `WAREHOUSE`.

Nghĩa là một phần của "14,8% quỹ thời gian cho email" có thể cắt được bằng cách
**cấu hình lại ERP**, không cần dựng gì. Đáng kiểm tra trước khi làm S4.

## Trạng thái chứng từ (Internal Purchasing)

`0.Draft` → `1.Submit` → `2.Approved` → `3.Release` → `4.Received`

Chuỗi duyệt là cấu hình theo nhà máy và **có tên người cụ thể** trong cẩm nang
(ví dụ chuỗi LS: PO → Mrs Mận → Mrs Uyên → Mr Phong → Mr Chow), có cả cơ chế bỏ
bước khi người duyệt đi công tác. S2 khi soạn PO nháp phải biết chuỗi này để
không gửi nhầm người.
