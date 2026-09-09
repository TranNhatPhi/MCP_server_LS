"""M2 · lsth-translate — Dịch tài liệu kỹ thuật có kiểm soát thuật ngữ.

Đội đã tự dùng ChatGPT cho tài liệu khách — làm sớm vừa giảm workload vừa đóng một lỗ hổng bảo mật. RÀNG BUỘC BẮT BUỘC: chỉ dịch phần chữ, giữ nguyên mọi con số và mã; từ điển thuật ngữ khoá cứng, không cho mô hình tự chọn từ; xuất bản song ngữ để người soát đối chiếu.

Trạng thái: hợp đồng tool đã chốt, phần thân chưa dựng.
Chặn bởi khoảng trống dữ liệu: G8 — xem docs/DATA_GAPS.md.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from ...core.envelope import ok
from ...core.errors import NotImplementedYetError
from ..base import BaseServer, ServerSpec

SPEC = ServerSpec(
    code="M2", module="m2_translate", name="lsth-translate",
    purpose="Dịch tài liệu kỹ thuật có kiểm soát thuật ngữ",
    resource="translate", group="MỚI", priority="Cao",
    difficulty="Thấp", round=1,
    depends_on=['F5', 'G8'], blocked_by=['G8'],
    accepted_by=['Chị Bích Thủy', 'Chị Nhiên'],
    tools=['doc_translate', 'comment_translate', 'glossary_manage', 'spec_table_extract'],
)


class TranslateServer(BaseServer):
    spec = SPEC

    def doc_translate(self, file: str, glossary: str) -> Dict[str, Any]:
        """Dịch tài liệu, xuất song ngữ"""
        raise NotImplementedYetError(
            "lsth-translate.doc_translate",
            blocked_by="G8",
            hint="Lấp khoảng trống G8 trước (xem docs/DATA_GAPS.md), rồi làm bước 2 quy trình dựng: ngồi cạnh Chị Bích Thủy ghi 20 thao tác.",
        )

    def comment_translate(self, text: str) -> Dict[str, Any]:
        """Dịch comment của khách"""
        raise NotImplementedYetError(
            "lsth-translate.comment_translate",
            blocked_by="G8",
            hint="Lấp khoảng trống G8 trước (xem docs/DATA_GAPS.md), rồi làm bước 2 quy trình dựng: ngồi cạnh Chị Bích Thủy ghi 20 thao tác.",
        )

    def glossary_manage(self, action: str, term: dict = None) -> Dict[str, Any]:
        """Quản lý từ điển thuật ngữ"""
        raise NotImplementedYetError(
            "lsth-translate.glossary_manage",
            blocked_by="G8",
            hint="Lấp khoảng trống G8 trước (xem docs/DATA_GAPS.md), rồi làm bước 2 quy trình dựng: ngồi cạnh Chị Bích Thủy ghi 20 thao tác.",
        )

    def spec_table_extract(self, file: str) -> Dict[str, Any]:
        """Bóc bảng thông số từ ảnh hoặc PDF"""
        raise NotImplementedYetError(
            "lsth-translate.spec_table_extract",
            blocked_by="G8",
            hint="Lấp khoảng trống G8 trước (xem docs/DATA_GAPS.md), rồi làm bước 2 quy trình dựng: ngồi cạnh Chị Bích Thủy ghi 20 thao tác.",
        )

