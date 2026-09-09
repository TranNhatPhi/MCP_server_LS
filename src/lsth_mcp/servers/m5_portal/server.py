"""M5 · lsth-portal-multi — Cổng khách đa hệ thống — 9 cổng.

Thành phần tốn công nhất và dễ hỏng nhất toàn danh mục. Chín cổng, phần lớn không có API, mỗi cổng một cách đăng nhập. BẮT BUỘC: xin phép khách trước, dùng tài khoản riêng cho tự động hoá, và server phải TỰ DỪNG BÁO NGƯỜI khi giao diện đổi thay vì đoán bừa. Tự động hoá không làm cổng khách nhanh lên — nó chỉ giúp người không phải ngồi chờ.

Trạng thái: hợp đồng tool đã chốt, phần thân chưa dựng.
Chặn bởi khoảng trống dữ liệu: G2 — xem docs/DATA_GAPS.md.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from ...core.envelope import ok
from ...core.errors import NotImplementedYetError
from ..base import BaseServer, ServerSpec

SPEC = ServerSpec(
    code="M5", module="m5_portal", name="lsth-portal-multi",
    purpose="Cổng khách đa hệ thống — 9 cổng",
    resource="portal", group="MỚI", priority="Thấp",
    difficulty="Rất cao", round=5,
    depends_on=['G2', 'thoả thuận khách'], blocked_by=['G2'],
    accepted_by=['Chị Hạnh', 'Chị Phúc'],
    tools=['portal_list', 'portal_download', 'portal_submit', 'portal_health'],
)


class MultiPortalServer(BaseServer):
    spec = SPEC

    def portal_list(self) -> Dict[str, Any]:
        """9 cổng và trạng thái tài khoản từng cổng"""
        raise NotImplementedYetError(
            "lsth-portal-multi.portal_list",
            blocked_by="G2",
            hint="Lấp khoảng trống G2 trước (xem docs/DATA_GAPS.md), rồi làm bước 2 quy trình dựng: ngồi cạnh Chị Hạnh ghi 20 thao tác.",
        )

    def portal_download(self, portal: str, ref: str) -> Dict[str, Any]:
        """Tải tài liệu từ một cổng"""
        raise NotImplementedYetError(
            "lsth-portal-multi.portal_download",
            blocked_by="G2",
            hint="Lấp khoảng trống G2 trước (xem docs/DATA_GAPS.md), rồi làm bước 2 quy trình dựng: ngồi cạnh Chị Hạnh ghi 20 thao tác.",
        )

    def portal_submit(self, portal: str, payload: dict) -> Dict[str, Any]:
        """Nộp lên cổng — cần người bấm nút"""
        raise NotImplementedYetError(
            "lsth-portal-multi.portal_submit",
            blocked_by="G2",
            hint="Lấp khoảng trống G2 trước (xem docs/DATA_GAPS.md), rồi làm bước 2 quy trình dựng: ngồi cạnh Chị Hạnh ghi 20 thao tác.",
        )

    def portal_health(self, portal: str = '') -> Dict[str, Any]:
        """Kiểm cổng còn đúng giao diện đã biết không"""
        raise NotImplementedYetError(
            "lsth-portal-multi.portal_health",
            blocked_by="G2",
            hint="Lấp khoảng trống G2 trước (xem docs/DATA_GAPS.md), rồi làm bước 2 quy trình dựng: ngồi cạnh Chị Hạnh ghi 20 thao tác.",
        )

