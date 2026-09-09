"""Khung chung cho một MCP server nghiệp vụ.

Mỗi server khai báo: mã, tên, miền quyền, vòng triển khai, phụ thuộc và khoảng
trống dữ liệu đang chặn nó. Nhờ vậy `lsth-mcp status` in ra được bức tranh 17
thành phần mà không phải tra tài liệu.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from ..core.audit import AuditLog, CallTrace, audited
from ..core.config import Settings, get_settings
from ..core.envelope import fail, ok
from ..core.errors import LsthError
from ..core.permissions import WriteGateStore
from ..io.writers.safe import SafeWriter


@dataclass
class ServerSpec:
    code: str                      # S1, M3…
    module: str                    # s1_techpack
    name: str                      # lsth-techpack
    purpose: str
    resource: str                  # miền quyền trong ROLE_MATRIX
    group: str                     # "Server v1.0" | "MỚI" | "Nền tảng"
    priority: str                  # Rất cao | Cao | Trung bình | Thấp
    difficulty: str
    round: int                     # vòng triển khai theo lộ trình v2.0
    depends_on: List[str] = field(default_factory=list)
    blocked_by: List[str] = field(default_factory=list)   # G1..G9
    accepted_by: List[str] = field(default_factory=list)  # người nghiệm thu
    tools: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return dict(self.__dict__)


class BaseServer:
    """Lớp cha: lo phần nhật ký, cổng ghi và khung trả về, để tool chỉ còn nghiệp vụ."""

    spec: ServerSpec

    def __init__(self, settings: Optional[Settings] = None,
                 actor: Optional[str] = None, role: Optional[str] = None) -> None:
        self.settings = settings or get_settings()
        self.actor = actor or self.settings.actor
        self.role = role or self.settings.role
        self.audit = AuditLog(self.settings.audit_dir, self.settings.audit_retention_days)
        self.gates = WriteGateStore(self.settings.state_dir / "write_gates.json")

    def writer(self, trace: Optional[CallTrace] = None, *, dry_run: bool = False) -> SafeWriter:
        return SafeWriter.for_server(
            self.spec.module, role=self.role, resource=self.spec.resource,
            settings=self.settings, trace=trace, dry_run=dry_run,
        )

    def call(self, tool: str, params: Dict[str, Any],
             handler: Callable[[CallTrace], Dict[str, Any]]) -> Dict[str, Any]:
        """Chạy một tool: ghi nhật ký 6 trường, bắt lỗi thành envelope chuẩn."""
        full_name = f"{self.spec.name}.{tool}"
        try:
            with audited(self.audit, full_name, params,
                         actor=self.actor, role=self.role) as trace:
                return handler(trace)
        except LsthError as exc:
            return fail(exc)
        except Exception as exc:  # noqa: BLE001 - biên ngoài cùng, không để rò lỗi thô
            return fail(exc)

    def info(self) -> Dict[str, Any]:
        gate = self.gates.get(self.spec.module)
        data = self.spec.to_dict()
        data["write_unlocked"] = gate.unlocked
        data["validated_styles"] = gate.validated_styles
        return ok(data)
