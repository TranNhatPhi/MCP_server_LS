"""Kiểm thử lớp lưu trữ object.

Phần không cần MinIO chạy: kiểm tra tên object, phân giải URI, bản đồ bucket.
Phần cần MinIO: tự bỏ qua nếu không nối được, để `make test` chạy được ở mọi máy.
"""
from __future__ import annotations

import os
import unittest

from lsth_mcp.core.errors import NotFoundError, ValidationError
from lsth_mcp.io.storage import BUCKETS, SEARCH_ORDER, WRITABLE_AREAS, parse_uri
from lsth_mcp.io.storage.base import ObjectInfo, check_key, content_type_for


class TestKeySafety(unittest.TestCase):
    def test_accepts_normal_keys(self):
        self.assertEqual(check_key("BOM.xlsx"), "BOM.xlsx")
        self.assertEqual(check_key("S27/GARAN/BOM.xlsx"), "S27/GARAN/BOM.xlsx")

    def test_strips_leading_slash_and_dot(self):
        self.assertEqual(check_key("/BOM.xlsx"), "BOM.xlsx")
        self.assertEqual(check_key("./BOM.xlsx"), "BOM.xlsx")

    def test_blocks_traversal(self):
        for bad in ("../etc/passwd", "a/../../b", "a/..", "..", "a//b", ""):
            with self.assertRaises(ValidationError, msg=bad):
                check_key(bad)

    def test_blocks_null_byte(self):
        with self.assertRaises(ValidationError):
            check_key("a\x00b.xlsx")


class TestUriParsing(unittest.TestCase):
    def test_parses_known_buckets(self):
        self.assertEqual(parse_uri("s3://lsth-raw/BOM.xlsx"), ("raw", "BOM.xlsx"))
        self.assertEqual(parse_uri("s3://lsth-out/a/b.json"), ("out", "a/b.json"))

    def test_plain_path_is_not_a_uri(self):
        self.assertIsNone(parse_uri("BOM.xlsx"))

    def test_unknown_bucket_is_refused(self):
        with self.assertRaises(NotFoundError):
            parse_uri("s3://bucket-la/BOM.xlsx")


class TestBucketLayout(unittest.TestCase):
    def test_raw_and_templates_are_read_only(self):
        """Nguyên tắc 8 — file gốc và khuôn đã duyệt không nằm trong vùng ghi được."""
        for area in ("raw", "templates", "identity"):
            self.assertNotIn(area, WRITABLE_AREAS)

    def test_every_area_has_a_bucket_and_a_search_position(self):
        self.assertEqual(set(BUCKETS), set(SEARCH_ORDER))

    def test_raw_is_searched_before_work(self):
        """Tìm dữ liệu gốc trước, tránh vô tình đọc bản nháp máy tự dựng."""
        self.assertLess(SEARCH_ORDER.index("raw"), SEARCH_ORDER.index("work"))

    def test_content_types_for_the_formats_we_read(self):
        self.assertIn("spreadsheetml", content_type_for("a.xlsx"))
        self.assertEqual(content_type_for("a.pdf"), "application/pdf")
        self.assertEqual(content_type_for("a.bin"), "application/octet-stream")

    def test_object_info_helpers(self):
        info = ObjectInfo(key="S27/BOM_66P866.xlsx", size=10)
        self.assertEqual(info.name, "BOM_66P866.xlsx")
        self.assertEqual(info.suffix, ".xlsx")


def _minio_reachable() -> bool:
    if os.environ.get("LSTH_STORAGE", "").lower() != "minio":
        return False
    try:
        from lsth_mcp.io.storage import get_store
        get_store("raw").list(limit=1)
        return True
    except Exception:
        return False


@unittest.skipUnless(_minio_reachable(),
                     "Cần MinIO đang chạy và LSTH_STORAGE=minio")
class TestMinioLive(unittest.TestCase):
    """Chạy khi có MinIO thật: docker compose up -d && export LSTH_STORAGE=minio"""

    def test_app_account_cannot_write_to_raw(self):
        """Hai lớp chặn: cờ writable trong Python, và chính sách của MinIO."""
        from lsth_mcp.io.storage import MinioStore, get_store

        with self.assertRaises(ValidationError):
            get_store("raw").put_bytes("hack.txt", b"x")

        # Vượt qua cờ Python — MinIO vẫn phải từ chối.
        forced = MinioStore.connect("lsth-raw", writable=True)
        with self.assertRaises(Exception) as ctx:
            forced.put_bytes("hack.txt", b"x")
        self.assertNotIsInstance(ctx.exception, ValidationError)

    def test_read_keeps_s3_uri_as_source(self):
        from lsth_mcp.io.registry import read_any

        result = read_any("DEMO_BOM_S2749189.xlsx", sheet="BOM")
        self.assertTrue(result.sources[0].file.startswith("s3://lsth-raw/"))
        self.assertEqual(result.sources[0].sheet, "BOM")

    def test_download_cache_reuses_by_etag(self):
        from lsth_mcp.io.storage import get_store

        store = get_store("raw")
        first = store.download("DEMO_BOM_S2749189.xlsx")
        mtime = first.stat().st_mtime
        second = store.download("DEMO_BOM_S2749189.xlsx")
        self.assertEqual(first, second)
        self.assertEqual(mtime, second.stat().st_mtime)  # không tải lại


if __name__ == "__main__":
    unittest.main()


class TestStorageModeIsolation(unittest.TestCase):
    """Chế độ lưu trữ phải theo Settings được truyền vào, không theo biến môi trường.

    Hồi quy: trước đây storage_mode() đọc thẳng os.environ, nên khi bật
    LSTH_STORAGE=minio toàn cục thì mọi Settings dựng riêng — kể cả thư mục tạm
    trong kiểm thử — đều bị đẩy lên MinIO và ghi rác vào bucket thật.
    """

    def test_explicit_settings_beat_the_environment(self):
        from lsth_mcp.core.config import Settings
        from lsth_mcp.io.storage import storage_mode, using_minio

        old = os.environ.get("LSTH_STORAGE")
        os.environ["LSTH_STORAGE"] = "minio"
        try:
            self.assertFalse(using_minio(Settings()))
            self.assertEqual(storage_mode(Settings()), "local")
            self.assertTrue(using_minio(Settings(storage="minio")))
        finally:
            if old is None:
                os.environ.pop("LSTH_STORAGE", None)
            else:
                os.environ["LSTH_STORAGE"] = old

    def test_environment_still_applies_when_loading_settings(self):
        from lsth_mcp.core.config import load_settings

        old = os.environ.get("LSTH_STORAGE")
        os.environ["LSTH_STORAGE"] = "minio"
        try:
            self.assertEqual(load_settings().storage, "minio")
        finally:
            if old is None:
                os.environ.pop("LSTH_STORAGE", None)
            else:
                os.environ["LSTH_STORAGE"] = old
