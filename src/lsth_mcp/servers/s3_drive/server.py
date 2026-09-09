"""S3 · lsth-drive — Tra SOF, DC, UPC theo style và thị trường.

Đòi hỏi chuẩn hoá quy ước đặt tên file trước — đó chính là G5.

Trạng thái: hợp đồng tool đã chốt, phần thân chưa dựng.
Chặn bởi khoảng trống dữ liệu: G5 — xem docs/DATA_GAPS.md.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from ...core.envelope import ok
from ...core.errors import NotImplementedYetError
from ..base import BaseServer, ServerSpec

SPEC = ServerSpec(
    code="S3", module="s3_drive", name="lsth-drive",
    purpose="Tra SOF, DC, UPC theo style và thị trường",
    resource="drive", group="Server v1.0", priority="Cao",
    difficulty="Thấp", round=2,
    depends_on=['F3', 'F4', 'G5'], blocked_by=['G5'],
    accepted_by=['Chị Thúy', 'Chị Ly'],
    tools=['sof_lookup', 'dc_get', 'upc_find', 'layout_publish'],
)


class DriveServer(BaseServer):
    spec = SPEC

    def sof_lookup(self, style: str, market: str) -> Dict[str, Any]:
        """PackingSpec tra từ SOF"""
        raise NotImplementedYetError(
            "lsth-drive.sof_lookup",
            blocked_by="G5",
            hint="Lấp khoảng trống G5 trước (xem docs/DATA_GAPS.md), rồi làm bước 2 quy trình dựng: ngồi cạnh Chị Thúy ghi 20 thao tác.",
        )

    def dc_get(self, style: str) -> Dict[str, Any]:
        """Tài liệu DC Production kèm bản dịch"""
        raise NotImplementedYetError(
            "lsth-drive.dc_get",
            blocked_by="G5",
            hint="Lấp khoảng trống G5 trước (xem docs/DATA_GAPS.md), rồi làm bước 2 quy trình dựng: ngồi cạnh Chị Thúy ghi 20 thao tác.",
        )

    def upc_find(self, style: str, color: str, size: str) -> Dict[str, Any]:
        """Mã UPC"""
        raise NotImplementedYetError(
            "lsth-drive.upc_find",
            blocked_by="G5",
            hint="Lấp khoảng trống G5 trước (xem docs/DATA_GAPS.md), rồi làm bước 2 quy trình dựng: ngồi cạnh Chị Thúy ghi 20 thao tác.",
        )

    def layout_publish(self, file: str, style: str) -> Dict[str, Any]:
        """Đăng layout đã duyệt lên ổ chung"""
        raise NotImplementedYetError(
            "lsth-drive.layout_publish",
            blocked_by="G5",
            hint="Lấp khoảng trống G5 trước (xem docs/DATA_GAPS.md), rồi làm bước 2 quy trình dựng: ngồi cạnh Chị Thúy ghi 20 thao tác.",
        )

