"""Khung trả về chung cho mọi tool: {ok, data, sources[], warnings[], error}.

Chuẩn kỹ thuật chương 15 — mọi tool trả về cùng một khung, `sources` là bắt buộc.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional

from .errors import LsthError
from .provenance import Source, dedupe_sources


@dataclass
class Envelope:
    ok: bool
    data: Any = None
    sources: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    error: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "data": self.data,
            "sources": self.sources,
            "warnings": self.warnings,
            "error": self.error,
        }


def _norm_sources(sources: Optional[Iterable[Any]]) -> List[Dict[str, Any]]:
    if not sources:
        return []
    items = list(sources)
    if items and isinstance(items[0], Source):
        return dedupe_sources(items)  # type: ignore[arg-type]
    return [s for s in items if isinstance(s, dict)]


def ok(
    data: Any = None,
    sources: Optional[Iterable[Any]] = None,
    warnings: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    return Envelope(
        ok=True,
        data=data,
        sources=_norm_sources(sources),
        warnings=list(warnings or []),
    ).to_dict()


def fail(error: Exception, warnings: Optional[Iterable[str]] = None) -> Dict[str, Any]:
    if isinstance(error, LsthError):
        payload = error.to_dict()
    else:
        payload = {
            "code": "unexpected_error",
            "message": str(error) or error.__class__.__name__,
            "hint": "Lỗi ngoài dự kiến — xem nhật ký ở data/audit và báo người vận hành.",
        }
    return Envelope(ok=False, error=payload, warnings=list(warnings or [])).to_dict()
