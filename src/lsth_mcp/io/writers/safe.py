"""SafeWriter — cửa ghi duy nhất của hệ thống.

Mọi thao tác ghi đi qua đây để bốn ràng buộc luôn được áp cùng lúc:

1. Nguyên tắc 2 "Đọc trước, ghi sau" — WriteGate của server phải đã mở khoá.
2. Chỉ ghi trong data/work và data/out. Không bao giờ đè lên data/raw (file gốc
   của khách và của merchandiser).
3. Ghi nguyên tử: viết ra file tạm rồi đổi tên, để không bao giờ để lại file
   nửa vời khi máy tắt giữa chừng.
4. Ghi đè thì sao lưu bản cũ trước — nguyên tắc 8 "luôn giữ được đường làm tay".

Nguyên tắc 1 "Máy soạn nháp, người bấm nút" thể hiện ở chỗ: SafeWriter chỉ ghi
được xuống ổ đĩa nội bộ. Không có hàm nào ở đây gửi mail, đặt hàng hay đẩy dữ
liệu ra hệ thống khách.
"""
from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Iterable, Optional

from ...core.audit import CallTrace
from ...core.config import Settings, get_settings
from ...core.errors import ValidationError, WriteNotAllowedError
from ...core.paths import resolve_within, timestamped
from ...core.permissions import Access, WriteGate, WriteGateStore, require
from ...core.provenance import Source
from ..base import WriteResult

#: Đuôi file không cho phép ghi — tránh biến thư mục dữ liệu thành nơi chạy mã.
_BLOCKED_SUFFIXES = {".exe", ".sh", ".bat", ".cmd", ".ps1", ".dll", ".so"}


@dataclass
class SafeWriter:
    """Bộ ghi có kiểm soát, gắn với một server cụ thể.

    Ví dụ::

        writer = SafeWriter.for_server("s2_erp", role="merchandiser_owner",
                                       resource="erp")
        writer.write_text("bom_draft.txt", "…")   # WriteNotAllowedError nếu chưa mở khoá
    """

    server: str
    settings: Settings
    gate: WriteGate
    role: str = "engineer"
    resource: Optional[str] = None
    trace: Optional[CallTrace] = None
    dry_run: bool = False

    @classmethod
    def for_server(
        cls,
        server: str,
        *,
        role: str = "engineer",
        resource: Optional[str] = None,
        settings: Optional[Settings] = None,
        trace: Optional[CallTrace] = None,
        dry_run: bool = False,
    ) -> "SafeWriter":
        cfg = settings or get_settings()
        gate = WriteGateStore(cfg.state_dir / "write_gates.json").get(server)
        return cls(server=server, settings=cfg, gate=gate, role=role,
                   resource=resource, trace=trace, dry_run=dry_run)

    # ---- kiểm tra trước khi ghi -------------------------------------------------

    def _authorize(self, path: Path, what: str) -> Path:
        self._authorize_common(what)
        target = resolve_within(path, self.settings.write_roots)
        if target.suffix.lower() in _BLOCKED_SUFFIXES:
            raise ValidationError(
                f"Không ghi file đuôi {target.suffix}.",
                hint="Thư mục dữ liệu chỉ chứa tài liệu, không chứa file chạy được.",
            )
        return target

    def _backup(self, target: Path) -> Optional[Path]:
        if not target.exists() or not self.settings.backup_on_overwrite:
            return None
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_dir = target.parent / "_backup"
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup = backup_dir / timestamped(target, stamp).name
        backup.write_bytes(target.read_bytes())
        return backup

    def _atomic(self, target: Path, payload: Callable[[Path], None]) -> int:
        """Ghi qua file tạm cùng thư mục rồi os.replace — đổi tên trong cùng ổ là nguyên tử."""
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(dir=str(target.parent), prefix=".tmp-",
                                        suffix=target.suffix)
        os.close(fd)
        tmp = Path(tmp_name)
        try:
            payload(tmp)
            size = tmp.stat().st_size
            os.replace(tmp, target)
            return size
        except BaseException:
            tmp.unlink(missing_ok=True)
            raise

    def _finish(self, target: Path, size: int, backup: Optional[Path],
                existed: bool, rows: int = 0) -> WriteResult:
        if self.trace:
            self.trace.wrote(target)
        return WriteResult(
            path=target, bytes_written=size, rows_written=rows,
            backup_path=backup, created=not existed,
            source=Source(file=str(target), note=f"do {self.server} dựng"),
        )

    # ---- các hàm ghi ------------------------------------------------------------

    def _authorize_common(self, what: str) -> None:
        """Phần kiểm tra không phụ thuộc nơi chứa: công tắc chung, cổng ghi, vai trò."""
        if not self.settings.write_enabled:
            raise WriteNotAllowedError(
                "Toàn hệ thống đang ở chế độ chỉ đọc.",
                hint="Bật LSTH_WRITE_ENABLED=true (hoặc write_enabled: true trong "
                     "config/settings.yaml) khi đã sẵn sàng cho phép ghi.",
                context={"server": self.server},
            )
        if self.settings.enforce_write_gate:
            self.gate.assert_can_write(what)
        if self.resource:
            require(self.role, self.resource, Access.WRITE)

    def write_object(self, key: str, data: bytes, *, area: str = "out",
                     what: str = "") -> WriteResult:
        """Ghi lên MinIO. Cùng cổng kiểm soát như ghi xuống đĩa.

        Bucket đích còn bị MinIO chặn thêm một lớp: tài khoản ứng dụng không có
        quyền ghi vào lsth-raw, lsth-templates hay lsth-identity.
        """
        from ..storage import get_store

        self._authorize_common(what)
        store = get_store(area, self.settings)
        existed = store.exists(key)
        if self.dry_run:
            return WriteResult(path=Path(store.uri(key)), bytes_written=len(data),
                               created=not existed,
                               source=Source(file=store.uri(key),
                                             note=f"do {self.server} dựng"))
        info = store.put_bytes(key, data)
        uri = store.uri(info.key)
        if self.trace:
            self.trace.wrote(uri)
        return WriteResult(
            path=Path(uri), bytes_written=info.size, created=not existed,
            # Không cần sao lưu tay: bucket ghi được đã bật versioning, bản cũ
            # vẫn lấy lại được (nguyên tắc 8).
            backup_path=None,
            source=Source(file=uri, note=f"do {self.server} dựng"),
        )

    def write_bytes(self, path: Any, data: bytes, *, what: str = "") -> WriteResult:
        from ..storage import parse_uri, using_minio

        parsed = parse_uri(str(path)) if str(path).startswith("s3://") else None
        if parsed:
            area, key = parsed
            return self.write_object(key, data, area=area, what=what)
        if using_minio(self.settings):
            # Ở chế độ MinIO, đường dẫn trần được hiểu là object trong lsth-out.
            return self.write_object(str(path).lstrip("/"), data, area="out", what=what)

        target = self._authorize(Path(path), what)
        existed = target.exists()
        if self.dry_run:
            return self._finish(target, len(data), None, existed)
        backup = self._backup(target)
        size = self._atomic(target, lambda tmp: tmp.write_bytes(data))
        return self._finish(target, size, backup, existed)

    def write_text(self, path: Any, text: str, *, encoding: str = "utf-8",
                   what: str = "") -> WriteResult:
        return self.write_bytes(path, text.encode(encoding), what=what)

    def write_with(self, path: Any, payload: Callable[[Path], None], *,
                   what: str = "", rows: int = 0) -> WriteResult:
        """Cho thư viện ngoài (openpyxl…) tự ghi vào file tạm, vẫn giữ tính nguyên tử.

        Ở chế độ MinIO: thư viện ghi ra file tạm, xong mới đẩy nguyên khối lên kho.
        """
        from ..storage import parse_uri, using_minio

        if using_minio(self.settings) or str(path).startswith("s3://"):
            import tempfile

            parsed = parse_uri(str(path)) if str(path).startswith("s3://") else None
            area, key = parsed if parsed else ("out", str(path).lstrip("/"))
            self._authorize_common(what)
            with tempfile.TemporaryDirectory(prefix="lsth-put-") as tmpdir:
                tmp = Path(tmpdir) / Path(key).name
                payload(tmp)
                result = self.write_object(key, tmp.read_bytes(), area=area, what=what)
            result.rows_written = rows
            return result

        target = self._authorize(Path(path), what)
        existed = target.exists()
        if self.dry_run:
            return self._finish(target, 0, None, existed, rows)
        backup = self._backup(target)
        size = self._atomic(target, payload)
        return self._finish(target, size, backup, existed, rows)

    def copy_from(self, source_path: Any, dest_path: Any, *, what: str = "") -> WriteResult:
        """Chép file khuôn từ data/templates sang vùng làm việc rồi mới điền (F4)."""
        src = resolve_within(source_path, self.settings.read_roots, must_exist=True)
        if self.trace:
            self.trace.read(src)
        return self.write_bytes(dest_path, src.read_bytes(), what=what or f"chép từ {src.name}")
