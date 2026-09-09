"""F4 · Kho template và quy ước đặt tên.

Giữ file khuôn đã duyệt (TLĐG, Worksheet, BOM, FDW, báo cáo test) và quy ước đặt
tên file. Khoảng trống G4 chặn nhiều thành phần nhất — S6, M1, M3 đều không dựng
được nếu chưa có khuôn.

Khuôn nằm ở data/templates, khai báo trong data/templates/registry.yaml.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.errors import NotFoundError, ValidationError
from ..core.paths import render_name
from ..core.provenance import Source

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]

#: Năm loại khuôn cần xin ở tuần này (việc số 2 trong bốn việc đề nghị).
KINDS = ("tldg", "worksheet", "bom", "tuv_report", "fdw")


@dataclass
class Template:
    kind: str
    file: Path
    customer: Optional[str] = None
    market: Optional[str] = None
    naming: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None
    notes: Optional[str] = None
    cell_map: Dict[str, str] = field(default_factory=dict)

    @property
    def source(self) -> Source:
        return Source(file=str(self.file), note=f"khuôn {self.kind}")

    def target_name(self, context: Dict[str, Any]) -> str:
        if not self.naming:
            raise ValidationError(
                f"Khuôn {self.kind} chưa khai quy ước đặt tên.",
                hint="Thêm khoá `naming` cho khuôn này trong data/templates/registry.yaml.",
            )
        return render_name(self.naming, context)


@dataclass
class TemplateStore:
    templates: List[Template] = field(default_factory=list)
    root: Optional[Path] = None

    @classmethod
    def load(cls, root: Any) -> "TemplateStore":
        root = Path(root)
        registry = root / "registry.yaml"
        if not registry.exists() or yaml is None:
            return cls(templates=[], root=root)
        data = yaml.safe_load(registry.read_text(encoding="utf-8")) or {}
        templates = [
            Template(
                kind=str(entry["kind"]).lower(),
                file=root / entry["file"],
                customer=entry.get("customer"),
                market=entry.get("market"),
                naming=entry.get("naming"),
                approved_by=entry.get("approved_by"),
                approved_at=entry.get("approved_at"),
                notes=entry.get("notes"),
                cell_map=entry.get("cell_map") or {},
            )
            for entry in (data.get("templates") or [])
        ]
        return cls(templates=templates, root=root)

    def get(self, kind: str, *, customer: Optional[str] = None,
            market: Optional[str] = None) -> Template:
        """Khuôn riêng của khách được ưu tiên hơn khuôn chung."""
        kind = kind.lower()
        candidates = [t for t in self.templates if t.kind == kind]
        if customer:
            specific = [t for t in candidates
                        if (t.customer or "").casefold() == customer.casefold()]
            candidates = specific or [t for t in candidates if not t.customer]
        if market:
            narrowed = [t for t in candidates
                        if not t.market or t.market.casefold() == market.casefold()]
            candidates = narrowed or candidates

        for template in candidates:
            if template.file.exists():
                return template

        raise NotFoundError(
            f"Chưa có khuôn '{kind}'" + (f" cho khách {customer}." if customer else "."),
            hint="Xin merchandiser một file đã duyệt, đặt vào data/templates và khai vào "
                 "registry.yaml. Đây là khoảng trống G4 — chặn S6, M1, M3.",
            context={"kind": kind, "customer": customer, "known_kinds": self.kinds()},
        )

    def kinds(self) -> List[str]:
        return sorted({t.kind for t in self.templates})

    def missing_kinds(self) -> List[str]:
        """Loại khuôn còn thiếu so với danh sách phải có — báo cáo tiến độ lấp G4."""
        have = {t.kind for t in self.templates if t.file.exists()}
        return [k for k in KINDS if k not in have]
