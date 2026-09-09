"""Tiện ích chung cho kiểm thử: dựng một môi trường tạm có đủ thư mục dữ liệu."""
from __future__ import annotations

import tempfile
from pathlib import Path

from lsth_mcp.core.config import Settings
from lsth_mcp.core.permissions import WriteGateStore


def temp_settings(write_enabled: bool = True, enforce_gate: bool = True) -> Settings:
    root = Path(tempfile.mkdtemp(prefix="lsth-test-"))
    settings = Settings(
        project_root=root,
        config_dir=root / "config",
        data_dir=root / "data",
        raw_dir=root / "data" / "raw",
        work_dir=root / "data" / "work",
        out_dir=root / "data" / "out",
        state_dir=root / "data" / "state",
        audit_dir=root / "data" / "audit",
        templates_dir=root / "data" / "templates",
        identity_dir=root / "data" / "identity",
        eval_dir=root / "data" / "eval",
        write_enabled=write_enabled,
        enforce_write_gate=enforce_gate,
    )
    settings.ensure_dirs()
    return settings


def unlock(settings: Settings, server: str, styles: int = 5) -> None:
    """Mở cổng ghi cho một server bằng đúng con đường thật: ghi nhận 5 mã hàng rồi unlock."""
    store = WriteGateStore(settings.state_dir / "write_gates.json")
    for i in range(styles):
        store.record_style(server, f"STYLE-{i}")
    store.unlock(server, "test")
