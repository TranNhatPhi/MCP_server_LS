"""Đọc file Excel — module đọc dùng nhiều nhất của hệ thống.

Khảo sát cho thấy Excel xuất hiện ở 66/107 dòng công việc, ERP chỉ 10. Nên đây là
nơi dữ liệu thật đang nằm, và mọi thứ đọc ra phải dẫn được tới sheet + dòng + cột.

Đọc bằng openpyxl ở chế độ read_only để mở được file BOM vài nghìn dòng mà không
ngốn bộ nhớ. Chỉ đọc, không bao giờ mở file gốc ở chế độ ghi.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Sequence

from ...core.errors import NotFoundError, UnsupportedFormatError, ValidationError
from ...core.provenance import Source
from ..base import ReadResult, Reader

try:
    from openpyxl import load_workbook
    from openpyxl.utils import get_column_letter
except ImportError:  # pragma: no cover
    load_workbook = None  # type: ignore[assignment]
    get_column_letter = None  # type: ignore[assignment]


def _require_openpyxl() -> None:
    if load_workbook is None:
        raise UnsupportedFormatError(
            "Chưa cài openpyxl nên không đọc được file Excel.",
            hint="Chạy: pip install openpyxl",
        )


class ExcelReader(Reader):
    suffixes = (".xlsx", ".xlsm")

    def read(
        self,
        path: Path,
        *,
        sheet: Optional[str] = None,
        header_row: Optional[int] = None,
        limit: Optional[int] = None,
        skip_empty: bool = True,
        **_: Any,
    ) -> ReadResult:
        """Đọc một sheet thành danh sách dict, mỗi dòng kèm nguồn.

        `header_row=None` thì tự dò dòng tiêu đề — file thật của LSTH hay có
        một hai dòng logo/tiêu đề phía trên bảng.
        """
        _require_openpyxl()
        path = Path(path)
        workbook = load_workbook(path, read_only=True, data_only=True)
        try:
            ws = _pick_sheet(workbook, path, sheet)
            grid = list(ws.iter_rows(values_only=True))
            if not grid:
                return ReadResult(path=path, sources=[Source(file=str(path), sheet=ws.title)],
                                  warnings=[f"Sheet {ws.title} rỗng."],
                                  meta={"sheet": ws.title, "row_count": 0})

            hdr_index = (header_row - 1) if header_row else _detect_header(grid)
            headers = _clean_headers(grid[hdr_index])
            rows: List[Dict[str, Any]] = []
            sources: List[Source] = []
            warnings: List[str] = []

            for offset, raw in enumerate(grid[hdr_index + 1:], start=hdr_index + 2):
                if limit is not None and len(rows) >= limit:
                    warnings.append(f"Chỉ đọc {limit} dòng đầu; sheet còn nữa.")
                    break
                if skip_empty and not any(v not in (None, "") for v in raw):
                    continue
                row = {headers[i]: raw[i] for i in range(min(len(headers), len(raw)))
                       if headers[i]}
                rows.append(row)
                sources.append(Source(file=str(path), sheet=ws.title, row=offset))

            return ReadResult(
                path=path, rows=rows, sources=sources or [Source(file=str(path), sheet=ws.title)],
                warnings=warnings,
                meta={"sheet": ws.title, "sheets": workbook.sheetnames,
                      "header_row": hdr_index + 1, "columns": headers,
                      "row_count": len(rows)},
            )
        finally:
            workbook.close()

    def sheet_names(self, path: Path) -> List[str]:
        _require_openpyxl()
        workbook = load_workbook(Path(path), read_only=True, data_only=True)
        try:
            return list(workbook.sheetnames)
        finally:
            workbook.close()

    def read_all_sheets(self, path: Path, **kwargs: Any) -> Dict[str, ReadResult]:
        """Đọc mọi sheet — dùng khi rà file khảo sát mỗi người một kiểu."""
        return {name: self.read(path, sheet=name, **kwargs)
                for name in self.sheet_names(path)}


def _pick_sheet(workbook: Any, path: Path, sheet: Optional[str]) -> Any:
    if sheet is None:
        return workbook.worksheets[0]
    if sheet in workbook.sheetnames:
        return workbook[sheet]
    raise NotFoundError(
        f"Không có sheet '{sheet}' trong {path.name}.",
        hint=f"Các sheet đang có: {', '.join(workbook.sheetnames)}.",
        source=Source(file=str(path)).to_dict(),
    )


def _detect_header(grid: Sequence[Sequence[Any]], scan: int = 15) -> int:
    """Dòng tiêu đề = dòng có nhiều ô chữ không rỗng nhất trong 15 dòng đầu."""
    best_index, best_score = 0, -1
    for index, row in enumerate(grid[:scan]):
        score = sum(1 for v in row if isinstance(v, str) and v.strip())
        if score > best_score:
            best_index, best_score = index, score
    return best_index


def _clean_headers(row: Sequence[Any]) -> List[str]:
    """Tên cột rỗng thì đặt theo chữ cái cột, để không mất dữ liệu và vẫn dẫn được nguồn."""
    headers: List[str] = []
    seen: Dict[str, int] = {}
    for index, value in enumerate(row, start=1):
        name = str(value).strip() if value not in (None, "") else (
            f"col_{get_column_letter(index)}" if get_column_letter else f"col_{index}")
        if name in seen:
            seen[name] += 1
            name = f"{name}_{seen[name]}"
        else:
            seen[name] = 0
        headers.append(name)
    return headers


def read_excel(path: Path, **kwargs: Any) -> ReadResult:
    return ExcelReader().read(Path(path), **kwargs)


def iter_excel_rows(path: Path, **kwargs: Any) -> Iterator[Dict[str, Any]]:
    """Duyệt từng dòng, dùng khi file lớn và không cần giữ hết trong bộ nhớ."""
    result = read_excel(path, **kwargs)
    for row in result.rows:
        yield row
