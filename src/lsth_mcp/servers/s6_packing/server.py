"""S6 · lsth-packing — TLĐG, FDW, PT8, tính kích túi.

Luồng rủi ro cao nhất: TLĐG sai dẫn tới đóng gói sai, hàng bị khách trả. Phải chạy song song ít nhất 5 mã hàng và có người soát 100% trước khi tin. Sai ở mục an toàn (vị trí bắn tag, loại đạn) là chưa đạt bất kể tỷ lệ.

Trạng thái: hợp đồng tool đã chốt, phần thân chưa dựng.
Chặn bởi khoảng trống dữ liệu: G4 — xem docs/DATA_GAPS.md.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from ...core.envelope import ok
from ...core.errors import NotImplementedYetError
from ..base import BaseServer, ServerSpec

SPEC = ServerSpec(
    code="S6", module="s6_packing", name="lsth-packing",
    purpose="TLĐG, FDW, PT8, tính kích túi",
    resource="packing", group="Server v1.0", priority="Trung bình",
    difficulty="Trung bình", round=4,
    depends_on=['S1', 'S3', 'F4', 'G4'], blocked_by=['G4'],
    accepted_by=['Chị Ly', 'Chị Hạnh'],
    tools=['tldg_draft', 'fdw_build', 'pt8_compose', 'polybag_size'],
)


class PackingServer(BaseServer):
    spec = SPEC

    def tldg_draft(self, style: str, market: str) -> Dict[str, Any]:
        """File TLĐG nháp dựng từ khuôn đã duyệt"""
        raise NotImplementedYetError(
            "lsth-packing.tldg_draft",
            blocked_by="G4",
            hint="Lấp khoảng trống G4 trước (xem docs/DATA_GAPS.md), rồi làm bước 2 quy trình dựng: ngồi cạnh Chị Ly ghi 20 thao tác.",
        )

    def fdw_build(self, images: list, specs: dict) -> Dict[str, Any]:
        """FDW nháp"""
        raise NotImplementedYetError(
            "lsth-packing.fdw_build",
            blocked_by="G4",
            hint="Lấp khoảng trống G4 trước (xem docs/DATA_GAPS.md), rồi làm bước 2 quy trình dựng: ngồi cạnh Chị Ly ghi 20 thao tác.",
        )

    def pt8_compose(self, style: str) -> Dict[str, Any]:
        """Bộ ảnh PT8"""
        raise NotImplementedYetError(
            "lsth-packing.pt8_compose",
            blocked_by="G4",
            hint="Lấp khoảng trống G4 trước (xem docs/DATA_GAPS.md), rồi làm bước 2 quy trình dựng: ngồi cạnh Chị Ly ghi 20 thao tác.",
        )

    def polybag_size(self, specs: dict, fold_ratio: float) -> Dict[str, Any]:
        """Kích thước túi"""
        raise NotImplementedYetError(
            "lsth-packing.polybag_size",
            blocked_by="G4",
            hint="Lấp khoảng trống G4 trước (xem docs/DATA_GAPS.md), rồi làm bước 2 quy trình dựng: ngồi cạnh Chị Ly ghi 20 thao tác.",
        )

