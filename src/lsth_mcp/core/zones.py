"""Bốn vùng dữ liệu — chương 9 kiến trúc v1.0, nguyên tắc 6.

Z1 công khai   -> được đưa lên dịch vụ AI ngoài
Z2 nội bộ      -> xử lý trên hạ tầng nội bộ
Z3 tài liệu khách (NDA) -> tuyệt đối không ra ngoài; đây là vùng đội đang lỡ dùng
                  ChatGPT để dịch tech pack, chính là lỗ hổng M2 phải bịt
Z4 hạn chế     -> giá, hợp đồng, dữ liệu nhân sự: chỉ người được chỉ định

Quy tắc phân vùng đọc từ config/data_zones.yaml để sửa được mà không đụng code.
Ranh giới cuối cùng còn chờ G8 (rà điều khoản bảo mật của 5 khách).
"""
from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from typing import Dict, List, Optional

from .errors import ZoneViolationError

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]


class Zone(IntEnum):
    PUBLIC = 1
    INTERNAL = 2
    CUSTOMER = 3
    RESTRICTED = 4

    @property
    def label(self) -> str:
        return {
            Zone.PUBLIC: "Z1 công khai",
            Zone.INTERNAL: "Z2 nội bộ",
            Zone.CUSTOMER: "Z3 tài liệu khách (NDA)",
            Zone.RESTRICTED: "Z4 hạn chế",
        }[self]


#: Vùng nào được gửi ra dịch vụ AI công cộng. Mặc định chỉ Z1.
EXTERNAL_AI_ALLOWED = {Zone.PUBLIC}

DEFAULT_RULES: Dict[str, str] = {
    "*tech*pack*": "CUSTOMER",
    "*techpack*": "CUSTOMER",
    "*BOM*": "CUSTOMER",
    "*price*": "RESTRICTED",
    "*gia*": "RESTRICTED",
    "*hop-dong*": "RESTRICTED",
    "*contract*": "RESTRICTED",
    "*nhan-su*": "RESTRICTED",
}


@dataclass
class ZoneClassifier:
    rules: Dict[str, Zone]
    default: Zone = Zone.INTERNAL

    @classmethod
    def load(cls, config_file: Optional[Path] = None) -> "ZoneClassifier":
        rules: Dict[str, Zone] = {k: Zone[v] for k, v in DEFAULT_RULES.items()}
        default = Zone.INTERNAL
        if config_file and config_file.exists() and yaml is not None:
            loaded = yaml.safe_load(config_file.read_text(encoding="utf-8")) or {}
            default = Zone[str(loaded.get("default", "INTERNAL")).upper()]
            for pattern, zone_name in (loaded.get("rules") or {}).items():
                rules[pattern] = Zone[str(zone_name).upper()]
        return cls(rules=rules, default=default)

    def classify(self, path) -> Zone:
        """Vùng của một file. Khớp nhiều luật thì lấy vùng nghiêm ngặt nhất."""
        name = str(path).lower()
        matched: List[Zone] = [
            zone for pattern, zone in self.rules.items()
            if fnmatch.fnmatch(name, pattern.lower())
        ]
        return max(matched) if matched else self.default

    def assert_external_ai_allowed(self, path) -> None:
        """Chặn trước khi một tool định gửi nội dung file ra dịch vụ ngoài."""
        zone = self.classify(path)
        if zone not in EXTERNAL_AI_ALLOWED:
            raise ZoneViolationError(
                f"File thuộc {zone.label}, không được đưa ra dịch vụ AI bên ngoài.",
                hint="Dùng mô hình chạy nội bộ, hoặc bóc phần chữ không nhạy cảm rồi gửi. "
                     "Phạm vi cho phép còn chờ kết quả rà NDA (khoảng trống G8).",
                context={"file": str(path), "zone": zone.name},
            )
