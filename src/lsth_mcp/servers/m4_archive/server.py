"""M4 · lsth-archive — Kho lịch sử mùa: giá NPL, báo cáo test, layout, định mức.

Thành phần rẻ nhất nhóm mới — chủ yếu gom file và đánh chỉ mục. Nhưng mỗi mùa trôi qua là mất thêm một lớp dữ liệu, nên đáng làm sớm.

Trạng thái: hợp đồng tool đã chốt, phần thân chưa dựng.
Không bị khoảng trống dữ liệu nào chặn — dựng được ngay khi tới vòng.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from ...core.envelope import ok
from ...core.errors import NotImplementedYetError
from ..base import BaseServer, ServerSpec

SPEC = ServerSpec(
    code="M4", module="m4_archive", name="lsth-archive",
    purpose="Kho lịch sử mùa: giá NPL, báo cáo test, layout, định mức",
    resource="archive", group="MỚI", priority="Trung bình",
    difficulty="Thấp", round=3,
    depends_on=['F3', 'F4'], blocked_by=[],
    accepted_by=['Chị Phạm Hương Vân'],
    tools=['price_history', 'report_history', 'layout_history', 'consumption_history'],
)


class ArchiveServer(BaseServer):
    spec = SPEC

    def price_history(self, item: str, season: str = '') -> Dict[str, Any]:
        """Giá NPL các mùa trước"""
        raise NotImplementedYetError(
            "lsth-archive.price_history",
            blocked_by="không",
            hint="Thành phần này thuộc vòng 3. Bắt đầu bằng bước 2 quy trình dựng: ngồi cạnh Chị Phạm Hương Vân ghi lại 20 thao tác thật.",
        )

    def report_history(self, style: str) -> Dict[str, Any]:
        """Số báo cáo test và ngày ra báo cáo"""
        raise NotImplementedYetError(
            "lsth-archive.report_history",
            blocked_by="không",
            hint="Thành phần này thuộc vòng 3. Bắt đầu bằng bước 2 quy trình dựng: ngồi cạnh Chị Phạm Hương Vân ghi lại 20 thao tác thật.",
        )

    def layout_history(self, style: str, market: str) -> Dict[str, Any]:
        """Layout đã duyệt"""
        raise NotImplementedYetError(
            "lsth-archive.layout_history",
            blocked_by="không",
            hint="Thành phần này thuộc vòng 3. Bắt đầu bằng bước 2 quy trình dựng: ngồi cạnh Chị Phạm Hương Vân ghi lại 20 thao tác thật.",
        )

    def consumption_history(self, style: str) -> Dict[str, Any]:
        """Định mức đã dùng"""
        raise NotImplementedYetError(
            "lsth-archive.consumption_history",
            blocked_by="không",
            hint="Thành phần này thuộc vòng 3. Bắt đầu bằng bước 2 quy trình dựng: ngồi cạnh Chị Phạm Hương Vân ghi lại 20 thao tác thật.",
        )

