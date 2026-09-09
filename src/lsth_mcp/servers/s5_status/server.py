"""S5 · lsth-status — Bảng trạng thái T&A, cảnh báo trễ.

Thay việc dò hộp thư 90 phút mỗi ngày. Nhánh 'không có bất thường' quan trọng ngang nhánh cảnh báo: không làm phiền khi không có gì để báo.

Trạng thái: hợp đồng tool đã chốt, phần thân chưa dựng.
Chặn bởi khoảng trống dữ liệu: G1 — xem docs/DATA_GAPS.md.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from ...core.envelope import ok
from ...core.errors import NotImplementedYetError
from ..base import BaseServer, ServerSpec

SPEC = ServerSpec(
    code="S5", module="s5_status", name="lsth-status",
    purpose="Bảng trạng thái T&A, cảnh báo trễ",
    resource="status", group="Server v1.0", priority="Cao",
    difficulty="Trung bình", round=3,
    depends_on=['S2', 'S4', 'G1'], blocked_by=['G1'],
    accepted_by=['Toàn khối', 'Sản xuất'],
    tools=['order_status', 'npl_eta', 'ta_alerts', 'wip_report'],
)


class StatusServer(BaseServer):
    spec = SPEC

    def order_status(self, po: str) -> Dict[str, Any]:
        """Tiến độ một PO"""
        raise NotImplementedYetError(
            "lsth-status.order_status",
            blocked_by="G1",
            hint="Lấp khoảng trống G1 trước (xem docs/DATA_GAPS.md), rồi làm bước 2 quy trình dựng: ngồi cạnh Toàn khối ghi 20 thao tác.",
        )

    def npl_eta(self, style: str) -> Dict[str, Any]:
        """Tình trạng NPL của một mã hàng"""
        raise NotImplementedYetError(
            "lsth-status.npl_eta",
            blocked_by="G1",
            hint="Lấp khoảng trống G1 trước (xem docs/DATA_GAPS.md), rồi làm bước 2 quy trình dựng: ngồi cạnh Toàn khối ghi 20 thao tác.",
        )

    def ta_alerts(self) -> Dict[str, Any]:
        """Mã hàng trễ mốc T&A"""
        raise NotImplementedYetError(
            "lsth-status.ta_alerts",
            blocked_by="G1",
            hint="Lấp khoảng trống G1 trước (xem docs/DATA_GAPS.md), rồi làm bước 2 quy trình dựng: ngồi cạnh Toàn khối ghi 20 thao tác.",
        )

    def wip_report(self, week: str) -> Dict[str, Any]:
        """Báo cáo WIP tuần"""
        raise NotImplementedYetError(
            "lsth-status.wip_report",
            blocked_by="G1",
            hint="Lấp khoảng trống G1 trước (xem docs/DATA_GAPS.md), rồi làm bước 2 quy trình dựng: ngồi cạnh Toàn khối ghi 20 thao tác.",
        )

