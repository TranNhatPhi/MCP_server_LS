"""Ghi file Excel: xuất bảng mới, hoặc điền vào file khuôn đã duyệt (F4).

Điền vào khuôn là cách dùng chính. Tài liệu v2.0 nói rõ: "Máy chỉ dựng được bản
nháp nếu có khuôn. Không có khuôn chuẩn thì mỗi lần sinh ra một kiểu."

Mọi file sinh ra đều là BẢN NHÁP: có ô đánh dấu ở đầu file, và các ô máy không
tra được nguồn được tô màu để merchandiser nhìn ra ngay chỗ cần mình (nguyên tắc 4).
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

from ...core.errors import UnsupportedFormatError
from ..base import WriteResult
from .safe import SafeWriter

try:
    from openpyxl import Workbook, load_workbook
    from openpyxl.styles import Font, PatternFill
except ImportError:  # pragma: no cover
    Workbook = None  # type: ignore[assignment]
    load_workbook = None  # type: ignore[assignment]

#: Vàng nhạt cho ô máy không tra được nguồn; xám cho dòng chú thích bản nháp.
FILL_NEEDS_HUMAN = "FFF2CC"
FILL_DRAFT_BANNER = "D9D9D9"

DRAFT_BANNER = "BẢN NHÁP DO MÁY DỰNG — người soát phải kiểm trước khi dùng"


def _require() -> None:
    if Workbook is None:
        raise UnsupportedFormatError(
            "Chưa cài openpyxl nên không ghi được file Excel.",
            hint="Chạy: pip install openpyxl",
        )


def write_rows(
    writer: SafeWriter,
    path: Any,
    rows: Sequence[Dict[str, Any]],
    *,
    columns: Optional[Sequence[str]] = None,
    sheet_name: str = "Data",
    draft_banner: bool = True,
    needs_human: Optional[Dict[int, Sequence[str]]] = None,
    what: str = "",
) -> WriteResult:
    """Xuất danh sách dict ra một sheet.

    `needs_human`: {chỉ số dòng (0-based) -> danh sách tên cột} — các ô đó được tô
    vàng để người soát biết máy không tra được nguồn cho chúng.
    """
    _require()
    headers = list(columns) if columns else _collect_headers(rows)
    marks = needs_human or {}

    def payload(tmp: Path) -> None:
        workbook = Workbook()
        ws = workbook.active
        ws.title = sheet_name
        offset = 0
        if draft_banner:
            ws.cell(row=1, column=1, value=f"{DRAFT_BANNER} · {datetime.now():%Y-%m-%d %H:%M}")
            ws.cell(row=1, column=1).font = Font(bold=True)
            ws.cell(row=1, column=1).fill = PatternFill("solid", fgColor=FILL_DRAFT_BANNER)
            offset = 1

        for col, header in enumerate(headers, start=1):
            cell = ws.cell(row=offset + 1, column=col, value=header)
            cell.font = Font(bold=True)

        for index, row in enumerate(rows):
            flagged = set(marks.get(index, ()))
            for col, header in enumerate(headers, start=1):
                cell = ws.cell(row=offset + 2 + index, column=col, value=row.get(header))
                if header in flagged:
                    cell.fill = PatternFill("solid", fgColor=FILL_NEEDS_HUMAN)

        _autosize(ws, headers)
        workbook.save(tmp)

    return writer.write_with(path, payload, what=what or f"xuất {len(rows)} dòng", rows=len(rows))


def fill_template(
    writer: SafeWriter,
    template_path: Any,
    dest_path: Any,
    values: Dict[str, Any],
    *,
    sheet: Optional[str] = None,
    what: str = "",
) -> WriteResult:
    """Điền vào file khuôn đã duyệt theo bản đồ {"B4": giá trị, "Sheet1!C7": giá trị}.

    Giữ nguyên mọi định dạng, công thức và ô khác của khuôn — chỉ đặt giá trị vào
    đúng các ô được chỉ định.
    """
    _require()
    template = Path(str(template_path))

    def payload(tmp: Path) -> None:
        workbook = load_workbook(template)
        for address, value in values.items():
            sheet_name, _, cell_ref = address.rpartition("!")
            ws = workbook[sheet_name] if sheet_name else (
                workbook[sheet] if sheet else workbook.active)
            ws[cell_ref] = value
        workbook.save(tmp)

    writer_result = writer.write_with(
        dest_path, payload, what=what or f"điền khuôn {template.name}", rows=len(values))
    if writer.trace:
        writer.trace.read(template)
    return writer_result


def _collect_headers(rows: Iterable[Dict[str, Any]]) -> List[str]:
    headers: List[str] = []
    for row in rows:
        for key in row:
            if key not in headers:
                headers.append(key)
    return headers


def _autosize(ws: Any, headers: Sequence[str], max_width: int = 45) -> None:
    for index, header in enumerate(headers, start=1):
        width = min(max(len(str(header)) + 2, 10), max_width)
        ws.column_dimensions[ws.cell(row=1, column=index).column_letter].width = width
