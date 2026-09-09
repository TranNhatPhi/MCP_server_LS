"""Mười hai server nghiệp vụ: bảy server v1.0 và năm thành phần mới của v2.0.

Năm thành phần nền F1–F5 không nằm ở đây vì chúng không phải server:
  F1 cổng điều phối  -> server.py + core/permissions.py + core/audit.py
  F2 mô hình dữ liệu -> core/models.py
  F3 ánh xạ định danh -> domain/identity.py
  F4 kho template     -> domain/templates.py
  F5 bộ đánh giá      -> domain/evalset.py
"""
from .base import BaseServer, ServerSpec
from .m1_sample import SPEC as M1
from .m2_translate import SPEC as M2
from .m3_compliance import SPEC as M3
from .m4_archive import SPEC as M4
from .m5_portal import SPEC as M5
from .s1_techpack import SPEC as S1
from .s1_techpack import TechpackServer
from .s2_erp import SPEC as S2
from .s3_drive import SPEC as S3
from .s4_mail import SPEC as S4
from .s5_status import SPEC as S5
from .s6_packing import SPEC as S6
from .s7_portal import SPEC as S7

#: Toàn bộ đặc tả server, xếp theo vòng triển khai của lộ trình v2.0.
ALL_SPECS = [S1, S2, S3, S4, S5, S6, S7, M1, M2, M3, M4, M5]

#: Năm thành phần nền — không phải server nhưng phải có trước, nên liệt kê để
#: `lsth-mcp status` in đủ 17 thành phần.
FOUNDATION = [
    {"code": "F1", "name": "Cổng điều phối", "round": 1, "priority": "Cao",
     "module": "server.py + core/permissions.py + core/audit.py"},
    {"code": "F2", "name": "Mô hình dữ liệu chuẩn", "round": 1, "priority": "Cao",
     "module": "core/models.py"},
    {"code": "F3", "name": "Bảng ánh xạ định danh", "round": 1, "priority": "Cao",
     "module": "domain/identity.py"},
    {"code": "F4", "name": "Kho template & quy ước tên", "round": 1, "priority": "Cao",
     "module": "domain/templates.py"},
    {"code": "F5", "name": "Bộ đánh giá chất lượng", "round": 1, "priority": "Cao",
     "module": "domain/evalset.py"},
]


def spec_by_code(code: str):
    for spec in ALL_SPECS:
        if spec.code.upper() == code.upper():
            return spec
    return None


def specs_for_round(round_number: int):
    return [s for s in ALL_SPECS if s.round == round_number]


__all__ = ["BaseServer", "ServerSpec", "ALL_SPECS", "FOUNDATION",
           "TechpackServer", "spec_by_code", "specs_for_round"]
