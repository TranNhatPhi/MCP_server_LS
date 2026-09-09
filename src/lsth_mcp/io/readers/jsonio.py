"""Đọc JSON và JSONL.

JSONL dùng cho bộ đánh giá F5 (erp_pilot.jsonl có sẵn 36 cặp hỏi đáp) và cho
nhật ký. Dòng hỏng thì báo rõ số dòng chứ không bỏ qua im lặng (nguyên tắc 5).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from ...core.errors import ValidationError
from ...core.provenance import Source
from ..base import ReadResult, Reader


class JsonReader(Reader):
    suffixes = (".json", ".jsonl", ".ndjson")

    def read(self, path: Path, *, strict: bool = True, **_: Any) -> ReadResult:
        path = Path(path)
        text = path.read_text(encoding="utf-8")
        if path.suffix.lower() in (".jsonl", ".ndjson"):
            return _read_jsonl(path, text, strict=strict)

        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValidationError(
                f"File JSON hỏng ở dòng {exc.lineno}, cột {exc.colno}: {exc.msg}",
                hint="Mở file kiểm tra dấu phẩy/ngoặc ở vị trí trên rồi chạy lại.",
                source=Source(file=str(path), row=exc.lineno).to_dict(),
            ) from exc

        rows: List[Dict[str, Any]] = data if isinstance(data, list) and (
            not data or isinstance(data[0], dict)) else []
        return ReadResult(
            path=path, rows=rows, data=data,
            sources=[Source(file=str(path))],
            meta={"kind": "json", "row_count": len(rows)},
        )


def _read_jsonl(path: Path, text: str, *, strict: bool) -> ReadResult:
    rows: List[Dict[str, Any]] = []
    sources: List[Source] = []
    warnings: List[str] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
            sources.append(Source(file=str(path), row=lineno))
        except json.JSONDecodeError as exc:
            message = f"Dòng {lineno} không phải JSON hợp lệ: {exc.msg}"
            if strict:
                raise ValidationError(
                    message,
                    hint="Sửa dòng đó, hoặc gọi lại với strict=False để bỏ qua và xem cảnh báo.",
                    source=Source(file=str(path), row=lineno).to_dict(),
                ) from exc
            warnings.append(message)
    return ReadResult(
        path=path, rows=rows, data=rows, sources=sources or [Source(file=str(path))],
        warnings=warnings, meta={"kind": "jsonl", "row_count": len(rows)},
    )


def read_json(path: Path, **kwargs: Any) -> ReadResult:
    return JsonReader().read(Path(path), **kwargs)
