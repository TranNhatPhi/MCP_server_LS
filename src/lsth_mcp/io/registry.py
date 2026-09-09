"""Bảng phân phối: đưa một đường dẫn, tự chọn đúng module đọc.

Đây là điểm vào của mọi tool đọc file. Nó cũng là nơi áp hai ràng buộc chung:
đường dẫn phải nằm trong vùng cho phép, và mỗi lần đọc đều ghi vào sổ tay lệnh gọi.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.audit import CallTrace
from ..core.config import Settings, get_settings
from ..core.errors import UnsupportedFormatError
from ..core.paths import resolve_within
from ..core.provenance import Source
from .base import ReadResult, Reader
from .readers.excel import ExcelReader
from .readers.jsonio import JsonReader
from .readers.pdf import PdfDocReader
from .readers.tabular import CsvReader
from .readers.text import DocxReader, TextReader

#: Thứ tự có ý nghĩa: reader đứng trước được ưu tiên khi trùng đuôi (.txt).
READERS: List[Reader] = [
    ExcelReader(), PdfDocReader(), JsonReader(), CsvReader(), DocxReader(), TextReader(),
]

SUPPORTED = sorted({s for r in READERS for s in r.suffixes})


def reader_for(path: Path) -> Reader:
    for reader in READERS:
        if reader.can_read(path):
            return reader
    raise UnsupportedFormatError(
        f"Chưa đọc được định dạng {path.suffix or '(không đuôi)'}.",
        hint=f"Định dạng đang hỗ trợ: {', '.join(SUPPORTED)}. "
             "Xuất file sang một trong các định dạng đó rồi chạy lại.",
        context={"file": str(path)},
    )


def read_any(
    path: Any,
    *,
    settings: Optional[Settings] = None,
    trace: Optional[CallTrace] = None,
    **kwargs: Any,
) -> ReadResult:
    """Đọc bất kỳ file nào được hỗ trợ, dù nằm trên đĩa hay trong MinIO."""
    cfg = settings or get_settings()
    from .storage import locate, using_minio

    if using_minio(cfg) or str(path).startswith("s3://"):
        store, key = locate(str(path), cfg)
        local = store.download(key)
        result = reader_for(local).read(local, **kwargs)
        # Nguồn phải trỏ về object trong kho, không phải file tạm trong cache.
        uri = store.uri(key)
        result.sources = [s.with_(file=uri) for s in result.sources] or [Source(file=uri)]
        result.meta["uri"] = uri
        result.meta["bucket"] = store.bucket
        if trace:
            trace.read(uri)
        return result

    target = resolve_within(path, cfg.read_roots, must_exist=True)
    result = reader_for(target).read(target, **kwargs)
    if trace:
        trace.read(target)
    return result


def list_files(
    pattern: str = "**/*",
    *,
    root: Optional[Any] = None,
    settings: Optional[Settings] = None,
    limit: int = 200,
) -> List[Dict[str, Any]]:
    """Liệt kê file trong vùng cho phép — bước đầu của mọi việc tra cứu ổ chung."""
    cfg = settings or get_settings()
    from .storage import BUCKETS, SEARCH_ORDER, get_store, using_minio

    if using_minio(cfg):
        out: List[Dict[str, Any]] = []
        areas = [root] if root and str(root) in BUCKETS else SEARCH_ORDER
        for area in areas:
            store = get_store(str(area), cfg)
            for obj in store.list(limit=limit - len(out)):
                out.append({
                    "path": store.uri(obj.key), "name": obj.name,
                    "area": area, "bucket": store.bucket, "suffix": obj.suffix,
                    "size_bytes": obj.size,
                    "modified": int(obj.last_modified.timestamp()) if obj.last_modified else None,
                    "readable": any(r.can_read(Path(obj.key)) for r in READERS),
                    "writable_area": store.writable,
                })
                if len(out) >= limit:
                    return out
        return out

    roots = [resolve_within(root, cfg.read_roots)] if root else cfg.read_roots
    out = []
    for base in roots:
        if not Path(base).exists():
            continue
        for item in sorted(Path(base).glob(pattern)):
            if not item.is_file() or item.name.startswith("."):
                continue
            stat = item.stat()
            out.append({
                "path": str(item),
                "name": item.name,
                "suffix": item.suffix.lower(),
                "size_bytes": stat.st_size,
                "modified": int(stat.st_mtime),
                "readable": any(r.can_read(item) for r in READERS),
            })
            if len(out) >= limit:
                return out
    return out
