# lsth-mcp

Hệ thống MCP server giảm workload khối BU — Lucky Star LSTH.

Dựng theo **Tài liệu hợp nhất v2.0** (09/09/2026) và **Kiến trúc giải pháp MCP
v1.0** (08/09/2026). Toàn bộ 17 thành phần đã có chỗ đứng trong cây thư mục; phần
nền và lớp đọc/ghi đã chạy được, các server nghiệp vụ có hợp đồng tool đã chốt và
ghi rõ khoảng trống dữ liệu đang chặn.

## Cài và chạy

```bash
python3 -m pip install -e .          # cần Python 3.10+ cho MCP SDK
make test                            # 43 kiểm thử, không cần thư viện ngoài
make status                          # bức tranh 17 thành phần
make run                             # MCP server, chế độ stdio
make run-http                        # chế độ HTTP cho máy chủ nội bộ
```

Lớp đọc/ghi (`lsth_mcp.io`) chạy được trên **Python 3.9** mà không cần MCP SDK —
đủ để dùng như thư viện hoặc chạy script trước khi hạ tầng sẵn sàng.

## Nối vào Claude Cowork

```bash
python3.13 -m venv .venv && .venv/bin/pip install -e .
.venv/bin/python scripts/make_demo_data.py   # dữ liệu giả để thử
./scripts/serve.sh                           # server + URL công khai
```

Script in ra URL dạng `https://…trycloudflare.com/mcp/<token>` — dán vào
**Cowork → Customize → Connectors → + → Add custom connector**.

Claude gọi từ đám mây của Anthropic chứ không phải từ máy bạn, nên bắt buộc phải
có URL công khai; `localhost` không dùng được. Chi tiết và cách lên máy chủ thật:
[`docs/DEPLOY.md`](docs/DEPLOY.md).

## Cây thư mục

```
lsth-mcp/
├── config/                  Cấu hình: vùng dữ liệu, quy ước tên, thiết lập chạy
├── data/
│   ├── raw/                 File gốc — CHỈ ĐỌC, máy không bao giờ ghi vào đây
│   ├── work/                Vùng làm việc, bản trung gian
│   ├── out/                 Bản nháp giao cho người soát
│   ├── templates/           F4 · kho khuôn đã duyệt
│   ├── identity/            F3 · bảng ánh xạ định danh
│   ├── eval/                F5 · bộ ca kiểm thử chất lượng
│   ├── state/               Trạng thái cổng quyền ghi
│   └── audit/               Nhật ký lệnh gọi, giữ 12 tháng
├── docker/                  MinIO — kho lưu trữ file (docker compose)
├── docs/                    Kiến trúc, hợp đồng tool, khoảng trống dữ liệu, lộ trình
├── scripts/                 serve.sh · status · write_gate · scan_drive · run_eval
├── src/lsth_mcp/
│   ├── core/                Lớp nền
│   │   ├── models.py            F2 · năm thực thể chuẩn
│   │   ├── provenance.py        Nguyên tắc 4 · mọi giá trị kèm nguồn
│   │   ├── envelope.py          Khung {ok, data, sources, warnings, error}
│   │   ├── errors.py            Nguyên tắc 5 · lỗi nói được phải làm gì
│   │   ├── permissions.py       Ma trận quyền + cổng "đọc trước, ghi sau"
│   │   ├── zones.py             Nguyên tắc 6 · bốn vùng dữ liệu
│   │   ├── erp.py               Bản đồ ERP rút từ 9 cẩm nang nội bộ
│   │   ├── audit.py             Nhật ký sáu trường
│   │   ├── paths.py             Ràng buộc đường dẫn + quy ước tên file
│   │   └── config.py
│   ├── io/                  ⬅ CÁC MODULE ĐỌC GHI
│   │   ├── base.py              ReadResult · WriteResult
│   │   ├── registry.py          read_any() · list_files() — điểm vào đọc
│   │   ├── readers/             excel · pdf · tabular · jsonio · text/docx
│   │   ├── writers/             safe · excel · structured
│   │   └── storage/             đĩa cục bộ hoặc MinIO — reader không cần biết
│   ├── domain/              F3 identity · F4 templates · F5 evalset
│   ├── servers/             12 server: S1–S7, M1–M5
│   └── server.py            F1 · cổng điều phối, điểm vào MCP
└── tests/
```

## Lớp đọc/ghi

### Tìm file và xem cây dữ liệu

Gateway có 16 tool, gồm `file_search` và `file_tree` dùng metadata để duyệt
MinIO hoặc các thư mục dữ liệu cục bộ, không đọc nội dung file:

```text
file_search(query="S2749189", root="raw")
file_search(query=".xlsx", root="s3://lsth-raw/orders/")
file_tree(root="raw", max_depth=4, limit=200)
file_tree(root="s3://lsth-raw/", query="S2749189 BOM")
file_tree(root="raw", query="cong viec")
```

`file_search` và `file_tree(query=...)` tìm theo mọi từ trong tên/đường dẫn tương đối,
không phân biệt hoa thường và dấu tiếng Việt (ví dụ `cong viec` tìm được `công việc`).
`file_tree` giữ các thư mục cha của file khớp, trả cả cây JSON và `tree_text` dễ đọc.
Bỏ `query` hoặc truyền chuỗi rỗng để xem toàn cây. `matched_count` là số file khớp
trong phần đã quét, trước khi áp `limit`; không phải tổng toàn kho nếu `scan_truncated=true`.
Thư mục được suy ra từ file nên không
hiển thị thư mục rỗng. Cả hai giữ đường dẫn nguồn `s3://` khi dùng MinIO.
`limit` giới hạn kết quả (tối đa 1.000 file); `scan_limit` giới hạn metadata được xét
(mặc định 10.000, tối đa 100.000). `truncated`/`scan_truncated` báo kết quả chưa đầy đủ;
`depth_limited` và `collapsed` báo cây đang thu gọn theo `max_depth`.

Sau khi cập nhật, cần nạp lại tiến trình server và danh sách tool ở MCP client.
Thêm tool không tự khắc phục việc client chưa nạp kết nối MCP vào phiên chat.

### Đọc — `lsth_mcp.io.readers`

| Module | Định dạng | Dùng cho |
|---|---|---|
| `excel.py` | `.xlsx` `.xlsm` | BOM 30 cột, file khảo sát, file xuất ERP — tự dò dòng tiêu đề |
| `pdf.py` | `.pdf` | Tech pack 48–86 trang; báo rõ trang nào là ảnh scan |
| `tabular.py` | `.csv` `.tsv` | Bảng ánh xạ định danh, dữ liệu trao đổi |
| `jsonio.py` | `.json` `.jsonl` | Hợp đồng dữ liệu giữa server, bộ ca kiểm thử |
| `text.py` | `.txt` `.md` `.docx` | Tài liệu mô tả công việc |

Mọi reader trả về `ReadResult` mang theo `sources` — file, sheet, dòng, trang.
Điểm vào chung là `read_any(path)`, tự chọn đúng reader theo đuôi file.

```python
from lsth_mcp.io import read_any

result = read_any("BOM_66P866.xlsx", sheet="BOM")
result.rows[0]                  # {"Style": "66P866", "Material Code": ...}
result.sources[0].label()       # "BOM_66P866.xlsx · sheet BOM · dòng 5"
```

### Ghi — `lsth_mcp.io.writers`

Mọi thao tác ghi đi qua **`SafeWriter`**, nơi bốn ràng buộc được áp cùng lúc:

1. **Cổng quyền ghi** — nguyên tắc 2: server chỉ ghi được sau khi chạy đúng 5 mã hàng thật
2. **Vùng ghi** — chỉ `work/`, `out/`, `state/`; không bao giờ đè lên `raw/`
3. **Ghi nguyên tử** — file tạm rồi đổi tên, không để lại file nửa vời
4. **Sao lưu trước khi đè** — nguyên tắc 8, luôn giữ được đường lùi

```python
from lsth_mcp.io import SafeWriter, write_rows

writer = SafeWriter.for_server("s6_packing", role="merchandiser_owner",
                               resource="packing")
write_rows(writer, "data/out/66P866_US_TLDG_v1.xlsx", rows,
           needs_human={0: ["upc"]})   # ô máy không tra được nguồn -> tô vàng
```

Không hàm nào ở lớp ghi gửi mail, đặt hàng hay đẩy dữ liệu ra hệ thống khách —
nguyên tắc 1, *máy soạn nháp, người bấm nút*.

## Kho lưu trữ file

Mặc định đọc thư mục `data/` trên đĩa. Bật MinIO thì thêm `LSTH_STORAGE=minio` vào
`.env` — không sửa dòng code nào, reader và writer đều không biết file nằm ở đâu.

```bash
make minio-up      # bật MinIO, tạo 6 bucket kèm chính sách quyền
make minio-sync    # đẩy data/ lên kho
```

Sáu bucket, mỗi vùng một chính sách: `lsth-raw`, `lsth-templates`, `lsth-identity`
là **chỉ đọc ngay ở tầng MinIO** — code sai cũng không ghi đè được file gốc.
Chi tiết: [`docs/STORAGE.md`](docs/STORAGE.md).

## Tám nguyên tắc, nằm ở đâu trong code

| # | Nguyên tắc | Thực thi ở |
|---|---|---|
| 1 | Máy soạn nháp, người bấm nút | `io/writers/` chỉ ghi xuống ổ nội bộ; dấu "BẢN NHÁP" trên mọi file sinh ra |
| 2 | Đọc trước, ghi sau | `core/permissions.py` · `WriteGate` — 5 mã hàng mới mở |
| 3 | Một nguồn sự thật | `errors.ConflictError` · `domain/identity.py` báo mâu thuẫn, không tự chọn |
| 4 | Trả lời kèm nguồn | `core/provenance.py` · `sources[]` bắt buộc trong mọi envelope |
| 5 | Hỏng thì im lặng, không đoán | `core/errors.py` · `BomLine._to_float` · `net_consumption()` trả None |
| 6 | Dữ liệu ở đâu, xử lý ở đó | `core/zones.py` · `config/data_zones.yaml` |
| 7 | Hai người biết vận hành | README từng server ghi người nghiệm thu; `docs/RUNBOOK.md` |
| 8 | Luôn giữ được đường làm tay | Sao lưu trước khi đè; `raw/` bất khả xâm phạm ở **cả hai** tầng — Python và chính sách MinIO |

## Trạng thái hiện tại

**Chạy được:** F1 cổng điều phối · F2 mô hình dữ liệu · F3 ánh xạ định danh ·
F4 kho khuôn · F5 bộ đánh giá · toàn bộ lớp đọc/ghi · S1 `bom_extract` và
`diff_check`.

**Chờ lấp khoảng trống dữ liệu:** 9 server còn lại. Xem `docs/DATA_GAPS.md` —
và `make status` để biết cái nào đang chặn cái nào.

**Đã đọc `Use_guide/`** (9 cẩm nang ERP nội bộ) — kết quả ở `docs/ERP_MAP.md`.
Lấp được một phần G1: ERP là web app **có app di động**, nên phía sau gần như
chắc chắn có API HTTP; và **19/25 module xuất được Excel** nên đường dự phòng
qua file chắc chắn dùng được. Quy tắc nối mã của F3 cũng đã có văn bản và đã
được cài vào `domain.identity.erp_style_number()`.

Không nên dựng thêm thành phần nào trước khi lấp xong **G1, G4, G5 và ít nhất một
nửa G6**. Dựng trên dữ liệu chưa rõ nghĩa thì phải làm lại từ đầu, và làm lại lần
hai sẽ mất niềm tin của người dùng.
