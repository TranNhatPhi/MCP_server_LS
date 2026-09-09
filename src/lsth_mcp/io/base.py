"""Giao diện chung cho mọi module đọc/ghi.

Mọi reader trả về `ReadResult`, mọi writer trả về `WriteResult`. Cả hai đều bắt
buộc mang theo nguồn (nguyên tắc 4), nên tầng tool chỉ việc gom `sources` lại.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from ..core.provenance import Source


@dataclass
class ReadResult:
    """Kết quả một lần đọc.

    - `rows`: dữ liệu dạng bảng (excel, csv, jsonl)
    - `text`: dữ liệu dạng chữ (pdf, txt, docx)
    - `data`: dữ liệu có cấu trúc tự do (json)
    """

    path: Path
    rows: List[Dict[str, Any]] = field(default_factory=list)
    text: Optional[str] = None
    data: Any = None
    sources: List[Source] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)

    @property
    def source(self) -> Source:
        return self.sources[0] if self.sources else Source(file=str(self.path))

    def to_dict(self, *, include_rows: bool = True) -> Dict[str, Any]:
        out: Dict[str, Any] = {
            "path": str(self.path),
            "meta": self.meta,
            "warnings": self.warnings,
        }
        if include_rows and self.rows:
            out["rows"] = self.rows
        if self.text is not None:
            out["text"] = self.text
        if self.data is not None:
            out["data"] = self.data
        return out


@dataclass
class WriteResult:
    path: Path
    bytes_written: int = 0
    rows_written: int = 0
    backup_path: Optional[Path] = None
    created: bool = True
    source: Optional[Source] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": str(self.path),
            "bytes_written": self.bytes_written,
            "rows_written": self.rows_written,
            "backup_path": str(self.backup_path) if self.backup_path else None,
            "created": self.created,
            "source": self.source.to_dict() if self.source else None,
        }


class Reader:
    """Lớp cha của module đọc. Mỗi reader khai báo phần đuôi file mình nhận."""

    suffixes: Sequence[str] = ()

    def can_read(self, path: Path) -> bool:
        return path.suffix.lower() in self.suffixes

    def read(self, path: Path, **kwargs: Any) -> ReadResult:  # pragma: no cover
        raise NotImplementedError
