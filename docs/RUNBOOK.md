# Vận hành

Nguyên tắc 7: **không server nào được bàn giao khi chỉ một người hiểu nó.** Tài
liệu này để người thứ hai chạy được hệ thống mà không phải hỏi người dựng.

## Kiểm tra nhanh

```bash
make status                                     # 17 thành phần, cái nào chặn cái nào
PYTHONPATH=src python3 scripts/write_gate.py list   # server nào đang mở quyền ghi
make test                                       # 43 kiểm thử
```

## Mở quyền ghi cho một server

Theo nguyên tắc 2, server ra mắt ở chế độ chỉ đọc. Mở theo đúng ba bước:

```bash
# 1. Chạy song song: merchandiser làm tay như cũ, máy làm song song, so kết quả
# 2. Ghi nhận từng mã hàng đã khớp
PYTHONPATH=src python3 scripts/write_gate.py record s2_erp 66P866
# 3. Đủ 5 mã thì mở
PYTHONPATH=src python3 scripts/write_gate.py unlock s2_erp
```

Phát hiện sai lệch sau khi đã mở thì khoá lại ngay:

```bash
PYTHONPATH=src python3 scripts/write_gate.py lock s2_erp
```

Ngoài ra còn một công tắc chung: `LSTH_WRITE_ENABLED=false` trong `.env` chặn mọi
thao tác ghi bất kể cổng từng server đã mở hay chưa.

## Khi có sự cố

| Triệu chứng | Việc cần làm |
|---|---|
| Tool trả `ok: false` | Đọc `error.hint` — mọi lỗi đều nói phải làm gì tiếp |
| Nghi kết quả sai | `audit_tail` hoặc đọc `data/audit/calls-YYYY-MM.jsonl`: bản nháp dựng lúc nào, từ file nào |
| File bị máy ghi đè nhầm | Bản cũ nằm ở `<thư mục>/_backup/` kèm dấu thời gian |
| Khách hỏi "vì sao TLĐG mã này sai" | Tra nhật ký ra: dựng lúc nào, nguồn nào, ai duyệt |
| Nghi rò rỉ dữ liệu | Nhật ký cho biết ai đã đọc gì trong khoảng thời gian nào |
| Hệ thống hỏng hoàn toàn | **Nguyên tắc 8** — công việc vẫn chạy như trước. `data/raw` nguyên vẹn, không có gì phụ thuộc vào máy |

## Nhật ký

Sáu trường bắt buộc theo chương 11: ai gọi, lúc nào, tool nào, tham số gì, đọc
file nào, kết quả sao. Giữ tối thiểu 12 tháng.

```bash
python3 -c "
import sys; sys.path.insert(0, 'src')
from lsth_mcp.core.audit import AuditLog
from lsth_mcp.core.config import get_settings
cfg = get_settings()
print(AuditLog(cfg.audit_dir).prune())   # xoá file quá hạn 12 tháng
"
```

Nhật ký cũng là nguồn số liệu đo hiệu quả: bao nhiêu lượt dùng, tool nào không ai
dùng thì nên bỏ.

## Hai người biết vận hành

| Thành phần | Người 1 | Người 2 |
|---|---|---|
| Cổng điều phối, lớp đọc/ghi | Phi | *(chưa có — phải điền trước khi bàn giao)* |
| S1 techpack | Phi | *(chưa có)* |

Bảng này trống là **chưa đủ điều kiện hoàn thành** theo chương 13.
