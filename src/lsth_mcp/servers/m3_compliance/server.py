"""M3 · lsth-compliance — Chứng từ và kiểm nghiệm: COC, RSL, CPSIA, TC, GACC.

7,1% quỹ thời gian toàn khối; riêng chị Phạm Hương Vân là 50%. Giá trị kép: vừa giảm giờ vừa giảm rủi ro pháp lý — thiếu chứng nhận CPSIA có thể bị giữ hàng ở hải quan.

Trạng thái: hợp đồng tool đã chốt, phần thân chưa dựng.
Chặn bởi khoảng trống dữ liệu: G4 — xem docs/DATA_GAPS.md.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from ...core.envelope import ok
from ...core.errors import NotImplementedYetError
from ..base import BaseServer, ServerSpec

SPEC = ServerSpec(
    code="M3", module="m3_compliance", name="lsth-compliance",
    purpose="Chứng từ và kiểm nghiệm: COC, RSL, CPSIA, TC, GACC",
    resource="compliance", group="MỚI", priority="Cao",
    difficulty="Trung bình", round=3,
    depends_on=['S1', 'M4', 'G4'], blocked_by=['G4'],
    accepted_by=['Chị Phạm Hương Vân', 'Chị Bích Thủy', 'Chị Ngọc Ánh'],
    tools=['test_report_fill', 'tc_match', 'coc_build', 'cert_expiry_check', 'gacc_package'],
)


class ComplianceServer(BaseServer):
    spec = SPEC

    def test_report_fill(self, manual: str, report: str) -> Dict[str, Any]:
        """Tự điền báo cáo test từ manual khách"""
        raise NotImplementedYetError(
            "lsth-compliance.test_report_fill",
            blocked_by="G4",
            hint="Lấp khoảng trống G4 trước (xem docs/DATA_GAPS.md), rồi làm bước 2 quy trình dựng: ngồi cạnh Chị Phạm Hương Vân ghi 20 thao tác.",
        )

    def tc_match(self, po: str, tc_files: list) -> Dict[str, Any]:
        """Dò TC vải NCC gửi khớp với từng mã hàng"""
        raise NotImplementedYetError(
            "lsth-compliance.tc_match",
            blocked_by="G4",
            hint="Lấp khoảng trống G4 trước (xem docs/DATA_GAPS.md), rồi làm bước 2 quy trình dựng: ngồi cạnh Chị Phạm Hương Vân ghi 20 thao tác.",
        )

    def coc_build(self, style: str, reports: list) -> Dict[str, Any]:
        """Dựng COC từ các báo cáo"""
        raise NotImplementedYetError(
            "lsth-compliance.coc_build",
            blocked_by="G4",
            hint="Lấp khoảng trống G4 trước (xem docs/DATA_GAPS.md), rồi làm bước 2 quy trình dựng: ngồi cạnh Chị Phạm Hương Vân ghi 20 thao tác.",
        )

    def cert_expiry_check(self) -> Dict[str, Any]:
        """Chứng nhận sắp hết hiệu lực"""
        raise NotImplementedYetError(
            "lsth-compliance.cert_expiry_check",
            blocked_by="G4",
            hint="Lấp khoảng trống G4 trước (xem docs/DATA_GAPS.md), rồi làm bước 2 quy trình dựng: ngồi cạnh Chị Phạm Hương Vân ghi 20 thao tác.",
        )

    def gacc_package(self, style: str) -> Dict[str, Any]:
        """Đóng gói hồ sơ GACC"""
        raise NotImplementedYetError(
            "lsth-compliance.gacc_package",
            blocked_by="G4",
            hint="Lấp khoảng trống G4 trước (xem docs/DATA_GAPS.md), rồi làm bước 2 quy trình dựng: ngồi cạnh Chị Phạm Hương Vân ghi 20 thao tác.",
        )

