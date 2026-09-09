#!/usr/bin/env python3
"""Sinh dữ liệu GIẢ để thử hệ thống — không dùng file khách thật.

Tech pack và BOM thật thuộc vùng Z3 (NDA). Chừng nào khoảng trống G8 chưa lấp
(rà điều khoản bảo mật của 5 khách) thì mọi buổi thử có nối ra dịch vụ ngoài đều
phải chạy trên dữ liệu giả.

    python3 scripts/make_demo_data.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lsth_mcp.core.config import get_settings   # noqa: E402

BRANDS = [("GA", "S2749189"), ("HA", "66P866")]
MATERIALS = [
    ("FB-K0007-HD", "HADDADCORE-06, HEATHER", "FB", 0.216, "YD", 1.38, "HENGDA", 1.0),
    ("TR-0021-BK", "THREAD 40/2 BLACK", "TR", 1.500, "PCS", 0.03, "COATS", 0.0),
    ("LB-MAIN-001", "MAIN LABEL WOVEN", "LB", 1.000, "PCS", 0.05, "TRIMCO", 2.0),
    ("PB-0035", "POLYBAG 300x400", "PB", 1.000, "PCS", 0.02, "NAMVIET", 3.0),
    ("HT-0012", "HANGTAG 60x90", "HT", 1.000, "PCS", 0.04, "TRIMCO", 1.0),
]
COLORS = [("U89", "GAME ROYAL"), ("042", "DK GREY HEATHER")]
SIZES = ["2T", "3T", "4T", "5T"]


def make_bom(path: Path) -> int:
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.title = "BOM"
    headers = ["Item No", "Style", "Color Garment Code", "Color Garment Name",
               "Material Code", "Description", "Color Code", "Color Name",
               "Garment Size", "Consumption", "Unit BOM", "Position",
               "Material Class", "Price", "Currency", "Vendor Code",
               "Lead Time", "Wastage %", "Less %", "Over %"]
    ws.append(headers)

    item = 1000
    for _, style in BRANDS[:1]:
        for ccode, cname in COLORS:
            for size in SIZES:
                for code, desc, cls, cons, uom, price, vendor, waste in MATERIALS:
                    item += 1
                    ws.append([str(item), style, ccode, cname, code, desc,
                               ccode, cname, size, cons, uom, "BODY", cls,
                               price, "USD", vendor, 60, waste, 0.0, 3.0])
    # Một dòng cố ý thiếu dữ liệu, để thấy máy báo "cần người điền" chứ không đoán.
    ws.append([str(item + 1), "S2749189", "U89", "GAME ROYAL", "", "CHUA CO MA",
               "U89", "GAME ROYAL", "2T", None, "PCS", "BODY", "XX",
               None, "USD", "", None, None, None, None])
    wb.save(path)
    return ws.max_row - 1


def make_techpack(path: Path) -> int:
    """PDF giả tối thiểu, viết tay theo đặc tả PDF 1.4 để không cần thư viện ngoài."""
    lines = [
        "LUCKY STAR - DEMO TECH PACK (DU LIEU GIA)",
        "STYLE: S2749189    SEASON: S27",
        "CUSTOMER: GARAN    MARKET: US",
        "COLORS: U89 GAME ROYAL / 042 DK GREY HEATHER",
        "SIZES: 2T 3T 4T 5T",
        "BODY: 100% COTTON JERSEY 150 GSM",
        "HANGTAG POSITION: LEFT SLEEVE SEAM",
    ]
    stream = "BT /F1 11 Tf 40 750 Td 16 TL\n" + "\n".join(
        f"({t}) Tj T*" for t in lines) + "\nET"
    objs = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
        "/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        f"<< /Length {len(stream)} >>\nstream\n{stream}\nendstream",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = "%PDF-1.4\n"
    offsets = []
    for i, body in enumerate(objs, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n{body}\nendobj\n"
    xref_at = len(out)
    out += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n"
    out += "".join(f"{o:010d} 00000 n \n" for o in offsets)
    out += (f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_at}\n%%EOF\n")
    path.write_bytes(out.encode("latin-1"))
    return 1


def main() -> int:
    cfg = get_settings()
    cfg.ensure_dirs()

    bom_path = cfg.raw_dir / "DEMO_BOM_S2749189.xlsx"
    rows = make_bom(bom_path)
    tp_path = cfg.raw_dir / "DEMO_TECHPACK_S2749189.pdf"
    make_techpack(tp_path)

    identity = cfg.identity_dir / "identity_map.csv"
    if not identity.exists():
        identity.write_text(
            (cfg.identity_dir / "identity_map.example.csv").read_text(encoding="utf-8"),
            encoding="utf-8")

    print(f"Đã tạo dữ liệu GIẢ trong {cfg.raw_dir}:")
    print(f"  {bom_path.name:<32} {rows} dòng BOM (1 dòng cố ý thiếu dữ liệu)")
    print(f"  {tp_path.name:<32} 1 trang tech pack")
    print(f"  {identity.name:<32} bảng ánh xạ định danh mẫu")
    print("\nLƯU Ý: đây là dữ liệu giả. Không chép tech pack hay BOM thật của khách "
          "vào data/raw khi server còn mở ra internet (khoảng trống G8 chưa lấp).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
