"""Đọc PDF — tech pack của khách dày 48–86 trang.

Chỉ bóc phần chữ. Không suy đoán bố cục: trang nào không có lớp chữ (bản scan)
thì báo rõ để người gọi biết phải OCR, chứ không trả về chuỗi rỗng như thể trang
đó trống (nguyên tắc 5).

Cảnh báo vùng dữ liệu: tech pack thuộc Z3, không được đẩy nội dung ra dịch vụ AI
công cộng — dùng core.zones.ZoneClassifier trước khi gửi đi đâu.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from ...core.errors import UnsupportedFormatError, ValidationError
from ...core.provenance import Source
from ..base import ReadResult, Reader

try:
    from pypdf import PdfReader as _PdfReader
except ImportError:  # pragma: no cover
    _PdfReader = None  # type: ignore[assignment]

#: Trang có ít hơn ngần này ký tự thì nhiều khả năng là ảnh scan.
_MIN_CHARS_PER_PAGE = 20


class PdfDocReader(Reader):
    suffixes = (".pdf",)

    def read(
        self,
        path: Path,
        *,
        pages: Optional[Sequence[int]] = None,
        max_pages: Optional[int] = None,
        **_: Any,
    ) -> ReadResult:
        """`pages` đánh số từ 1 để khớp với cách người dùng nói "trang 12"."""
        if _PdfReader is None:
            raise UnsupportedFormatError(
                "Chưa cài pypdf nên không đọc được PDF.",
                hint="Chạy: pip install pypdf",
            )
        path = Path(path)
        reader = _PdfReader(str(path))
        total = len(reader.pages)
        wanted = list(pages) if pages else list(range(1, total + 1))
        if max_pages:
            wanted = wanted[:max_pages]

        chunks: List[str] = []
        sources: List[Source] = []
        warnings: List[str] = []
        image_only: List[int] = []
        page_texts: Dict[int, str] = {}

        for number in wanted:
            if number < 1 or number > total:
                raise ValidationError(
                    f"Trang {number} không tồn tại (file có {total} trang).",
                    hint=f"Chọn trang trong khoảng 1–{total}.",
                    source=Source(file=str(path)).to_dict(),
                )
            text = reader.pages[number - 1].extract_text() or ""
            page_texts[number] = text
            if len(text.strip()) < _MIN_CHARS_PER_PAGE:
                image_only.append(number)
            chunks.append(text)
            sources.append(Source(file=str(path), page=number))

        if image_only:
            warnings.append(
                f"Trang {_compact(image_only)} không có lớp chữ — nhiều khả năng là ảnh scan. "
                "Cần OCR hoặc người đọc tay, không được coi là trang trống."
            )

        return ReadResult(
            path=path,
            text="\n\n".join(chunks),
            data=page_texts,
            sources=sources,
            warnings=warnings,
            meta={"page_count": total, "pages_read": wanted, "image_only_pages": image_only},
        )


def _compact(numbers: Sequence[int]) -> str:
    return ", ".join(str(n) for n in numbers[:10]) + ("…" if len(numbers) > 10 else "")


def find_in_pdf(result: ReadResult, pattern: str) -> List[Dict[str, Any]]:
    """Tìm mẫu chữ trong PDF đã đọc, trả về kèm số trang.

    Dùng cho techpack_parse: mọi giá trị bóc ra phải nói được nằm ở trang nào.
    """
    regex = re.compile(pattern, re.IGNORECASE)
    hits: List[Dict[str, Any]] = []
    for page_number, text in (result.data or {}).items():
        for match in regex.finditer(text or ""):
            hits.append({
                "match": match.group(0),
                "groups": list(match.groups()),
                "page": page_number,
                "source": Source(file=str(result.path), page=page_number).to_dict(),
            })
    return hits


def read_pdf(path: Path, **kwargs: Any) -> ReadResult:
    return PdfDocReader().read(Path(path), **kwargs)
