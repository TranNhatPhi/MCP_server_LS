"""Ghi JSON, JSONL và CSV qua SafeWriter.

JSON là định dạng trao đổi giữa các server (hợp đồng dữ liệu F2), JSONL dùng cho
bộ đánh giá F5 và các bản ghi nối thêm, CSV dùng khi cần mở nhanh bằng Excel.
"""
from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

from ..base import WriteResult
from .safe import SafeWriter


def write_json(writer: SafeWriter, path: Any, data: Any, *, indent: int = 2,
               what: str = "") -> WriteResult:
    text = json.dumps(data, ensure_ascii=False, indent=indent, default=_fallback)
    return writer.write_text(path, text + "\n", what=what or "ghi JSON")


def write_jsonl(writer: SafeWriter, path: Any, rows: Sequence[Any], *,
                what: str = "") -> WriteResult:
    lines = [json.dumps(row, ensure_ascii=False, default=_fallback) for row in rows]
    result = writer.write_text(path, "\n".join(lines) + ("\n" if lines else ""),
                               what=what or f"ghi {len(rows)} dòng JSONL")
    result.rows_written = len(rows)
    return result


def append_jsonl(writer: SafeWriter, path: Any, row: Any, *, what: str = "") -> WriteResult:
    """Nối một dòng. Đọc lại rồi ghi nguyên tử — an toàn cho file vừa và nhỏ.

    File nhật ký lớn dùng core.audit.AuditLog thay cho hàm này.
    """
    target = Path(str(path))
    existing = ""
    resolved = writer._authorize(target, what)  # noqa: SLF001 - cùng gói, cố ý dùng
    if resolved.exists():
        existing = resolved.read_text(encoding="utf-8")
        if existing and not existing.endswith("\n"):
            existing += "\n"
    line = json.dumps(row, ensure_ascii=False, default=_fallback)
    return writer.write_text(path, existing + line + "\n", what=what or "nối một dòng JSONL")


def write_csv(writer: SafeWriter, path: Any, rows: Sequence[Dict[str, Any]], *,
              columns: Optional[Sequence[str]] = None, delimiter: str = ",",
              what: str = "") -> WriteResult:
    headers = list(columns) if columns else _collect_headers(rows)
    buffer = io.StringIO()
    csv_writer = csv.DictWriter(buffer, fieldnames=headers, delimiter=delimiter,
                                extrasaction="ignore", lineterminator="\n")
    csv_writer.writeheader()
    for row in rows:
        csv_writer.writerow(row)
    # utf-8-sig để Excel trên máy Windows mở ra không vỡ dấu tiếng Việt.
    result = writer.write_bytes(path, buffer.getvalue().encode("utf-8-sig"),
                                what=what or f"xuất {len(rows)} dòng CSV")
    result.rows_written = len(rows)
    return result


def _collect_headers(rows: Iterable[Dict[str, Any]]) -> List[str]:
    headers: List[str] = []
    for row in rows:
        for key in row:
            if key not in headers:
                headers.append(key)
    return headers


def _fallback(obj: Any) -> Any:
    """Cho phép ghi thẳng dataclass của core.models mà không phải chuyển tay."""
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    if isinstance(obj, Path):
        return str(obj)
    raise TypeError(f"Không chuyển được sang JSON: {type(obj).__name__}")
