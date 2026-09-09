"""Cấu hình chạy. Đọc từ config/settings.yaml, cho phép biến môi trường đè lên.

Không có bí mật nào nằm trong file này — token và chuỗi kết nối đọc từ môi trường
(xem .env.example).
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

try:  # PyYAML có sẵn trên máy trạm; thiếu thì chạy bằng mặc định
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]

PROJECT_ROOT = Path(__file__).resolve().parents[3]
_ENV_PREFIX = "LSTH_"


@dataclass
class Settings:
    project_root: Path = PROJECT_ROOT
    config_dir: Path = PROJECT_ROOT / "config"
    data_dir: Path = PROJECT_ROOT / "data"

    # Bốn thư mục dữ liệu: đọc vào -> làm việc -> xuất ra, cộng trạng thái/nhật ký.
    raw_dir: Path = PROJECT_ROOT / "data" / "raw"
    work_dir: Path = PROJECT_ROOT / "data" / "work"
    out_dir: Path = PROJECT_ROOT / "data" / "out"
    state_dir: Path = PROJECT_ROOT / "data" / "state"
    audit_dir: Path = PROJECT_ROOT / "data" / "audit"
    templates_dir: Path = PROJECT_ROOT / "data" / "templates"
    identity_dir: Path = PROJECT_ROOT / "data" / "identity"
    eval_dir: Path = PROJECT_ROOT / "data" / "eval"

    #: Nơi chứa file: "local" (thư mục data/) hoặc "minio" (kho object).
    #: Là một trường của Settings chứ không đọc biến môi trường lúc gọi — nếu đọc
    #: env mỗi lần thì một Settings dựng riêng (kiểm thử, hay một phiên khác) sẽ
    #: bị chế độ toàn cục ghi đè, và ghi nhầm chỗ.
    storage: str = "local"

    # Nguyên tắc 2: toàn hệ thống mặc định chỉ đọc.
    write_enabled: bool = False
    enforce_write_gate: bool = True
    backup_on_overwrite: bool = True

    actor: str = "unknown"
    role: str = "engineer"
    transport: str = "stdio"  # stdio cho máy cá nhân, http cho máy chủ nội bộ
    http_host: str = "127.0.0.1"
    http_port: int = 8787
    audit_retention_days: int = 365  # chương 11: giữ tối thiểu 12 tháng

    extra: Dict[str, Any] = field(default_factory=dict)

    @property
    def read_roots(self):
        """Các gốc thư mục được phép đọc. Ngoài danh sách này thì từ chối."""
        return [self.raw_dir, self.work_dir, self.out_dir, self.templates_dir,
                self.identity_dir, self.eval_dir]

    @property
    def write_roots(self):
        """Chỉ ghi vào work/ và out/. Không bao giờ ghi đè lên raw/."""
        return [self.work_dir, self.out_dir, self.state_dir]

    def ensure_dirs(self) -> None:
        for p in [self.raw_dir, self.work_dir, self.out_dir, self.state_dir,
                  self.audit_dir, self.templates_dir, self.identity_dir, self.eval_dir]:
            p.mkdir(parents=True, exist_ok=True)


def _coerce(default: Any, raw: str) -> Any:
    if isinstance(default, bool):
        return raw.strip().lower() in {"1", "true", "yes", "on", "có"}
    if isinstance(default, int):
        return int(raw)
    if isinstance(default, Path):
        return Path(raw).expanduser()
    return raw


def load_settings(config_file: Optional[Path] = None) -> Settings:
    """Thứ tự ưu tiên: biến môi trường > settings.yaml > mặc định."""
    settings = Settings()
    path = config_file or (settings.config_dir / "settings.yaml")
    if yaml is not None and path.exists():
        loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for key, value in loaded.items():
            if not hasattr(settings, key):
                settings.extra[key] = value
                continue
            current = getattr(settings, key)
            setattr(settings, key, Path(value).expanduser() if isinstance(current, Path) else value)

    for key in vars(settings):
        if key == "extra":
            continue
        env_val = os.environ.get(_ENV_PREFIX + key.upper())
        if env_val is not None:
            setattr(settings, key, _coerce(getattr(settings, key), env_val))

    # Đường dẫn tương đối trong yaml tính từ gốc dự án.
    for key in ("raw_dir", "work_dir", "out_dir", "state_dir", "audit_dir",
                "templates_dir", "identity_dir", "eval_dir", "config_dir", "data_dir"):
        value = getattr(settings, key)
        if not value.is_absolute():
            setattr(settings, key, (settings.project_root / value).resolve())
    return settings


_cached: Optional[Settings] = None


def get_settings(reload: bool = False) -> Settings:
    global _cached
    if _cached is None or reload:
        _cached = load_settings()
    return _cached
