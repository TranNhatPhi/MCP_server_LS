"""LSTH MCP — hệ thống MCP server giảm workload khối BU của Lucky Star.

Dựng theo tài liệu hợp nhất v2.0 (09/09/2026) và tài liệu kiến trúc v1.0 (08/09/2026).

Bố cục:
    core/     — lớp nền: mô hình dữ liệu, nguồn gốc dữ liệu, quyền, vùng, nhật ký
    io/       — module đọc và module ghi
    domain/   — F3 ánh xạ định danh, F4 kho khuôn, F5 bộ đánh giá
    servers/  — 12 server nghiệp vụ (S1–S7, M1–M5)
    server.py — F1 cổng điều phối, điểm vào MCP
"""
from .core.config import get_settings

__version__ = "0.1.0"
__all__ = ["get_settings", "__version__"]
