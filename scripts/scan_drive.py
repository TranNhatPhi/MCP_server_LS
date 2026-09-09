#!/usr/bin/env python3
"""Lấp khoảng trống G5 — chụp lại hiện trạng ổ chung trước khi chuẩn hoá.

Tài liệu v2.0 nói rõ: "Hiện mỗi người một kiểu. Cần chụp lại hiện trạng rồi mới
chuẩn hoá được." Script này đi 2 ngày công đó trong vài giây: đếm file theo đuôi,
gom các kiểu đặt tên đang dùng, và chỉ ra tên nào lệch quy ước.

    python3 scripts/scan_drive.py "/đường/dẫn/ổ/chung" --out data/work/g5_hien_trang.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lsth_mcp.core.paths import slugify   # noqa: E402


def shape_of(name: str) -> str:
    """"66P866_US_TLDG_v2.xlsx" -> "A_A_A_vN.xlsx" — để gom các kiểu đặt tên."""
    stem = Path(name).stem
    parts = re.split(r"[ _\-.]+", stem)
    shaped = []
    for part in parts:
        if re.fullmatch(r"v\d+", part, re.I):
            shaped.append("vN")
        elif part.isdigit():
            shaped.append("N")
        elif re.fullmatch(r"[A-Za-z]+\d+[A-Za-z0-9]*", part):
            shaped.append("CODE")
        else:
            shaped.append("A")
    return "_".join(shaped) + Path(name).suffix.lower()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", help="thư mục ổ chung cần chụp hiện trạng")
    parser.add_argument("--out", default="", help="ghi kết quả ra file JSON")
    parser.add_argument("--top", type=int, default=25)
    args = parser.parse_args()

    root = Path(args.root).expanduser()
    if not root.exists():
        print(f"Không thấy thư mục: {root}", file=sys.stderr)
        return 1

    suffixes: Counter = Counter()
    shapes: Counter = Counter()
    depths: Counter = Counter()
    odd_names = []
    total = 0

    for path in root.rglob("*"):
        if not path.is_file() or path.name.startswith((".", "~$")):
            continue
        total += 1
        suffixes[path.suffix.lower()] += 1
        shapes[shape_of(path.name)] += 1
        depths[len(path.relative_to(root).parts) - 1] += 1
        if path.stem != slugify(path.stem) and len(odd_names) < 200:
            odd_names.append(str(path.relative_to(root)))

    report = {
        "root": str(root),
        "file_count": total,
        "by_suffix": suffixes.most_common(),
        "naming_shapes": shapes.most_common(args.top),
        "depth_histogram": sorted(depths.items()),
        "names_needing_normalisation": odd_names,
        "distinct_naming_shapes": len(shapes),
    }

    print(f"Đã quét {total} file trong {root}")
    print(f"Số kiểu đặt tên khác nhau: {len(shapes)}  "
          f"(càng nhiều càng khẳng định 'mỗi người một kiểu')")
    print("\nMười kiểu đặt tên phổ biến nhất:")
    for shape, count in shapes.most_common(10):
        print(f"  {count:>5}  {shape}")
    print(f"\n{len(odd_names)} tên file có dấu hoặc ký tự cần chuẩn hoá.")

    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nĐã ghi báo cáo: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
