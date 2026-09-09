"""S1 · lsth-techpack — bóc tech pack PDF 48–86 trang và BOM xlsx ra JSON chuẩn.

Vòng 1. Chỉ đọc file, không chạm ERP, nên dựng được ngay trên tech pack và BOM
đang có trong thư mục. Nuôi dữ liệu cho mọi server khác.

Tiêu chí nghiệm thu (chương 14 v1.0): bóc đúng ≥ 95% trường bắt buộc trên 5 tech
pack, và 0 trường bịa ra. Vế thứ hai quan trọng hơn vế thứ nhất.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from ...core.audit import CallTrace
from ...core.envelope import ok
from ...core.errors import NotFoundError, ValidationError
from ...core.models import BomLine, Color, Style
from ...core.provenance import Collector, Source
from ...io.readers.pdf import find_in_pdf
from ...io.registry import read_any
from ..base import BaseServer, ServerSpec

SPEC = ServerSpec(
    code="S1", module="s1_techpack", name="lsth-techpack",
    purpose="Bóc tech pack PDF và BOM xlsx ra JSON chuẩn",
    resource="techpack", group="Server v1.0", priority="Rất cao",
    difficulty="Thấp", round=1,
    depends_on=["F2", "F4"], blocked_by=[],
    accepted_by=["Chị Thương", "Chị Quỳnh"],
    tools=["techpack_parse", "bom_extract", "spec_lookup", "diff_check"],
)

#: Mẫu mã hàng thật của LSTH: S2749189 (Garan), 66P866 (Haddad).
STYLE_PATTERN = r"\b([A-Z]{0,2}\d{2}[A-Z]?\d{3,6})\b"
SEASON_PATTERN = r"\b((?:SS|FW|S|F)\d{2})\b"


class TechpackServer(BaseServer):
    spec = SPEC

    # ---- techpack_parse ---------------------------------------------------------

    def techpack_parse(self, file: str, max_pages: Optional[int] = None) -> Dict[str, Any]:
        """PDF tech pack -> thực thể Style, mỗi trường kèm số trang bóc ra được.

        Trường nào không tìm thấy thì để trống và liệt kê ở `missing_fields` —
        không suy đoán từ tên file (nguyên tắc 5).
        """
        def handler(trace: CallTrace) -> Dict[str, Any]:
            result = read_any(file, settings=self.settings, trace=trace,
                              max_pages=max_pages)
            collector = Collector()
            collector.extend(result.sources[:1])

            style_hits = find_in_pdf(result, STYLE_PATTERN)
            season_hits = find_in_pdf(result, SEASON_PATTERN)
            missing: List[str] = []

            if not style_hits:
                raise NotFoundError(
                    f"Không tìm thấy mã hàng trong {Path(file).name}.",
                    hint="Kiểm tra xem PDF có phải bản scan không (xem cảnh báo trang ảnh), "
                         "hoặc truyền style thủ công cho các bước sau.",
                )
            style_code = style_hits[0]["match"]
            style_page = style_hits[0]["page"]
            collector.add(Source(file=str(result.path), page=style_page))

            season = season_hits[0]["match"] if season_hits else None
            if season is None:
                missing.append("season")

            style = Style(
                style=style_code,
                season=season,
                techpack_ref=Path(file).name,
                source=Source(file=str(result.path), page=style_page),
                missing_fields=missing + ["customer", "colors", "sizes"],
            )
            return ok(
                {
                    "style": style.to_dict(),
                    "page_count": result.meta.get("page_count"),
                    "image_only_pages": result.meta.get("image_only_pages"),
                    "style_candidates": sorted({h["match"] for h in style_hits})[:10],
                },
                sources=collector.items,
                warnings=result.warnings + [
                    "Bản vòng 1 mới bóc mã hàng và mùa. Màu, size và khách còn chờ bản ghi "
                    "thao tác của chị Thương và chị Quỳnh (khoảng trống G6).",
                ],
            )

        return self.call("techpack_parse", {"file": file, "max_pages": max_pages}, handler)

    # ---- bom_extract ------------------------------------------------------------

    def bom_extract(self, file: str, sheet: Optional[str] = None,
                    limit: Optional[int] = None) -> Dict[str, Any]:
        """File BOM xlsx -> danh sách BomLine chuẩn, mỗi dòng dẫn được về sheet + dòng."""
        def handler(trace: CallTrace) -> Dict[str, Any]:
            result = read_any(file, settings=self.settings, trace=trace,
                              **({"sheet": sheet} if sheet else {}),
                              **({"limit": limit} if limit else {}))
            if not result.rows:
                raise ValidationError(
                    f"Sheet {result.meta.get('sheet')} không có dòng dữ liệu nào.",
                    hint="Chọn sheet khác bằng tham số `sheet`, hoặc kiểm tra lại file nguồn.",
                )

            lines: List[BomLine] = []
            incomplete: List[Dict[str, Any]] = []
            for row, source in zip(result.rows, result.sources):
                line = BomLine.from_row(row, source=source)
                missing = line.validate()
                if missing:
                    incomplete.append({
                        "row": source.row, "missing": missing,
                        "source": source.to_dict(),
                    })
                lines.append(line)

            unmapped = sorted({k for line in lines for k in line.extra})
            warnings: List[str] = []
            if incomplete:
                warnings.append(
                    f"{len(incomplete)}/{len(lines)} dòng thiếu trường bắt buộc — "
                    "xem `incomplete_rows`, cần người điền chứ máy không đoán."
                )
            if unmapped:
                warnings.append(
                    f"{len(unmapped)} cột chưa có trong bảng alias, đang giữ nguyên ở `extra`: "
                    f"{', '.join(unmapped[:8])}. Bổ sung vào core/models.py BOM_ALIASES nếu cần dùng."
                )

            return ok(
                {
                    "lines": [line.to_dict() for line in lines],
                    "line_count": len(lines),
                    "styles": sorted({line.style for line in lines if line.style}),
                    "materials": sorted({line.material_code for line in lines if line.material_code}),
                    "incomplete_rows": incomplete[:50],
                    "unmapped_columns": unmapped,
                    "sheet": result.meta.get("sheet"),
                },
                sources=result.sources[:1] + result.sources[-1:],
                warnings=result.warnings + warnings,
            )

        return self.call("bom_extract", {"file": file, "sheet": sheet, "limit": limit}, handler)

    # ---- spec_lookup ------------------------------------------------------------

    def spec_lookup(self, file: str, style: str, size: Optional[str] = None) -> Dict[str, Any]:
        """Tra thông số đo của một mã hàng theo size, trả về kèm trang tìm thấy."""
        def handler(trace: CallTrace) -> Dict[str, Any]:
            result = read_any(file, settings=self.settings, trace=trace)
            needle = re.escape(style)
            hits = find_in_pdf(result, rf"{needle}.{{0,200}}")
            if size:
                hits = [h for h in hits if re.search(rf"\b{re.escape(size)}\b", h["match"], re.I)]
            if not hits:
                raise NotFoundError(
                    f"Không thấy thông số cho {style}" + (f" size {size}." if size else "."),
                    hint="Tech pack có thể để bảng thông số ở dạng ảnh — cần người mở xem trang "
                         f"{result.meta.get('page_count')} trang và đọc tay.",
                )
            return ok(
                {"matches": hits[:20], "match_count": len(hits)},
                sources=[Source(file=str(result.path), page=h["page"]) for h in hits[:5]],
                warnings=["Kết quả là đoạn chữ thô quanh mã hàng. Bảng thông số có cấu trúc "
                          "cần bản ghi thao tác ở vòng khảo sát bổ sung (G6)."],
            )

        return self.call("spec_lookup", {"file": file, "style": style, "size": size}, handler)

    # ---- diff_check -------------------------------------------------------------

    def diff_check(self, techpack_file: str, bom_file: str,
                   bom_sheet: Optional[str] = None) -> Dict[str, Any]:
        """So tech pack với BOM, chỉ ra mâu thuẫn. Nguyên tắc 3: báo, không tự chọn."""
        def handler(trace: CallTrace) -> Dict[str, Any]:
            pdf = read_any(techpack_file, settings=self.settings, trace=trace)
            excel = read_any(bom_file, settings=self.settings, trace=trace,
                             **({"sheet": bom_sheet} if bom_sheet else {}))
            bom_styles = {str(r.get("Style") or r.get("style") or "").strip()
                          for r in excel.rows}
            bom_styles.discard("")
            pdf_styles = {h["match"] for h in find_in_pdf(pdf, STYLE_PATTERN)}

            only_bom = sorted(bom_styles - pdf_styles)
            only_pdf = sorted(pdf_styles - bom_styles)[:20]
            return ok(
                {
                    "in_both": sorted(bom_styles & pdf_styles),
                    "only_in_bom": only_bom,
                    "only_in_techpack": only_pdf,
                    "conflict": bool(only_bom),
                },
                sources=[pdf.sources[0], excel.sources[0]] if excel.sources else pdf.sources[:1],
                warnings=(["Có mã hàng trong BOM mà tech pack không nhắc tới — cần người "
                           "xác nhận trước khi dùng BOM này."] if only_bom else []),
            )

        return self.call(
            "diff_check",
            {"techpack_file": techpack_file, "bom_file": bom_file, "bom_sheet": bom_sheet},
            handler,
        )
