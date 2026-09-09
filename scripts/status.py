#!/usr/bin/env python3
"""In bức tranh 17 thành phần: cái nào đã dựng, cái nào đang chờ lấp khoảng trống.

    PYTHONPATH=src python3 scripts/status.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lsth_mcp.core.config import get_settings          # noqa: E402
from lsth_mcp.core.permissions import WriteGateStore   # noqa: E402
from lsth_mcp.domain.templates import TemplateStore    # noqa: E402
from lsth_mcp.servers import ALL_SPECS, FOUNDATION     # noqa: E402

ROUND_LABELS = {
    0: "Vòng 0 · tuần 1–2 · không dựng gì",
    1: "Vòng 1 · tuần 2–5",
    2: "Vòng 2 · tuần 5–9",
    3: "Vòng 3 · tuần 9–13",
    4: "Vòng 4 · tuần 13–18",
    5: "Vòng 5 · sau khi có thoả thuận khách",
}


def main() -> int:
    cfg = get_settings()
    gates = WriteGateStore(cfg.state_dir / "write_gates.json")

    print("=" * 78)
    print("LSTH · CHƯƠNG TRÌNH GIẢM WORKLOAD KHỐI BU — 17 THÀNH PHẦN")
    print("=" * 78)
    print(f"Chế độ ghi toàn hệ thống: {'MỞ' if cfg.write_enabled else 'ĐÓNG (chỉ đọc)'}"
          f"   ·   Vai trò: {cfg.role}")

    print("\nNHÓM 3 — NĂM THÀNH PHẦN NỀN (phải có trước)")
    for item in FOUNDATION:
        print(f"  {item['code']}  {item['name']:<32} {item['module']}")

    print("\nMƯỜI HAI SERVER NGHIỆP VỤ")
    for round_number in sorted({s.round for s in ALL_SPECS}):
        print(f"\n  {ROUND_LABELS.get(round_number, f'Vòng {round_number}')}")
        for spec in [s for s in ALL_SPECS if s.round == round_number]:
            gate = gates.get(spec.module)
            write_state = "ghi: MỞ" if gate.unlocked else \
                f"ghi: đóng ({len(gate.validated_styles)}/5 mã)"
            blocked = ("CHẶN: " + ",".join(spec.blocked_by)) if spec.blocked_by else "sẵn sàng"
            print(f"    {spec.code:<3} {spec.name:<22} {spec.priority:<12} "
                  f"{blocked:<14} {write_state}")

    store = TemplateStore.load(cfg.templates_dir)
    missing = store.missing_kinds()
    print("\nF4 · KHO KHUÔN")
    print(f"  Đã có: {', '.join(store.kinds()) or '(chưa có gì)'}")
    if missing:
        print(f"  CÒN THIẾU: {', '.join(missing)}  <- khoảng trống G4, chặn S6, M1, M3")

    identity = cfg.identity_dir / "identity_map.csv"
    print("\nF3 · BẢNG ÁNH XẠ ĐỊNH DANH")
    if identity.exists():
        from lsth_mcp.domain.identity import IdentityMap
        print(f"  {IdentityMap.load(identity).coverage()}")
    else:
        print("  CHƯA CÓ  <- chép từ identity_map.example.csv rồi điền (khoảng trống G9)")

    print("\nBỐN VIỆC ĐỀ NGHỊ LÀM TRONG TUẦN NÀY")
    for index, task in enumerate([
        "Gọi nhà cung cấp ERP: hỏi API + yêu cầu sửa 2 lỗi BOM/định mức (lấp G1 + vòng 0)",
        "Xin mỗi loại một file khuôn đã duyệt: TLĐG, WS, BOM, TUV, FDW (lấp G4)",
        "Lập bảng 9 cổng khách: ai có tài khoản, có nút export không (lấp G2)",
        "Đặt lịch ngồi cùng 4 người cho 4 đầu việc nặng chưa có bản ghi thao tác (lấp G6)",
    ], start=1):
        print(f"  {index}. {task}")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
