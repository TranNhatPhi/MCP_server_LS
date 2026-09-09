"""S7 · lsth-portal — Cổng khách hàng — bản v1.0, nay gộp vào M5.

ĐÃ GỘP VÀO M5. Gói này giữ lại để không gãy tham chiếu từ tài liệu v1.0; code mới viết ở servers/m5_portal.

Trạng thái: hợp đồng tool đã chốt, phần thân chưa dựng.
Chặn bởi khoảng trống dữ liệu: G2 — xem docs/DATA_GAPS.md.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from ...core.envelope import ok
from ...core.errors import NotImplementedYetError
from ..base import BaseServer, ServerSpec

SPEC = ServerSpec(
    code="S7", module="s7_portal", name="lsth-portal",
    purpose="Cổng khách hàng — bản v1.0, nay gộp vào M5",
    resource="portal", group="Server v1.0", priority="Thấp",
    difficulty="Cao", round=5,
    depends_on=['G2'], blocked_by=['G2'],
    accepted_by=['Chị Hạnh', 'Chị Phúc'],
    tools=['symparel_download', 'quonda_book_fi', 'vsn_submit', 'gacc_upload'],
)


class PortalLegacyServer(BaseServer):
    spec = SPEC

    def symparel_download(self, po: str) -> Dict[str, Any]:
        """Tải PO từ Symparel"""
        raise NotImplementedYetError(
            "lsth-portal.symparel_download",
            blocked_by="G2",
            hint="Lấp khoảng trống G2 trước (xem docs/DATA_GAPS.md), rồi làm bước 2 quy trình dựng: ngồi cạnh Chị Hạnh ghi 20 thao tác.",
        )

    def quonda_book_fi(self, items: list) -> Dict[str, Any]:
        """Book kiểm hàng cuối"""
        raise NotImplementedYetError(
            "lsth-portal.quonda_book_fi",
            blocked_by="G2",
            hint="Lấp khoảng trống G2 trước (xem docs/DATA_GAPS.md), rồi làm bước 2 quy trình dựng: ngồi cạnh Chị Hạnh ghi 20 thao tác.",
        )

    def vsn_submit(self, sample: dict) -> Dict[str, Any]:
        """Submit mẫu lên VSN"""
        raise NotImplementedYetError(
            "lsth-portal.vsn_submit",
            blocked_by="G2",
            hint="Lấp khoảng trống G2 trước (xem docs/DATA_GAPS.md), rồi làm bước 2 quy trình dựng: ngồi cạnh Chị Hạnh ghi 20 thao tác.",
        )

    def gacc_upload(self, dossier: dict) -> Dict[str, Any]:
        """Upload hồ sơ e-filing GACC"""
        raise NotImplementedYetError(
            "lsth-portal.gacc_upload",
            blocked_by="G2",
            hint="Lấp khoảng trống G2 trước (xem docs/DATA_GAPS.md), rồi làm bước 2 quy trình dựng: ngồi cạnh Chị Hạnh ghi 20 thao tác.",
        )

