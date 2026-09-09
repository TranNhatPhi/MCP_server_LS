"""Nguyên tắc 4 — "Trả lời kèm nguồn".

Mọi giá trị chạy qua hệ thống đều đi kèm một `Source` nói rõ lấy từ file nào,
sheet/trang nào, dòng nào. Trường không dẫn được nguồn thì để trống và đánh dấu
`needs_human=True` — theo tài liệu kiến trúc, đó là tín hiệu tốt chứ không phải lỗi:
nó chỉ đúng chỗ quy trình hiện tại đang dựa vào trí nhớ của một người.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Generic, List, Optional, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class Source:
    file: str
    sheet: Optional[str] = None
    row: Optional[int] = None
    column: Optional[str] = None
    page: Optional[int] = None
    note: Optional[str] = None

    def label(self) -> str:
        """Chuỗi ngắn để hiển thị cho merchandiser đối chiếu."""
        parts: List[str] = [self.file]
        if self.sheet:
            parts.append(f"sheet {self.sheet}")
        if self.page is not None:
            parts.append(f"trang {self.page}")
        if self.row is not None:
            parts.append(f"dòng {self.row}")
        if self.column:
            parts.append(f"cột {self.column}")
        if self.note:
            parts.append(self.note)
        return " · ".join(parts)

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v is not None}

    def with_(self, **kw: Any) -> "Source":
        data = dict(self.__dict__)
        data.update(kw)
        return Source(**data)


@dataclass
class Sourced(Generic[T]):
    """Một giá trị kèm nguồn của nó."""

    value: Optional[T]
    source: Optional[Source] = None
    needs_human: bool = False
    note: Optional[str] = None

    @classmethod
    def unknown(cls, note: str) -> "Sourced[T]":
        """Không tra được nguồn — để trống và đánh dấu cần người điền."""
        return cls(value=None, source=None, needs_human=True, note=note)

    @property
    def is_trusted(self) -> bool:
        return self.value is not None and self.source is not None

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {"value": self.value}
        if self.source:
            out["source"] = self.source.to_dict()
        if self.needs_human:
            out["needs_human"] = True
        if self.note:
            out["note"] = self.note
        return out


def dedupe_sources(sources: List[Source]) -> List[Dict[str, Any]]:
    """Gom nguồn trùng, giữ nguyên thứ tự xuất hiện."""
    seen: Dict[tuple, None] = {}
    out: List[Dict[str, Any]] = []
    for s in sources:
        key = (s.file, s.sheet, s.page, s.row, s.column)
        if key in seen:
            continue
        seen[key] = None
        out.append(s.to_dict())
    return out


@dataclass
class Collector:
    """Gom nguồn trong lúc một tool chạy, để trả về ở trường `sources`."""

    items: List[Source] = field(default_factory=list)

    def add(self, source: Optional[Source]) -> None:
        if source is not None:
            self.items.append(source)

    def extend(self, sources: List[Source]) -> None:
        for s in sources:
            self.add(s)

    def files(self) -> List[str]:
        out: List[str] = []
        for s in self.items:
            if s.file not in out:
                out.append(s.file)
        return out

    def as_list(self) -> List[Dict[str, Any]]:
        return dedupe_sources(self.items)
