"""M1 · lsth-sample — Vòng đời mẫu: FIT, PP, TOP, photoshoot.

Mảng trắng lớn nhất của v1.0. Chị Huỳnh Thị Thúy dành 100% quỹ thời gian ở đây. Con số 4,0% là thấp giả tạo vì file Lucy team không có cột %.

Trạng thái: hợp đồng tool đã chốt, phần thân chưa dựng.
Chặn bởi khoảng trống dữ liệu: G6 — xem docs/DATA_GAPS.md.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from ...core.envelope import ok
from ...core.errors import NotImplementedYetError
from ..base import BaseServer, ServerSpec

SPEC = ServerSpec(
    code="M1", module="m1_sample", name="lsth-sample",
    purpose="Vòng đời mẫu: FIT, PP, TOP, photoshoot",
    resource="sample", group="MỚI", priority="Trung bình",
    difficulty="Trung bình", round=4,
    depends_on=['S1', 'M2'], blocked_by=['G6'],
    accepted_by=['Chị Huỳnh Thị Thúy', 'Chị Tuyết Như'],
    tools=['sample_request', 'sample_status', 'hangtag_make', 'sending_list', 'comment_sync'],
)


class SampleServer(BaseServer):
    spec = SPEC

    def sample_request(self, style: str, kind: str) -> Dict[str, Any]:
        """Tạo yêu cầu mẫu"""
        raise NotImplementedYetError(
            "lsth-sample.sample_request",
            blocked_by="G6",
            hint="Lấp khoảng trống G6 trước (xem docs/DATA_GAPS.md), rồi làm bước 2 quy trình dựng: ngồi cạnh Chị Huỳnh Thị Thúy ghi 20 thao tác.",
        )

    def sample_status(self, style: str) -> Dict[str, Any]:
        """Tiến độ mẫu"""
        raise NotImplementedYetError(
            "lsth-sample.sample_status",
            blocked_by="G6",
            hint="Lấp khoảng trống G6 trước (xem docs/DATA_GAPS.md), rồi làm bước 2 quy trình dựng: ngồi cạnh Chị Huỳnh Thị Thúy ghi 20 thao tác.",
        )

    def hangtag_make(self, sample: dict) -> Dict[str, Any]:
        """Dựng hangtag"""
        raise NotImplementedYetError(
            "lsth-sample.hangtag_make",
            blocked_by="G6",
            hint="Lấp khoảng trống G6 trước (xem docs/DATA_GAPS.md), rồi làm bước 2 quy trình dựng: ngồi cạnh Chị Huỳnh Thị Thúy ghi 20 thao tác.",
        )

    def sending_list(self, bill: str, destination: str) -> Dict[str, Any]:
        """Danh sách gửi hàng"""
        raise NotImplementedYetError(
            "lsth-sample.sending_list",
            blocked_by="G6",
            hint="Lấp khoảng trống G6 trước (xem docs/DATA_GAPS.md), rồi làm bước 2 quy trình dựng: ngồi cạnh Chị Huỳnh Thị Thúy ghi 20 thao tác.",
        )

    def comment_sync(self, customer_system: str) -> Dict[str, Any]:
        """Đồng bộ comment từ hệ thống khách"""
        raise NotImplementedYetError(
            "lsth-sample.comment_sync",
            blocked_by="G6",
            hint="Lấp khoảng trống G6 trước (xem docs/DATA_GAPS.md), rồi làm bước 2 quy trình dựng: ngồi cạnh Chị Huỳnh Thị Thúy ghi 20 thao tác.",
        )

