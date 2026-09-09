#!/usr/bin/env python3
"""Đẩy dữ liệu từ thư mục data/ lên MinIO.

    python3 scripts/sync_to_minio.py            # đẩy tất cả các vùng
    python3 scripts/sync_to_minio.py raw        # chỉ một vùng
    python3 scripts/sync_to_minio.py --list     # xem trong kho đang có gì

Vùng raw/templates/identity là chỉ đọc với tài khoản ứng dụng, nên script này
dùng tài khoản quản trị (đọc từ docker/.env) để nạp dữ liệu ban đầu.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def load_docker_env() -> None:
    """Lấy khoá quản trị từ docker/.env để nạp được vào cả bucket chỉ đọc."""
    env_file = ROOT / "docker" / ".env"
    if not env_file.exists():
        return
    values = {}
    for line in env_file.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, _, v = line.partition("=")
            values[k.strip()] = v.strip()
    os.environ.setdefault("LSTH_S3_ENDPOINT", f"localhost:{values.get('MINIO_PORT', '9000')}")
    os.environ["LSTH_S3_ACCESS_KEY"] = values.get("MINIO_ROOT_USER", "")
    os.environ["LSTH_S3_SECRET_KEY"] = values.get("MINIO_ROOT_PASSWORD", "")


load_docker_env()

from lsth_mcp.core.config import get_settings          # noqa: E402
from lsth_mcp.io.storage import BUCKETS, MinioStore    # noqa: E402
from lsth_mcp.io.storage.base import content_type_for  # noqa: E402

#: Vùng -> thư mục cục bộ tương ứng.
AREA_DIRS = {
    "raw": "raw_dir", "templates": "templates_dir", "identity": "identity_dir",
    "work": "work_dir", "out": "out_dir",
}


def admin_store(bucket: str) -> MinioStore:
    store = MinioStore.connect(bucket, writable=True)
    return store


def main() -> int:
    cfg = get_settings()
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    listing = "--list" in sys.argv

    if listing:
        for area, bucket in BUCKETS.items():
            objects = admin_store(bucket).list(limit=100)
            print(f"\n{bucket}  ({len(objects)} object)")
            for obj in objects:
                print(f"   {obj.size:>10,} B  {obj.key}")
        return 0

    areas = args or [a for a in AREA_DIRS if a in BUCKETS]
    total = 0
    for area in areas:
        if area not in AREA_DIRS:
            print(f"Bỏ qua vùng không rõ: {area}", file=sys.stderr)
            continue
        local_dir = Path(getattr(cfg, AREA_DIRS[area]))
        if not local_dir.exists():
            continue
        store = admin_store(BUCKETS[area])
        print(f"\n{local_dir.name}/  ->  {BUCKETS[area]}")
        for path in sorted(local_dir.rglob("*")):
            if not path.is_file() or path.name.startswith(".") or path.name == "README.md":
                continue
            if "_backup" in path.parts or "cache" in path.parts:
                continue
            key = str(path.relative_to(local_dir))
            store.put_bytes(key, path.read_bytes(), content_type_for(key))
            print(f"   {path.stat().st_size:>10,} B  {key}")
            total += 1

    print(f"\nĐã đẩy {total} file. Xem lại: python3 scripts/sync_to_minio.py --list")
    print("Console MinIO: http://localhost:9001")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
