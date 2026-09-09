#!/bin/sh
# Tạo bucket, tài khoản ứng dụng và chính sách quyền. Chạy lại nhiều lần được.
set -e

ALIAS=local
mc alias set "$ALIAS" http://minio:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" >/dev/null

echo "==> Tạo bucket"
for b in lsth-raw lsth-templates lsth-identity lsth-work lsth-out lsth-archive; do
  mc mb --ignore-existing "$ALIAS/$b" >/dev/null
  echo "    $b"
done

echo "==> Bật versioning cho bucket ghi được"
# Ghi đè nhầm thì còn lấy lại được bản cũ — nguyên tắc 8.
for b in lsth-work lsth-out lsth-archive; do
  mc version enable "$ALIAS/$b" >/dev/null 2>&1 || true
done

echo "==> Khoá chống xoá cho dữ liệu gốc"
# lsth-raw giữ file gốc của khách và của merchandiser. Bật versioning để một lần
# xoá nhầm không mất vĩnh viễn.
mc version enable "$ALIAS/lsth-raw" >/dev/null 2>&1 || true

echo "==> Chính sách cho tài khoản ứng dụng"
cat > /tmp/lsth-app-policy.json <<'JSON'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ChiDocDuLieuGoc",
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:ListBucket", "s3:GetBucketLocation"],
      "Resource": [
        "arn:aws:s3:::lsth-raw", "arn:aws:s3:::lsth-raw/*",
        "arn:aws:s3:::lsth-templates", "arn:aws:s3:::lsth-templates/*",
        "arn:aws:s3:::lsth-identity", "arn:aws:s3:::lsth-identity/*"
      ]
    },
    {
      "Sid": "DocGhiVungLamViec",
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject", "s3:ListBucket",
                 "s3:GetBucketLocation", "s3:ListBucketVersions",
                 "s3:GetObjectVersion"],
      "Resource": [
        "arn:aws:s3:::lsth-work", "arn:aws:s3:::lsth-work/*",
        "arn:aws:s3:::lsth-out", "arn:aws:s3:::lsth-out/*",
        "arn:aws:s3:::lsth-archive", "arn:aws:s3:::lsth-archive/*"
      ]
    },
    {
      "Sid": "CamXoaMoiThu",
      "Effect": "Deny",
      "Action": ["s3:DeleteObject", "s3:DeleteObjectVersion", "s3:DeleteBucket"],
      "Resource": ["arn:aws:s3:::*"]
    }
  ]
}
JSON
mc admin policy create "$ALIAS" lsth-app /tmp/lsth-app-policy.json >/dev/null 2>&1 \
  || mc admin policy update "$ALIAS" lsth-app /tmp/lsth-app-policy.json >/dev/null 2>&1 \
  || true

echo "==> Tài khoản ứng dụng: $LSTH_S3_ACCESS_KEY"
mc admin user add "$ALIAS" "$LSTH_S3_ACCESS_KEY" "$LSTH_S3_SECRET_KEY" >/dev/null 2>&1 || true
mc admin policy attach "$ALIAS" lsth-app --user "$LSTH_S3_ACCESS_KEY" >/dev/null 2>&1 || true

echo ""
echo "===================================================================="
echo " MinIO đã sẵn sàng"
echo "===================================================================="
echo " API      http://localhost:9000"
echo " Console  http://localhost:9001   (đăng nhập bằng MINIO_ROOT_USER)"
echo ""
echo " Bucket        Quyền của tài khoản ứng dụng"
echo "   lsth-raw        chỉ đọc   <- file gốc, máy không ghi đè được"
echo "   lsth-templates  chỉ đọc   <- F4 kho khuôn đã duyệt"
echo "   lsth-identity   chỉ đọc   <- F3 bảng ánh xạ định danh"
echo "   lsth-work       đọc + ghi <- vùng làm việc"
echo "   lsth-out        đọc + ghi <- bản nháp giao người soát"
echo "   lsth-archive    đọc + ghi <- M4 kho lịch sử mùa"
echo ""
echo " Không tài khoản nào được xoá object (chính sách Deny)."
echo "===================================================================="
