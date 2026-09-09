"""Trừu tượng hoá nơi chứa file.

Cùng một reader phải đọc được dù file nằm trên đĩa hay trong MinIO. Lớp này giấu
sự khác biệt đó đi, và giữ hai điều quan trọng không đổi:

- Nguyên tắc 4 — mỗi object có một URI ổn định (`s3://lsth-raw/BOM.xlsx`) dùng
  làm nguồn, để câu trả lời vẫn dẫn về đúng chỗ.
- Nguyên tắc 2 và 8 — vùng nào chỉ đọc thì chỉ đọc, ở cả tầng lưu trữ.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Protocol

from ...core.errors import ValidationError

#: Tên thành phần bị cấm trong key — chặn đường dẫn đi ra ngoài bucket.
_FORBIDDEN_PARTS = {"..", ""}


@dataclass(frozen=True)
class ObjectInfo:
    key: str
    size: int
    last_modified: Optional[datetime] = None
    etag: Optional[str] = None
    bucket: Optional[str] = None

    @property
    def name(self) -> str:
        return self.key.rsplit("/", 1)[-1]

    @property
    def suffix(self) -> str:
        return Path(self.key).suffix.lower()


def check_key(key: str) -> str:
    """Chặn đường dẫn đi ra ngoài bucket. Tương đương resolve_within của bản đĩa."""
    key = str(key or "").strip()
    while key.startswith("./"):
        key = key[2:]
    key = key.lstrip("/")
    if not key:
        raise ValidationError(
            "Tên object rỗng.",
            hint="Truyền tên file, ví dụ 'BOM_66P866.xlsx' hoặc 'S27/BOM_66P866.xlsx'.",
        )
    if "\x00" in key:
        raise ValidationError(
            "Tên object chứa ký tự rỗng.",
            hint="Đặt lại tên file, chỉ dùng chữ, số, gạch và dấu chấm.",
        )
    parts = key.split("/")
    if any(part in _FORBIDDEN_PARTS for part in parts):
        raise ValidationError(
            f"Tên object không hợp lệ: {key!r}",
            hint="Không dùng '..' hay dấu gạch chéo thừa — chỉ tên file trong bucket.",
        )
    return key


class ObjectStore(Protocol):
    """Giao diện tối thiểu mà mọi nơi chứa file phải có."""

    name: str
    writable: bool

    def uri(self, key: str) -> str: ...
    def exists(self, key: str) -> bool: ...
    def stat(self, key: str) -> ObjectInfo: ...
    def list(self, prefix: str = "", limit: int = 200) -> List[ObjectInfo]: ...
    def get_bytes(self, key: str) -> bytes: ...
    def download(self, key: str, dest: Path) -> Path: ...
    def put_bytes(self, key: str, data: bytes,
                  content_type: str = "application/octet-stream") -> ObjectInfo: ...


#: Đuôi file -> content type, để object tải về từ console MinIO mở đúng ứng dụng.
CONTENT_TYPES = {
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".xlsm": "application/vnd.ms-excel.sheet.macroEnabled.12",
    ".pdf": "application/pdf",
    ".csv": "text/csv; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".jsonl": "application/x-ndjson; charset=utf-8",
    ".txt": "text/plain; charset=utf-8",
    ".md": "text/markdown; charset=utf-8",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def content_type_for(key: str) -> str:
    return CONTENT_TYPES.get(Path(key).suffix.lower(), "application/octet-stream")
