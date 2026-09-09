"""S2 · lsth-erp — Sinh BOM, dựng PO nháp, kéo việc cần duyệt.

Nhóm việc chiếm 30,2% quỹ thời gian toàn khối — nặng nhất. Ra mắt chỉ đọc; quyền ghi mở sau 5 mã hàng đúng.

Trạng thái: hợp đồng tool đã chốt, phần thân chưa dựng.
Chặn bởi khoảng trống dữ liệu: G1 — xem docs/DATA_GAPS.md.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from ...core.envelope import ok
from ...core.errors import NotImplementedYetError
from ..base import BaseServer, ServerSpec

SPEC = ServerSpec(
    code="S2", module="s2_erp", name="lsth-erp",
    purpose="Sinh BOM, dựng PO nháp, kéo việc cần duyệt",
    resource="erp", group="Server v1.0", priority="Rất cao",
    difficulty="Trung bình", round=2,
    depends_on=['F2', 'F3', 'G1'], blocked_by=['G1'],
    accepted_by=['Chị Hằng', 'Chị Phúc'],
    tools=['bom_get', 'bom_generate', 'po_draft', 'fabric_claim_list', 'balance_check'],
)


class ErpServer(BaseServer):
    spec = SPEC

    def bom_get(self, style: str) -> Dict[str, Any]:
        """BomLine[] của một mã hàng lấy từ ERP"""
        raise NotImplementedYetError(
            "lsth-erp.bom_get",
            blocked_by="G1",
            hint="Lấp khoảng trống G1 trước (xem docs/DATA_GAPS.md), rồi làm bước 2 quy trình dựng: ngồi cạnh Chị Hằng ghi 20 thao tác.",
        )

    def bom_generate(self, master: str, colors: list, sizes: list) -> Dict[str, Any]:
        """Sinh BOM 202–374 dòng từ 7–22 mã vật tư gốc bằng phép nhân"""
        raise NotImplementedYetError(
            "lsth-erp.bom_generate",
            blocked_by="G1",
            hint="Lấp khoảng trống G1 trước (xem docs/DATA_GAPS.md), rồi làm bước 2 quy trình dựng: ngồi cạnh Chị Hằng ghi 20 thao tác.",
        )

    def po_draft(self, bom_id: str, vendor: str) -> Dict[str, Any]:
        """PO nháp — máy soạn, người bấm nút"""
        raise NotImplementedYetError(
            "lsth-erp.po_draft",
            blocked_by="G1",
            hint="Lấp khoảng trống G1 trước (xem docs/DATA_GAPS.md), rồi làm bước 2 quy trình dựng: ngồi cạnh Chị Hằng ghi 20 thao tác.",
        )

    def fabric_claim_list(self) -> Dict[str, Any]:
        """Phiếu bù vải chờ duyệt"""
        raise NotImplementedYetError(
            "lsth-erp.fabric_claim_list",
            blocked_by="G1",
            hint="Lấp khoảng trống G1 trước (xem docs/DATA_GAPS.md), rồi làm bước 2 quy trình dựng: ngồi cạnh Chị Hằng ghi 20 thao tác.",
        )

    def balance_check(self, style: str) -> Dict[str, Any]:
        """Cân đối định mức đã đặt với định mức cần"""
        raise NotImplementedYetError(
            "lsth-erp.balance_check",
            blocked_by="G1",
            hint="Lấp khoảng trống G1 trước (xem docs/DATA_GAPS.md), rồi làm bước 2 quy trình dựng: ngồi cạnh Chị Hằng ghi 20 thao tác.",
        )

