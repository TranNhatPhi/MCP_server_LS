"""F2 · Mô hình dữ liệu chuẩn — năm thực thể dùng chung cho mọi server.

Tên trường lấy đúng theo tên cột đang có trong file BOM thật của LSTH để không
phải dịch qua lại. BOM của Garan và Haddad đã dùng chung đúng bộ cột, nên một bộ
alias là đủ cho cả hai khách; khách mới thì bổ sung vào ALIASES chứ không sửa model.
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from .errors import ValidationError
from .provenance import Source


def normalize_header(name: Any) -> str:
    """"Color Garment Code" / "COLOR_GARMENT_CODE " -> "color_garment_code"."""
    text = str(name or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


#: Tên cột thật trong file -> tên trường chuẩn. Khoá đã chuẩn hoá bằng normalize_header.
BOM_ALIASES: Dict[str, str] = {
    "item_no": "item_no", "item": "item_no", "no": "item_no", "stt": "item_no",
    "style": "style", "style_no": "style", "ma_hang": "style",
    "color_garment_code": "color_garment_code", "garment_color_code": "color_garment_code",
    "color_garment_name": "color_garment_name", "garment_color_name": "color_garment_name",
    "material_code": "material_code", "mat_code": "material_code", "ma_vat_tu": "material_code",
    "description": "description", "desc": "description", "mo_ta": "description",
    "color_code": "color_code", "color_name": "color_name",
    "garment_size": "garment_size", "size": "garment_size",
    "consumption": "consumption", "cons": "consumption", "dinh_muc": "consumption",
    "unit_bom": "unit_bom", "unit": "unit_bom", "uom": "unit_bom", "dvt": "unit_bom",
    "position": "position", "vi_tri": "position",
    "material_class": "material_class", "class": "material_class",
    "price": "price", "unit_price": "price", "gia": "price",
    "currency": "currency", "vendor_code": "vendor_code", "vendor": "vendor_code",
    "supplier": "vendor_code", "ncc": "vendor_code",
    "lead_time": "lead_time", "leadtime": "lead_time",
    "wastage_pct": "wastage_pct", "wastage": "wastage_pct", "hao_hut": "wastage_pct",
    "less_pct": "less_pct", "less": "less_pct",
    "over_pct": "over_pct", "over": "over_pct",
    "fabric_weight_gsm": "fabric_weight_gsm", "gsm": "fabric_weight_gsm",
    "fabric_width_inch": "fabric_width_inch", "width": "fabric_width_inch",
}


def _to_float(value: Any, field_name: str, source: Optional[Source]) -> Optional[float]:
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "")
    text = text.rstrip("%")
    try:
        return float(text)
    except ValueError:
        # Nguyên tắc 5: gặp dữ liệu lạ thì dừng, không đoán về 0.
        raise ValidationError(
            f"Trường '{field_name}' không phải số: {value!r}",
            hint="Sửa ô này trong file nguồn rồi chạy lại, hoặc báo người giữ file.",
            source=source.to_dict() if source else None,
        )


@dataclass
class Color:
    code: str
    name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Style:
    """5.1 — mã hàng."""

    style: str
    customer: Optional[str] = None
    season: Optional[str] = None
    colors: List[Color] = field(default_factory=list)
    sizes: List[str] = field(default_factory=list)
    techpack_ref: Optional[str] = None
    source: Optional[Source] = None
    missing_fields: List[str] = field(default_factory=list)

    REQUIRED = ("style",)

    def validate(self) -> None:
        missing = [f for f in self.REQUIRED if not getattr(self, f)]
        if missing:
            raise ValidationError(
                f"Style thiếu trường bắt buộc: {', '.join(missing)}",
                hint="Kiểm tra lại trang bìa tech pack; nếu tech pack không ghi thì hỏi merchandiser.",
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "style": self.style,
            "customer": self.customer,
            "season": self.season,
            "colors": [c.to_dict() for c in self.colors],
            "sizes": self.sizes,
            "techpack_ref": self.techpack_ref,
            "source": self.source.to_dict() if self.source else None,
            "missing_fields": self.missing_fields,
        }


@dataclass
class BomLine:
    """5.2 — một dòng định mức. Giữ đúng bộ cột hiện có của ERP."""

    item_no: Optional[str] = None
    style: Optional[str] = None
    color_garment_code: Optional[str] = None
    color_garment_name: Optional[str] = None
    material_code: Optional[str] = None
    description: Optional[str] = None
    color_code: Optional[str] = None
    color_name: Optional[str] = None
    garment_size: Optional[str] = None
    consumption: Optional[float] = None
    unit_bom: Optional[str] = None
    position: Optional[str] = None
    material_class: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    vendor_code: Optional[str] = None
    lead_time: Optional[float] = None
    wastage_pct: Optional[float] = None
    less_pct: Optional[float] = None
    over_pct: Optional[float] = None
    fabric_weight_gsm: Optional[float] = None
    fabric_width_inch: Optional[float] = None
    extra: Dict[str, Any] = field(default_factory=dict)
    source: Optional[Source] = None

    NUMERIC = ("consumption", "price", "lead_time", "wastage_pct", "less_pct",
               "over_pct", "fabric_weight_gsm", "fabric_width_inch")
    REQUIRED = ("style", "material_code", "consumption")

    @classmethod
    def from_row(cls, row: Dict[str, Any], source: Optional[Source] = None) -> "BomLine":
        """Dựng từ một dòng Excel/CSV. Cột không nhận ra thì giữ nguyên trong `extra`."""
        mapped: Dict[str, Any] = {}
        extra: Dict[str, Any] = {}
        known = {f for f in cls.__dataclass_fields__ if f not in ("extra", "source")}
        for raw_key, value in row.items():
            key = BOM_ALIASES.get(normalize_header(raw_key))
            if key and key in known:
                mapped[key] = value
            elif str(raw_key).strip():
                extra[str(raw_key).strip()] = value

        for key in cls.NUMERIC:
            if key in mapped:
                mapped[key] = _to_float(mapped[key], key, source)
        for key, value in list(mapped.items()):
            if key not in cls.NUMERIC and value is not None:
                mapped[key] = str(value).strip() or None

        return cls(**mapped, extra=extra, source=source)

    def validate(self) -> List[str]:
        """Trả về danh sách trường thiếu thay vì ném lỗi — người gọi quyết định xử lý."""
        return [f for f in self.REQUIRED if getattr(self, f) in (None, "")]

    def net_consumption(self) -> Optional[float]:
        """Định mức đã cộng hao hụt. None nếu thiếu dữ liệu — không tự cho hao hụt = 0."""
        if self.consumption is None:
            return None
        wastage = self.wastage_pct
        if wastage is None:
            return None
        return round(self.consumption * (1 + wastage / 100.0), 6)

    def to_dict(self) -> Dict[str, Any]:
        data = {k: v for k, v in asdict(self).items() if k not in ("source", "extra")}
        data["extra"] = self.extra
        data["source"] = self.source.to_dict() if self.source else None
        return data


@dataclass
class PurchaseOrder:
    """5.3 — sinh bởi lsth-portal từ PO khách; erp và status cùng dùng."""

    po_no: str
    style: Optional[str] = None
    colors: List[str] = field(default_factory=list)
    size_breakdown: Dict[str, int] = field(default_factory=dict)
    qty: Optional[int] = None
    etd: Optional[str] = None
    ship_date: Optional[str] = None
    market: Optional[str] = None
    source: Optional[Source] = None

    REQUIRED = ("po_no", "style", "qty", "etd")

    def validate(self) -> List[str]:
        return [f for f in self.REQUIRED if getattr(self, f) in (None, "")]

    def to_dict(self) -> Dict[str, Any]:
        data = {k: v for k, v in asdict(self).items() if k != "source"}
        data["source"] = self.source.to_dict() if self.source else None
        return data


@dataclass
class NplItem:
    """5.3 — nguyên phụ liệu. erp và mail cùng cập nhật; status tổng hợp."""

    npl_type: str          # label | hanger | sticker | thread | polybag | carton
    code: str
    vendor: Optional[str] = None
    qty: Optional[float] = None
    order_date: Optional[str] = None
    etd: Optional[str] = None
    status: Optional[str] = None
    style: Optional[str] = None
    source: Optional[Source] = None

    TYPES = ("label", "hanger", "sticker", "thread", "polybag", "carton")

    def validate(self) -> List[str]:
        missing = [f for f in ("npl_type", "code") if not getattr(self, f)]
        if self.npl_type and self.npl_type not in self.TYPES:
            missing.append(f"npl_type không hợp lệ: {self.npl_type}")
        return missing

    def to_dict(self) -> Dict[str, Any]:
        data = {k: v for k, v in asdict(self).items() if k != "source"}
        data["source"] = self.source.to_dict() if self.source else None
        return data


@dataclass
class PackingSpec:
    """5.3 — lsth-drive tra ra từ SOF/DC; lsth-packing dùng để dựng TLĐG."""

    style: str
    market: Optional[str] = None
    folding_size: Optional[str] = None
    polybag_code: Optional[str] = None
    carton_layout: Optional[str] = None
    hangtag_position: Optional[str] = None
    sticker_rule: Optional[str] = None
    upc: Optional[str] = None
    source: Optional[Source] = None
    #: Trường tra không ra nguồn -> ghi vào đây để merchandiser biết chỗ cần mình.
    needs_human: List[str] = field(default_factory=list)

    #: Sai ở nhóm này dẫn tới đóng gói sai, hàng bị khách trả (luồng C).
    SAFETY_CRITICAL = ("hangtag_position", "sticker_rule")

    def validate(self) -> List[str]:
        return [f for f in self.SAFETY_CRITICAL if not getattr(self, f)]

    def to_dict(self) -> Dict[str, Any]:
        data = {k: v for k, v in asdict(self).items() if k != "source"}
        data["source"] = self.source.to_dict() if self.source else None
        return data


ENTITIES = {
    "Style": Style,
    "BomLine": BomLine,
    "PurchaseOrder": PurchaseOrder,
    "NplItem": NplItem,
    "PackingSpec": PackingSpec,
}
