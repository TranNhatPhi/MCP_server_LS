"""Nhật ký và khả năng truy vết — chương 11 kiến trúc v1.0.

Mỗi lệnh gọi ghi đúng sáu thông tin: ai gọi, lúc nào, tool nào, tham số gì,
đọc những file nào, kết quả thành công hay lỗi. Ghi thêm file đã ghi ra và thời
gian chạy vì hai thứ đó gần như miễn phí mà rất cần khi truy sự cố.

Định dạng JSONL, mỗi ngày một file, giữ tối thiểu 12 tháng.
"""
from __future__ import annotations

import json
import os
import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

_MAX_PARAM_LEN = 500


@dataclass
class AuditRecord:
    actor: str
    ts: str
    tool: str
    params: Dict[str, Any]
    files_read: List[str] = field(default_factory=list)
    files_written: List[str] = field(default_factory=list)
    ok: bool = True
    error: Optional[str] = None
    duration_ms: int = 0
    role: Optional[str] = None


def _redact(params: Dict[str, Any]) -> Dict[str, Any]:
    """Không ghi nội dung file hay bí mật vào nhật ký — chỉ ghi đủ để tái hiện lệnh gọi."""
    out: Dict[str, Any] = {}
    for key, value in (params or {}).items():
        if any(s in key.lower() for s in ("password", "token", "secret", "api_key")):
            out[key] = "***"
        elif isinstance(value, (str, bytes)) and len(value) > _MAX_PARAM_LEN:
            out[key] = f"<{len(value)} ký tự đã lược>"
        elif isinstance(value, (list, tuple)) and len(value) > 20:
            out[key] = f"<{len(value)} phần tử>"
        else:
            out[key] = value
    return out


class AuditLog:
    def __init__(self, directory: Path, retention_days: int = 365) -> None:
        self.directory = Path(directory)
        self.retention_days = retention_days

    def _file_for(self, when: datetime) -> Path:
        return self.directory / f"calls-{when.strftime('%Y-%m')}.jsonl"

    def write(self, record: AuditRecord) -> Path:
        self.directory.mkdir(parents=True, exist_ok=True)
        path = self._file_for(datetime.now(timezone.utc))
        line = json.dumps(asdict(record), ensure_ascii=False)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
            fh.flush()
            os.fsync(fh.fileno())
        return path

    def tail(self, limit: int = 50) -> List[Dict[str, Any]]:
        files = sorted(self.directory.glob("calls-*.jsonl"))
        rows: List[Dict[str, Any]] = []
        for path in reversed(files):
            lines = path.read_text(encoding="utf-8").splitlines()
            for line in reversed(lines):
                if line.strip():
                    rows.append(json.loads(line))
                if len(rows) >= limit:
                    return rows
        return rows

    def iter_records(self) -> Iterator[Dict[str, Any]]:
        for path in sorted(self.directory.glob("calls-*.jsonl")):
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    yield json.loads(line)

    def prune(self) -> List[Path]:
        """Xoá file nhật ký quá hạn giữ. Mặc định giữ 12 tháng."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.retention_days)
        removed: List[Path] = []
        for path in self.directory.glob("calls-*.jsonl"):
            try:
                stamp = datetime.strptime(path.stem.replace("calls-", ""), "%Y-%m")
            except ValueError:
                continue
            if stamp.replace(tzinfo=timezone.utc) < cutoff.replace(day=1):
                path.unlink()
                removed.append(path)
        return removed


@dataclass
class CallTrace:
    """Sổ tay của một lệnh gọi: tool tự khai đã đọc/ghi file nào."""

    files_read: List[str] = field(default_factory=list)
    files_written: List[str] = field(default_factory=list)

    def read(self, path: Any) -> None:
        p = str(path)
        if p not in self.files_read:
            self.files_read.append(p)

    def wrote(self, path: Any) -> None:
        p = str(path)
        if p not in self.files_written:
            self.files_written.append(p)


@contextmanager
def audited(
    log: AuditLog,
    tool: str,
    params: Dict[str, Any],
    *,
    actor: str = "unknown",
    role: Optional[str] = None,
) -> Iterator[CallTrace]:
    """Bọc một lệnh gọi tool. Lỗi vẫn được ghi rồi ném tiếp — không nuốt lỗi."""
    trace = CallTrace()
    started = time.perf_counter()
    error: Optional[str] = None
    try:
        yield trace
    except Exception as exc:
        error = f"{exc.__class__.__name__}: {exc}"
        raise
    finally:
        log.write(AuditRecord(
            actor=actor,
            role=role,
            ts=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            tool=tool,
            params=_redact(params),
            files_read=trace.files_read,
            files_written=trace.files_written,
            ok=error is None,
            error=error,
            duration_ms=int((time.perf_counter() - started) * 1000),
        ))
