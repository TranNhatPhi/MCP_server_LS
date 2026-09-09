"""Nơi chứa file: đĩa cục bộ hoặc MinIO.

Chọn bằng biến môi trường LSTH_STORAGE = local | minio (mặc định local).
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

from ...core.config import Settings, get_settings
from ...core.errors import NotFoundError
from .base import ObjectInfo, ObjectStore, check_key, content_type_for
from .minio_store import MinioStore, StorageUnavailableError

#: Vùng dữ liệu -> bucket. Tên bucket khớp với docker/init/setup.sh.
BUCKETS: Dict[str, str] = {
    "raw": "lsth-raw",
    "templates": "lsth-templates",
    "identity": "lsth-identity",
    "work": "lsth-work",
    "out": "lsth-out",
    "archive": "lsth-archive",
}

#: Vùng nào ghi được. raw/templates/identity chỉ đọc — MinIO cũng chặn ở tầng chính sách.
WRITABLE_AREAS = ("work", "out", "archive")

#: Thứ tự tìm khi người dùng chỉ đưa tên file mà không nói vùng nào.
SEARCH_ORDER = ("raw", "templates", "identity", "work", "out", "archive")


def storage_mode(settings: Optional[Settings] = None) -> str:
    """Chế độ lưu trữ của CẤU HÌNH ĐƯỢC TRUYỀN VÀO, không phải của biến môi trường.

    Biến LSTH_STORAGE được nạp một lần khi dựng Settings (core.config), nên một
    Settings dựng riêng — trong kiểm thử chẳng hạn — giữ đúng chế độ của nó.
    """
    cfg = settings or get_settings()
    return str(getattr(cfg, "storage", "local")).lower()


def using_minio(settings: Optional[Settings] = None) -> bool:
    return storage_mode(settings) == "minio"


_cache: Dict[str, MinioStore] = {}


def get_store(area: str, settings: Optional[Settings] = None) -> MinioStore:
    """Trả về kho object cho một vùng dữ liệu. Có nhớ để khỏi nối lại mỗi lần."""
    cfg = settings or get_settings()
    if area not in BUCKETS:
        raise NotFoundError(
            f"Không có vùng dữ liệu '{area}'.",
            hint=f"Các vùng đang có: {', '.join(BUCKETS)}.",
        )
    if area not in _cache:
        cache_dir = Path(cfg.data_dir) / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        _cache[area] = MinioStore.connect(
            BUCKETS[area], writable=area in WRITABLE_AREAS, cache_dir=cache_dir)
    return _cache[area]


def reset_stores() -> None:
    """Quên các kết nối đã nhớ — dùng sau khi đổi cấu hình hoặc trong kiểm thử."""
    _cache.clear()


def parse_uri(value: str) -> Optional[tuple]:
    """`s3://lsth-raw/BOM.xlsx` -> ("raw", "BOM.xlsx"). Không phải URI thì trả None."""
    text = str(value)
    if not text.startswith("s3://"):
        return None
    rest = text[5:]
    bucket, _, key = rest.partition("/")
    for area, name in BUCKETS.items():
        if name == bucket:
            return area, check_key(key)
    raise NotFoundError(
        f"Bucket không thuộc hệ thống LSTH: {bucket}",
        hint=f"Các bucket đang dùng: {', '.join(BUCKETS.values())}.",
    )


def locate(key_or_uri: str, settings: Optional[Settings] = None) -> tuple:
    """Tìm object theo tên, trả về (store, key).

    Đưa `s3://bucket/key` thì đi thẳng. Đưa mỗi tên file thì dò lần lượt các vùng
    theo SEARCH_ORDER — tìm thấy ở đâu dùng ở đó, không thấy thì báo rõ đã tìm đâu.
    """
    parsed = parse_uri(key_or_uri)
    if parsed:
        area, key = parsed
        return get_store(area, settings), key

    key = check_key(key_or_uri)
    for area in SEARCH_ORDER:
        store = get_store(area, settings)
        if store.exists(key):
            return store, key

    raise NotFoundError(
        f"Không tìm thấy '{key}' trong kho object.",
        hint=f"Đã tìm ở: {', '.join(BUCKETS[a] for a in SEARCH_ORDER)}. "
             "Dùng file_list để xem có gì, hoặc tải file lên qua console MinIO "
             "(http://localhost:9001).",
    )


__all__ = [
    "ObjectStore", "ObjectInfo", "MinioStore", "StorageUnavailableError",
    "BUCKETS", "WRITABLE_AREAS", "SEARCH_ORDER",
    "get_store", "locate", "parse_uri", "reset_stores",
    "storage_mode", "using_minio", "check_key", "content_type_for",
]
