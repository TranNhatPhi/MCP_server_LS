"""S4 · lsth-mail — Trích ETD, tìm luồng thư, soạn nháp.

Email chiếm 14,8% quỹ thời gian. Chỉ đọc và soạn nháp — KHÔNG có quyền gửi (nguyên tắc 1). Nuôi n8n WF-1.

Trạng thái: hợp đồng tool đã chốt, phần thân chưa dựng.
Không bị khoảng trống dữ liệu nào chặn — dựng được ngay khi tới vòng.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from ...core.envelope import ok
from ...core.errors import NotImplementedYetError
from ..base import BaseServer, ServerSpec

SPEC = ServerSpec(
    code="S4", module="s4_mail", name="lsth-mail",
    purpose="Trích ETD, tìm luồng thư, soạn nháp",
    resource="mail", group="Server v1.0", priority="Cao",
    difficulty="Trung bình", round=3,
    depends_on=['F1', 'F3'], blocked_by=[],
    accepted_by=['Chị Quỳnh', 'Chị Thương'],
    tools=['thread_search', 'etd_extract', 'draft_reply', 'claim_draft'],
)


class MailServer(BaseServer):
    spec = SPEC

    def thread_search(self, style: str = '', po: str = '') -> Dict[str, Any]:
        """Luồng thư liên quan"""
        raise NotImplementedYetError(
            "lsth-mail.thread_search",
            blocked_by="không",
            hint="Thành phần này thuộc vòng 3. Bắt đầu bằng bước 2 quy trình dựng: ngồi cạnh Chị Quỳnh ghi lại 20 thao tác thật.",
        )

    def etd_extract(self, since: str, until: str) -> Dict[str, Any]:
        """NplItem[] với ETD trích từ thư"""
        raise NotImplementedYetError(
            "lsth-mail.etd_extract",
            blocked_by="không",
            hint="Thành phần này thuộc vòng 3. Bắt đầu bằng bước 2 quy trình dựng: ngồi cạnh Chị Quỳnh ghi lại 20 thao tác thật.",
        )

    def draft_reply(self, thread_id: str, points: list) -> Dict[str, Any]:
        """Thư nháp"""
        raise NotImplementedYetError(
            "lsth-mail.draft_reply",
            blocked_by="không",
            hint="Thành phần này thuộc vòng 3. Bắt đầu bằng bước 2 quy trình dựng: ngồi cạnh Chị Quỳnh ghi lại 20 thao tác thật.",
        )

    def claim_draft(self, issue: str) -> Dict[str, Any]:
        """Thư khiếu nại nháp"""
        raise NotImplementedYetError(
            "lsth-mail.claim_draft",
            blocked_by="không",
            hint="Thành phần này thuộc vòng 3. Bắt đầu bằng bước 2 quy trình dựng: ngồi cạnh Chị Quỳnh ghi lại 20 thao tác thật.",
        )

