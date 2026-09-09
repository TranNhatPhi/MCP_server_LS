"""Ràng buộc đường dẫn và quy ước đặt tên file (F4).

Hai việc:
1. Không cho tool đọc/ghi ra ngoài các gốc đã khai báo — chặn cả đường dẫn kiểu ../..
2. Sinh và kiểm tên file theo quy ước chung, để ổ chung thôi mỗi người một kiểu (G5).
"""
from __future__ import annotations

import re
import unicodedata
from datetime import date
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from .errors import PathOutsideRootError, ValidationError

_SAFE_CHARS = re.compile(r"[^A-Za-z0-9._-]+")


def resolve_within(path: Any, roots: Iterable[Path], *, must_exist: bool = False) -> Path:
    """Trả về đường dẫn tuyệt đối, đảm bảo nằm trong một trong các gốc cho phép."""
    roots = [Path(r).resolve() for r in roots]
    candidate = Path(path).expanduser()
    if not candidate.is_absolute():
        candidate = (roots[0] / candidate) if roots else candidate.resolve()
    candidate = candidate.resolve()

    for root in roots:
        try:
            candidate.relative_to(root)
        except ValueError:
            continue
        if must_exist and not candidate.exists():
            cand_str = str(candidate)
            found = None
            for norm in [unicodedata.normalize("NFD", cand_str), unicodedata.normalize("NFC", cand_str)]:
                p_norm = Path(norm)
                if p_norm.exists():
                    found = p_norm
                    break
            if found is not None:
                return found
            raise ValidationError(
                f"Không thấy file: {candidate}",
                hint="Kiểm tra lại tên file, hoặc chép file vào data/raw trước khi gọi lại.",
            )
        return candidate

    raise PathOutsideRootError(
        f"Đường dẫn nằm ngoài vùng cho phép: {candidate}",
        hint="Chỉ đọc/ghi trong các thư mục đã khai báo ở config/settings.yaml "
             "(data/raw, data/work, data/out, data/templates).",
        context={"roots": [str(r) for r in roots]},
    )


def slugify(text: str, *, keep_case: bool = True) -> str:
    """Bỏ dấu tiếng Việt và ký tự lạ để tên file an toàn trên mọi ổ đĩa."""
    normalized = unicodedata.normalize("NFKD", str(text))
    ascii_text = "".join(c for c in normalized if not unicodedata.combining(c))
    ascii_text = ascii_text.replace("đ", "d").replace("Đ", "D")
    cleaned = _SAFE_CHARS.sub("-", ascii_text).strip("-_.")
    return cleaned if keep_case else cleaned.lower()


def render_name(pattern: str, context: Dict[str, Any], *, today: Optional[date] = None) -> str:
    """Sinh tên file theo mẫu, ví dụ "{style}_{market}_TLDG_v{rev}.xlsx".

    Thiếu biến nào thì báo rõ biến đó, không tự điền chuỗi rỗng (nguyên tắc 5).
    """
    ctx = dict(context)
    ctx.setdefault("date", (today or date.today()).isoformat())
    try:
        rendered = pattern.format(**{k: slugify(v) if isinstance(v, str) else v
                                     for k, v in ctx.items()})
    except KeyError as exc:
        raise ValidationError(
            f"Mẫu tên file thiếu biến {exc}.",
            hint=f"Truyền thêm {exc} hoặc sửa mẫu trong config/naming.yaml.",
            context={"pattern": pattern, "given": sorted(ctx)},
        ) from exc
    return rendered


def check_name(name: str, pattern: Optional[str] = None) -> bool:
    """Kiểm tên file có khớp biểu thức quy ước không (dùng khi rà soát ổ chung)."""
    if pattern is None:
        return bool(name) and name == slugify(name)
    return re.fullmatch(pattern, name) is not None


def timestamped(path: Path, stamp: str) -> Path:
    """`bom.xlsx` + `20260909-1030` -> `bom.20260909-1030.xlsx` (dùng cho bản sao lưu)."""
    return path.with_name(f"{path.stem}.{stamp}{path.suffix}")
