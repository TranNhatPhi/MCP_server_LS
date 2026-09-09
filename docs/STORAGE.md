# Kho lưu trữ file — MinIO

Code: [`io/storage/`](../src/lsth_mcp/io/storage/) · Hạ tầng: [`docker/`](../docker/)

## Chạy

```bash
cp docker/.env.example docker/.env      # rồi ĐỔI hai mật khẩu trong đó
docker compose -f docker/docker-compose.yml up -d
docker compose -f docker/docker-compose.yml logs minio-init
```

Console: <http://localhost:9001> · API S3: <http://localhost:9000>

Bật chế độ MinIO cho lsth-mcp — tạo file `.env` ở gốc dự án:

```ini
LSTH_STORAGE=minio
LSTH_S3_ENDPOINT=localhost:9000
LSTH_S3_ACCESS_KEY=lsth-app
LSTH_S3_SECRET_KEY=<lấy từ docker/.env>
LSTH_S3_SECURE=false
```

Nạp dữ liệu từ `data/` lên kho:

```bash
python3 scripts/sync_to_minio.py           # đẩy tất cả
python3 scripts/sync_to_minio.py raw       # chỉ một vùng
python3 scripts/sync_to_minio.py --list    # xem trong kho có gì
```

Bỏ `LSTH_STORAGE=minio` là quay lại đọc thư mục `data/` trên đĩa. Không phải sửa
dòng code nào — tool, reader và writer đều không biết file nằm ở đâu.

## Sáu bucket, mỗi vùng một chính sách

| Bucket | Quyền của `lsth-app` | Chứa gì |
|---|---|---|
| `lsth-raw` | **chỉ đọc** | Tech pack, BOM, file xuất từ ERP — bản gốc |
| `lsth-templates` | **chỉ đọc** | F4 · khuôn đã duyệt |
| `lsth-identity` | **chỉ đọc** | F3 · bảng ánh xạ định danh |
| `lsth-work` | đọc + ghi | Vùng làm việc, bản trung gian |
| `lsth-out` | đọc + ghi | Bản nháp giao người soát |
| `lsth-archive` | đọc + ghi | M4 · kho lịch sử mùa |

Không tài khoản nào được **xoá** object — chính sách có mệnh đề `Deny` cho
`s3:DeleteObject` trên mọi bucket. Ba bucket ghi được đều bật versioning.

### Vì sao tách bucket thay vì một bucket nhiều thư mục

Để chặn ở **hai lớp độc lập**:

1. Trong Python — `SafeWriter` và cờ `writable` của store
2. Trong MinIO — chính sách IAM gắn với tài khoản `lsth-app`

Code sai một lớp thì lớp kia vẫn giữ. Đã kiểm chứng: ép `writable=True` cho
`lsth-raw` rồi ghi, MinIO vẫn trả `AccessDenied`.

Đây là cách thực thi nguyên tắc 8 — *luôn giữ được đường làm tay*: dù hệ thống
hỏng thế nào, `lsth-raw` vẫn nguyên vẹn vì tài khoản của máy không có quyền đụng vào.

## Cách gọi

Tool nhận cả hai dạng:

```
DEMO_BOM_S2749189.xlsx              # tự dò theo thứ tự raw → templates → identity → work → out → archive
s3://lsth-raw/DEMO_BOM_S2749189.xlsx  # chỉ đích danh
```

Thứ tự dò đặt `raw` trước `work` có chủ ý: tìm dữ liệu gốc trước, tránh vô tình
đọc phải bản nháp do máy tự dựng.

## Nguồn dẫn ra vẫn đúng

Mọi kết quả trỏ về URI trong kho, không phải file tạm:

```json
"sources": [{"file": "s3://lsth-raw/DEMO_BOM_S2749189.xlsx",
             "sheet": "BOM", "row": 42}]
```

Nhật ký cũng ghi URI, nên câu hỏi *"bản nháp này dựng từ đâu"* vẫn trả lời được
sau khi file cục bộ đã bị xoá.

## Bộ nhớ đệm

File tải về nằm ở `data/cache/<etag>__<tên>`. Lần sau nếu etag không đổi thì dùng
lại, không tải lại — tech pack 48–86 trang không nên tải mỗi lần hỏi. Object đổi
nội dung là etag đổi, cache tự hết hiệu lực. Xoá `data/cache/` lúc nào cũng an toàn.

## Lên môi trường thật

Bản compose này chạy MinIO **một node, không TLS**, đủ để thử và cho một nhóm nhỏ
dùng nội bộ. Trước khi đưa dữ liệu khách vào, cần:

1. **Bật TLS** — hiện `LSTH_S3_SECURE=false`, dữ liệu đi trong mạng không mã hoá
2. **Sao lưu volume `lsth-minio-data`** — versioning chống xoá nhầm, không chống hỏng ổ đĩa
3. **Đổi mật khẩu** trong `docker/.env` — file mẫu để mật khẩu giả
4. **Lấp khoảng trống G8** trước khi nạp tech pack thật (vùng Z3, NDA)
5. Cân nhắc chế độ phân tán nếu cần chịu lỗi ổ đĩa

## Sự cố hay gặp

| Triệu chứng | Nguyên nhân |
|---|---|
| `storage_unavailable` khi khởi động | MinIO chưa chạy. `docker compose -f docker/docker-compose.yml ps` |
| `Bị từ chối khi ghi s3://lsth-raw/...` | Đúng như thiết kế. Ghi vào `lsth-work` hoặc `lsth-out` |
| `NoSuchBucket` | Container `minio-init` chưa chạy xong. Xem log của nó |
| `Không tìm thấy '...' trong kho object` | Chưa nạp. `python3 scripts/sync_to_minio.py` |
| Đọc ra dữ liệu cũ | Bộ nhớ đệm theo etag. Nếu ghi đè bằng công cụ ngoài mà etag không đổi thì xoá `data/cache/` |
