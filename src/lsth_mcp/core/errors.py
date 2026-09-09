"""Cây lỗi dùng chung.

Nguyên tắc 5 — "Hỏng thì im lặng, không đoán": mọi lỗi phải dừng luồng, không
được trả về giá trị suy đoán. Chuẩn kỹ thuật chương 15 — thông báo lỗi phải nói
được người dùng cần làm gì tiếp theo, nên `hint` là phần bắt buộc về mặt quy ước.
"""
from __future__ import annotations

from typing import Any, Dict, Optional


class LsthError(Exception):
    """Lỗi gốc. Mọi lỗi nghiệp vụ của hệ thống đều kế thừa từ đây."""

    code = "lsth_error"

    def __init__(
        self,
        message: str,
        *,
        hint: Optional[str] = None,
        source: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.hint = hint
        self.source = source
        self.context = context or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "hint": self.hint,
            "source": self.source,
            "context": self.context or None,
        }

    def __str__(self) -> str:  # pragma: no cover - chỉ để đọc log cho dễ
        return f"{self.message} — {self.hint}" if self.hint else self.message


class NotFoundError(LsthError):
    """Tra không ra. Không được thay bằng giá trị mặc định."""

    code = "not_found"


class SourceMissingError(LsthError):
    """Nguyên tắc 4 — có giá trị nhưng không dẫn được nguồn thì coi như không có."""

    code = "source_missing"


class ConflictError(LsthError):
    """Nguyên tắc 3 — hai nguồn nói khác nhau. Server báo mâu thuẫn, không tự chọn."""

    code = "conflict"

    def __init__(self, message: str, *, candidates: Any = None, **kw: Any) -> None:
        super().__init__(message, **kw)
        self.context["candidates"] = candidates


class ValidationError(LsthError):
    code = "validation_error"


class UnsupportedFormatError(LsthError):
    code = "unsupported_format"


class PermissionDeniedError(LsthError):
    """Ma trận quyền theo vai trò — chương 10 kiến trúc v1.0."""

    code = "permission_denied"


class WriteNotAllowedError(LsthError):
    """Nguyên tắc 2 — "Đọc trước, ghi sau". Quyền ghi mở sau 5 mã hàng chạy đúng."""

    code = "write_not_allowed"


class ZoneViolationError(LsthError):
    """Nguyên tắc 6 — "Dữ liệu ở đâu, xử lý ở đó"."""

    code = "zone_violation"


class PathOutsideRootError(LsthError):
    code = "path_outside_root"


class NotImplementedYetError(LsthError):
    """Hợp đồng tool đã chốt nhưng chưa dựng, thường vì còn chặn ở một khoảng trống dữ liệu.

    Luôn kèm mã khoảng trống (G1..G9) để người gọi biết phải lấp gì trước.
    """

    code = "not_implemented_yet"

    def __init__(self, tool: str, *, blocked_by: str = "", hint: str = "") -> None:
        super().__init__(
            f"Tool {tool} chưa dựng.",
            hint=hint or f"Chặn bởi {blocked_by}. Xem docs/DATA_GAPS.md.",
            context={"tool": tool, "blocked_by": blocked_by},
        )
