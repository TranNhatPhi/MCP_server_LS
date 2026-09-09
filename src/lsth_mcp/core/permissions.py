"""Ma trận quyền theo vai trò (chương 10) và cổng mở quyền ghi (nguyên tắc 2).

Hai lớp chặn độc lập, phải qua cả hai mới ghi được:
  1. Vai trò người gọi có quyền ghi trên miền dữ liệu đó không.
  2. Server đó đã chạy đúng 5 mã hàng thật và được mở khoá ghi chưa.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import IntEnum
from pathlib import Path
from typing import Dict, List, Optional

from .errors import PermissionDeniedError, WriteNotAllowedError


class Access(IntEnum):
    NONE = 0
    READ = 1
    DRAFT = 2      # soạn nháp, chưa ghi vào hệ thống nguồn
    WRITE = 3
    APPROVE = 4


#: Chương 10 — hàng là vai trò, cột là miền dữ liệu.
ROLE_MATRIX: Dict[str, Dict[str, Access]] = {
    "merchandiser_owner": {
        "techpack": Access.READ, "drive": Access.WRITE, "mail": Access.DRAFT,
        "erp": Access.DRAFT, "packing": Access.WRITE, "status": Access.READ,
        "sample": Access.WRITE, "compliance": Access.WRITE, "archive": Access.READ,
        "portal": Access.DRAFT, "translate": Access.DRAFT,
    },
    "merchandiser_other": {
        "techpack": Access.READ, "drive": Access.READ, "mail": Access.NONE,
        "erp": Access.READ, "packing": Access.READ, "status": Access.READ,
        "sample": Access.READ, "compliance": Access.READ, "archive": Access.READ,
        "portal": Access.NONE, "translate": Access.DRAFT,
    },
    "bu_lead": {
        "techpack": Access.READ, "drive": Access.WRITE, "mail": Access.READ,
        "erp": Access.APPROVE, "packing": Access.READ, "status": Access.READ,
        "sample": Access.READ, "compliance": Access.APPROVE, "archive": Access.READ,
        "portal": Access.APPROVE, "translate": Access.READ,
    },
    "production": {
        "techpack": Access.NONE, "drive": Access.READ, "mail": Access.NONE,
        "erp": Access.READ, "packing": Access.READ, "status": Access.READ,
        "sample": Access.READ, "compliance": Access.READ, "archive": Access.READ,
        "portal": Access.NONE, "translate": Access.NONE,
    },
    "n8n": {  # tài khoản máy: đọc là chính, chỉ được tạo nháp
        "techpack": Access.READ, "drive": Access.READ, "mail": Access.READ,
        "erp": Access.READ, "packing": Access.DRAFT, "status": Access.READ,
        "sample": Access.READ, "compliance": Access.READ, "archive": Access.READ,
        "portal": Access.NONE, "translate": Access.DRAFT,
    },
    # Người dựng hệ thống không có quyền trên dữ liệu vận hành thật —
    # vừa là chuẩn, vừa bảo vệ chính người dựng khi có sự cố dữ liệu.
    "engineer": {k: Access.NONE for k in (
        "techpack", "drive", "mail", "erp", "packing", "status",
        "sample", "compliance", "archive", "portal", "translate")},
    "engineer_sandbox": {k: Access.APPROVE for k in (
        "techpack", "drive", "mail", "erp", "packing", "status",
        "sample", "compliance", "archive", "portal", "translate")},
}


def access_of(role: str, resource: str) -> Access:
    return ROLE_MATRIX.get(role, {}).get(resource, Access.NONE)


def require(role: str, resource: str, needed: Access) -> None:
    granted = access_of(role, resource)
    if granted < needed:
        raise PermissionDeniedError(
            f"Vai trò '{role}' chỉ có quyền {granted.name} trên '{resource}', cần {needed.name}.",
            hint="Đổi vai trò trong cấu hình phiên, hoặc nhờ người có quyền thực hiện bước này.",
            context={"role": role, "resource": resource,
                     "granted": granted.name, "needed": needed.name},
        )


@dataclass
class WriteGate:
    """Nguyên tắc 2 — mỗi server ra mắt chỉ đọc, mở ghi sau 5 mã hàng chạy đúng."""

    server: str
    unlocked: bool = False
    validated_styles: List[str] = field(default_factory=list)
    unlocked_at: Optional[str] = None
    unlocked_by: Optional[str] = None
    required_styles: int = 5

    def assert_can_write(self, what: str = "") -> None:
        if self.unlocked:
            return
        missing = self.required_styles - len(self.validated_styles)
        raise WriteNotAllowedError(
            f"Server {self.server} đang ở chế độ chỉ đọc{(' — ' + what) if what else ''}.",
            hint=f"Còn thiếu {max(missing, 0)}/{self.required_styles} mã hàng chạy song song "
                 f"khớp kết quả. Ghi nhận bằng `write_gate record`, rồi mở khoá bằng "
                 f"`write_gate unlock {self.server}`.",
            context={"server": self.server, "validated_styles": self.validated_styles},
        )


class WriteGateStore:
    """Lưu trạng thái mở khoá ghi ra data/state/write_gates.json."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def _load(self) -> Dict[str, dict]:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, data: Dict[str, dict]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def get(self, server: str) -> WriteGate:
        raw = self._load().get(server)
        return WriteGate(server=server, **raw) if raw else WriteGate(server=server)

    def record_style(self, server: str, style: str) -> WriteGate:
        """Ghi nhận một mã hàng đã chạy song song và khớp kết quả (bước 5 quy trình dựng)."""
        data = self._load()
        gate = self.get(server)
        if style not in gate.validated_styles:
            gate.validated_styles.append(style)
        data[server] = _gate_payload(gate)
        self._save(data)
        return gate

    def unlock(self, server: str, actor: str) -> WriteGate:
        gate = self.get(server)
        if len(gate.validated_styles) < gate.required_styles:
            raise WriteNotAllowedError(
                f"Chưa đủ điều kiện mở quyền ghi cho {server}: "
                f"{len(gate.validated_styles)}/{gate.required_styles} mã hàng.",
                hint="Chạy song song thêm mã hàng thật và ghi nhận kết quả trước khi mở khoá.",
            )
        gate.unlocked = True
        gate.unlocked_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        gate.unlocked_by = actor
        data = self._load()
        data[server] = _gate_payload(gate)
        self._save(data)
        return gate

    def lock(self, server: str) -> WriteGate:
        """Khoá lại — dùng khi phát hiện sai lệch sau khi đã mở."""
        gate = self.get(server)
        gate.unlocked = False
        data = self._load()
        data[server] = _gate_payload(gate)
        self._save(data)
        return gate


def _gate_payload(gate: WriteGate) -> dict:
    return {
        "unlocked": gate.unlocked,
        "validated_styles": gate.validated_styles,
        "unlocked_at": gate.unlocked_at,
        "unlocked_by": gate.unlocked_by,
        "required_styles": gate.required_styles,
    }
