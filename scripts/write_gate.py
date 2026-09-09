#!/usr/bin/env python3
"""Quản lý cổng quyền ghi — nguyên tắc 2 "Đọc trước, ghi sau".

    python3 scripts/write_gate.py list
    python3 scripts/write_gate.py record s2_erp 66P866    # ghi nhận 1 mã chạy đúng
    python3 scripts/write_gate.py unlock s2_erp           # mở khi đủ 5 mã
    python3 scripts/write_gate.py lock s2_erp             # khoá lại khi phát hiện lệch
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lsth_mcp.core.config import get_settings          # noqa: E402
from lsth_mcp.core.errors import LsthError             # noqa: E402
from lsth_mcp.core.permissions import WriteGateStore   # noqa: E402
from lsth_mcp.servers import ALL_SPECS                 # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    for name in ("record", "unlock", "lock"):
        p = sub.add_parser(name)
        p.add_argument("server")
        if name == "record":
            p.add_argument("style", help="mã hàng đã chạy song song và khớp kết quả")
    args = parser.parse_args()

    cfg = get_settings()
    store = WriteGateStore(cfg.state_dir / "write_gates.json")

    try:
        if args.cmd == "list":
            for spec in ALL_SPECS:
                gate = store.get(spec.module)
                mark = "MỞ " if gate.unlocked else "đóng"
                print(f"  {mark}  {spec.module:<16} {len(gate.validated_styles)}/5 mã"
                      f"  {', '.join(gate.validated_styles)}")
            return 0

        if args.cmd == "record":
            gate = store.record_style(args.server, args.style)
            print(f"Đã ghi nhận {args.style}. Hiện {len(gate.validated_styles)}/5 mã.")
            if len(gate.validated_styles) >= gate.required_styles:
                print(f"Đủ điều kiện — chạy: python3 scripts/write_gate.py unlock {args.server}")
            return 0

        if args.cmd == "unlock":
            gate = store.unlock(args.server, cfg.actor)
            print(f"Đã mở quyền ghi cho {args.server} bởi {gate.unlocked_by}.")
            print("Nhắc: nguyên tắc 8 — vẫn phải giữ được đường làm tay khi hệ thống hỏng.")
            return 0

        store.lock(args.server)
        print(f"Đã khoá lại quyền ghi của {args.server}.")
        return 0
    except LsthError as exc:
        print(f"LỖI: {exc.message}\n  -> {exc.hint}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
