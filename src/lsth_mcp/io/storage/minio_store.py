"""Kho object MinIO (giao thức S3).

Mỗi vùng dữ liệu một bucket riêng, để chính sách quyền cắm được ở tầng lưu trữ:
tài khoản ứng dụng không ghi được vào lsth-raw dù code có sai. Xem
docker/init/setup.sh.

File tải về được lưu tạm ở data/cache và dùng lại theo etag — tech pack 48–86
trang không nên tải lại mỗi lần hỏi.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional

from ...core.errors import LsthError, NotFoundError, ValidationError
from .base import ObjectInfo, check_key, content_type_for

try:
    from minio import Minio
    from minio.error import S3Error
except ImportError:  # pragma: no cover
    Minio = None  # type: ignore[assignment]
    S3Error = Exception  # type: ignore[assignment,misc]


class StorageUnavailableError(LsthError):
    code = "storage_unavailable"


def _require_sdk() -> None:
    if Minio is None:
        raise StorageUnavailableError(
            "Chưa cài thư viện minio nên không nối được kho object.",
            hint="Chạy: pip install 'lsth-mcp[minio]'  (hoặc pip install minio)",
        )


@dataclass
class MinioStore:
    """Một bucket MinIO."""

    bucket: str
    client: Any
    endpoint: str
    writable: bool = False
    cache_dir: Optional[Path] = None

    @property
    def name(self) -> str:
        return self.bucket

    # ---- dựng -------------------------------------------------------------

    @classmethod
    def connect(
        cls,
        bucket: str,
        *,
        endpoint: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        secure: Optional[bool] = None,
        writable: bool = False,
        cache_dir: Optional[Path] = None,
    ) -> "MinioStore":
        _require_sdk()
        endpoint = endpoint or os.environ.get("LSTH_S3_ENDPOINT", "localhost:9000")
        access_key = access_key or os.environ.get("LSTH_S3_ACCESS_KEY", "")
        secret_key = secret_key or os.environ.get("LSTH_S3_SECRET_KEY", "")
        if not access_key or not secret_key:
            raise StorageUnavailableError(
                "Thiếu khoá truy cập kho object.",
                hint="Đặt LSTH_S3_ACCESS_KEY và LSTH_S3_SECRET_KEY trong .env "
                     "(xem docker/.env.example).",
            )
        if secure is None:
            secure = os.environ.get("LSTH_S3_SECURE", "false").lower() in {"1", "true", "yes"}

        client = Minio(endpoint.replace("http://", "").replace("https://", ""),
                       access_key=access_key, secret_key=secret_key, secure=secure)
        return cls(bucket=bucket, client=client, endpoint=endpoint,
                   writable=writable, cache_dir=cache_dir)

    # ---- đọc --------------------------------------------------------------

    def uri(self, key: str) -> str:
        return f"s3://{self.bucket}/{check_key(key)}"

    def exists(self, key: str) -> bool:
        try:
            self.client.stat_object(self.bucket, check_key(key))
            return True
        except S3Error:
            return False

    def stat(self, key: str) -> ObjectInfo:
        key = check_key(key)
        try:
            st = self.client.stat_object(self.bucket, key)
        except S3Error as exc:
            raise self._not_found(key, exc) from exc
        return ObjectInfo(key=key, size=st.size, last_modified=st.last_modified,
                          etag=(st.etag or "").strip('"'), bucket=self.bucket)

    def list(self, prefix: str = "", limit: int = 200) -> List[ObjectInfo]:
        out: List[ObjectInfo] = []
        try:
            for obj in self.client.list_objects(self.bucket, prefix=prefix or None,
                                                recursive=True):
                if obj.is_dir:
                    continue
                out.append(ObjectInfo(
                    key=obj.object_name, size=obj.size or 0,
                    last_modified=obj.last_modified,
                    etag=(obj.etag or "").strip('"'), bucket=self.bucket))
                if len(out) >= limit:
                    break
        except S3Error as exc:
            raise self._wrap(exc, f"liệt kê bucket {self.bucket}") from exc
        return out

    def get_bytes(self, key: str) -> bytes:
        key = check_key(key)
        response = None
        try:
            response = self.client.get_object(self.bucket, key)
            return response.read()
        except S3Error as exc:
            raise self._not_found(key, exc) from exc
        finally:
            if response is not None:
                response.close()
                response.release_conn()

    def download(self, key: str, dest: Optional[Path] = None) -> Path:
        """Tải về file cục bộ để reader mở. Dùng lại bản đã tải nếu etag không đổi."""
        info = self.stat(key)
        if dest is None:
            if self.cache_dir is None:
                raise ValidationError(
                    "Chưa cấu hình thư mục tạm cho kho object.",
                    hint="Đặt cache_dir khi dựng MinioStore, hoặc truyền dest.",
                )
            safe = check_key(key).replace("/", "__")
            tag = (info.etag or "notag")[:16]
            dest = self.cache_dir / f"{tag}__{safe}"
            if dest.exists() and dest.stat().st_size == info.size:
                return dest  # đã có bản đúng etag, khỏi tải lại

        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_suffix(dest.suffix + ".part")
        try:
            self.client.fget_object(self.bucket, check_key(key), str(tmp))
            os.replace(tmp, dest)
        except S3Error as exc:
            tmp.unlink(missing_ok=True)
            raise self._not_found(key, exc) from exc
        return dest

    # ---- ghi --------------------------------------------------------------

    def put_bytes(self, key: str, data: bytes,
                  content_type: Optional[str] = None) -> ObjectInfo:
        key = check_key(key)
        if not self.writable:
            raise ValidationError(
                f"Bucket {self.bucket} là vùng chỉ đọc.",
                hint="Ghi vào lsth-work hoặc lsth-out. Bucket lsth-raw giữ file gốc "
                     "và tài khoản ứng dụng cũng bị MinIO chặn ghi vào đó.",
            )
        import io as _io

        try:
            result = self.client.put_object(
                self.bucket, key, _io.BytesIO(data), length=len(data),
                content_type=content_type or content_type_for(key))
        except S3Error as exc:
            raise self._wrap(exc, f"ghi {self.uri(key)}") from exc
        return ObjectInfo(key=key, size=len(data),
                          etag=(getattr(result, "etag", "") or "").strip('"'),
                          bucket=self.bucket)

    # ---- lỗi --------------------------------------------------------------

    def _not_found(self, key: str, exc: Exception) -> LsthError:
        code = getattr(exc, "code", "")
        if code in {"NoSuchKey", "NoSuchObject"}:
            return NotFoundError(
                f"Không có object {self.uri(key)}.",
                hint=f"Xem danh sách bằng file_list, hoặc tải file lên bucket "
                     f"{self.bucket} qua console MinIO (http://localhost:9001).",
            )
        if code == "NoSuchBucket":
            return NotFoundError(
                f"Chưa có bucket {self.bucket}.",
                hint="Chạy: docker compose -f docker/docker-compose.yml up -d",
            )
        return self._wrap(exc, f"đọc {self.uri(key)}")

    def _wrap(self, exc: Exception, what: str) -> LsthError:
        code = getattr(exc, "code", "")
        if code in {"AccessDenied", "InvalidAccessKeyId", "SignatureDoesNotMatch"}:
            return StorageUnavailableError(
                f"Bị từ chối khi {what}.",
                hint="Kiểm tra LSTH_S3_ACCESS_KEY/SECRET_KEY, và nhớ tài khoản ứng "
                     "dụng cố ý không có quyền ghi vào lsth-raw hay xoá object.",
                context={"s3_code": code},
            )
        return StorageUnavailableError(
            f"Lỗi kho object khi {what}: {exc}",
            hint=f"Kiểm tra MinIO còn chạy không: curl http://{self.endpoint}/minio/health/live",
            context={"s3_code": code},
        )
