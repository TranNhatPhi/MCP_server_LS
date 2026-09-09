"""Đọc file bảng phẳng: CSV, TSV.

Mỗi dòng trả về kèm số dòng thật trong file để dẫn nguồn được tới từng ô.
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List, Optional

from ...core.provenance import Source
from ..base import ReadResult, Reader

#: Thử lần lượt các bảng mã hay gặp ở file xuất từ ERP và ổ chung.
ENCODINGS = ("utf-8-sig", "utf-8", "cp1258", "latin-1")


def _open_text(path: Path, encoding: Optional[str]) -> str:
    if encoding:
        return path.read_text(encoding=encoding)
    last: Exception = ValueError("không đọc được")
    for enc in ENCODINGS:
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError as exc:
            last = exc
    raise UnicodeDecodeError("lsth", b"", 0, 1, f"Không đoán được bảng mã của {path.name}") from last


class CsvReader(Reader):
    suffixes = (".csv", ".tsv", ".txt")

    def read(
        self,
        path: Path,
        *,
        encoding: Optional[str] = None,
        delimiter: Optional[str] = None,
        limit: Optional[int] = None,
        **_: Any,
    ) -> ReadResult:
        path = Path(path)
        raw = _open_text(path, encoding)
        if delimiter is None:
            delimiter = "\t" if path.suffix.lower() == ".tsv" else _sniff(raw)

        reader = csv.DictReader(raw.splitlines(), delimiter=delimiter)
        rows: List[Dict[str, Any]] = []
        sources: List[Source] = []
        warnings: List[str] = []
        for index, row in enumerate(reader, start=2):  # dòng 1 là tiêu đề
            if limit is not None and len(rows) >= limit:
                warnings.append(f"Chỉ đọc {limit} dòng đầu; file còn nữa.")
                break
            cleaned = {(k or "").strip(): v for k, v in row.items() if k is not None}
            if not any(str(v or "").strip() for v in cleaned.values()):
                continue
            rows.append(cleaned)
            sources.append(Source(file=str(path), row=index))

        return ReadResult(
            path=path,
            rows=rows,
            sources=sources or [Source(file=str(path))],
            warnings=warnings,
            meta={"delimiter": delimiter, "row_count": len(rows),
                  "columns": list(reader.fieldnames or [])},
        )


def _sniff(sample: str) -> str:
    head = "\n".join(sample.splitlines()[:5])
    try:
        return csv.Sniffer().sniff(head, delimiters=",;\t|").delimiter
    except csv.Error:
        return ","


def read_csv(path: Path, **kwargs: Any) -> ReadResult:
    return CsvReader().read(Path(path), **kwargs)
