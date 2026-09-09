"""F3 · Bảng ánh xạ định danh.

Nối các hệ mã khác nhau: LS-style của nhà máy ↔ style của khách ↔ account ↔ thị
trường ↔ UPC ↔ mã vật tư. Với 6 nhãn khách, mỗi khách một hệ mã, đây là điều kiện
sống còn — chị Trần Sương đang mất 120 phút mỗi lần, 2 lần một tuần chỉ để tạo
LS style và cập nhật OD của khách.

Kỹ thuật thì thấp, công sức thu thập dữ liệu ban đầu mới là phần nặng. Bảng nguồn
là CSV để merchandiser sửa được bằng Excel, không cần qua kỹ thuật.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.erp import BRANDS, style_number_rule
from ..core.errors import ConflictError, NotFoundError
from ..core.provenance import Source
from ..io.readers.tabular import read_csv

#: Các hệ mã đang biết. Thêm khách mới thì thêm cột vào CSV, không sửa code.
#: `contract_no` là hệ mã thứ bảy, lộ ra từ cẩm nang ERP: với Haddad, IFG,
#: Jako và Osaka thì chính nó — không phải customer_style — đóng vai style number.
SYSTEMS = ("ls_style", "customer_style", "contract_no", "customer",
           "account", "market", "upc", "material_code")


@dataclass
class IdentityRecord:
    values: Dict[str, str]
    source: Optional[Source] = None

    def get(self, system: str) -> Optional[str]:
        return self.values.get(system) or None


@dataclass
class IdentityMap:
    records: List[IdentityRecord] = field(default_factory=list)
    path: Optional[Path] = None

    @classmethod
    def load(cls, path: Any) -> "IdentityMap":
        path = Path(path)
        if not path.exists():
            raise NotFoundError(
                f"Chưa có bảng ánh xạ định danh: {path}",
                hint="Tạo từ data/identity/identity_map.example.csv. "
                     "Đây là thành phần F3 — cần merchandiser cung cấp dữ liệu gốc (khoảng trống G9).",
            )
        result = read_csv(path)
        records = [
            IdentityRecord(
                values={k.strip(): str(v).strip() for k, v in row.items() if v not in (None, "")},
                source=src,
            )
            for row, src in zip(result.rows, result.sources)
        ]
        return cls(records=records, path=path)

    def resolve(
        self,
        value: str,
        *,
        from_system: str,
        to_system: str,
        market: Optional[str] = None,
        customer: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Đổi một mã sang hệ mã khác.

        Nhiều kết quả khác nhau -> ném ConflictError. Nguyên tắc 3: server báo mâu
        thuẫn chứ không tự chọn một trong hai.
        """
        needle = str(value).strip().casefold()
        hits = [
            r for r in self.records
            if (r.get(from_system) or "").casefold() == needle
            and (market is None or (r.get("market") or "").casefold() == market.casefold())
            and (customer is None or (r.get("customer") or "").casefold() == customer.casefold())
        ]
        if not hits:
            raise NotFoundError(
                f"Không tra được {from_system}={value} sang {to_system}.",
                hint="Bổ sung dòng này vào bảng ánh xạ định danh (data/identity), "
                     "hoặc kiểm tra lại thị trường/khách đã truyền đúng chưa.",
                context={"from": from_system, "to": to_system, "value": value},
            )

        answers = {r.get(to_system) for r in hits if r.get(to_system)}
        if not answers:
            raise NotFoundError(
                f"Có dòng khớp {from_system}={value} nhưng cột {to_system} còn trống.",
                hint=f"Điền cột {to_system} cho dòng đó trong bảng ánh xạ.",
                source=hits[0].source.to_dict() if hits[0].source else None,
            )
        if len(answers) > 1:
            raise ConflictError(
                f"{from_system}={value} cho ra {len(answers)} giá trị {to_system} khác nhau.",
                candidates=sorted(answers),
                hint="Hai nguồn đang nói khác nhau — cần merchandiser chốt giá trị đúng "
                     "rồi sửa bảng ánh xạ. Máy không tự chọn (nguyên tắc 3).",
            )

        hit = next(r for r in hits if r.get(to_system))
        return {
            "value": hit.get(to_system),
            "source": hit.source.to_dict() if hit.source else None,
            "record": hit.values,
        }

    def lookup_all(self, value: str, *, from_system: str) -> List[Dict[str, Any]]:
        needle = str(value).strip().casefold()
        return [
            {"record": r.values, "source": r.source.to_dict() if r.source else None}
            for r in self.records
            if (r.get(from_system) or "").casefold() == needle
        ]

    def coverage(self) -> Dict[str, Any]:
        """Bao nhiêu phần trăm ô đã điền cho từng hệ mã — dùng để theo dõi tiến độ lấp F3."""
        total = len(self.records) or 1
        return {
            "record_count": len(self.records),
            "filled_pct": {
                system: round(100.0 * sum(1 for r in self.records if r.get(system)) / total, 1)
                for system in SYSTEMS
            },
        }


def erp_style_number(brand: str, *, customer_style: str = "",
                     contract_no: str = "") -> Dict[str, Any]:
    """Trường nào đóng vai style number khi import BOM vào ERP, theo nhãn khách.

    Quy tắc lấy từ cẩm nang ERP nội bộ (SO-BOM-PURCHASE), không phải suy đoán:
    Haddad, IFG, Jako, Osaka dùng Contract No; các nhãn còn lại dùng customer style.

    Sai chỗ này thì BOM import vào nhầm mã hàng, nên hàm ném lỗi khi trường cần
    dùng đang trống thay vì lặng lẽ lấy trường kia (nguyên tắc 5).
    """
    field, column_b = style_number_rule(brand)
    value = contract_no if field == "contract_no" else customer_style
    if not (value or "").strip():
        raise NotFoundError(
            f"Nhãn {brand} dùng {field} làm style number nhưng trường đó đang trống.",
            hint=f"Điền {field} từ Sales Order. Cột B trong file BOM phải là {column_b}.",
            context={"brand": brand, "rule_field": field,
                     "known_brands": sorted(BRANDS)},
        )
    return {
        "style_number": value.strip(),
        "rule_field": field,
        "bom_column_b": column_b,
        "source": {"file": "USE GUIDE ERP VERSION WEB SO-BOM-PURCHASE 20260331.docx",
                   "note": "mục Import BOM, phần Chú ý"},
    }
