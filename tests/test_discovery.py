"""Tìm file/cây: giới hạn, ràng buộc đường dẫn và nguồn MinIO."""
import shutil
import unittest
import unicodedata
from unittest.mock import patch

from helpers import temp_settings
from lsth_mcp.core.errors import PathOutsideRootError, ValidationError
from lsth_mcp.io.discovery import build_tree, search_files
from lsth_mcp.io.storage.base import ObjectInfo


class FakeStore:
    bucket = "lsth-raw"
    writable = False

    def __init__(self):
        self.objects = [ObjectInfo(key=key, size=10) for key in
                        ("a.txt", "orders/S27/BOM.xlsx", "orders/S27/pack.pdf")]

    def list(self, prefix="", limit=200):
        return [obj for obj in self.objects if obj.key.startswith(prefix)][:limit]

    def uri(self, key):
        return "s3://lsth-raw/" + key


class TestDiscovery(unittest.TestCase):
    def setUp(self):
        self.cfg = temp_settings(write_enabled=False)
        self.addCleanup(shutil.rmtree, self.cfg.project_root)
        folder = self.cfg.raw_dir / "orders" / "S27"
        folder.mkdir(parents=True)
        (folder / "BOM.xlsx").write_bytes(b"metadata only")
        (folder / "pack.pdf").write_bytes(b"metadata only")
        (self.cfg.raw_dir / "a.txt").write_text("BOM in content is not searched")

    def test_search_casefold_relative_path_and_no_content_reads(self):
        result = search_files("bom", root="raw", settings=self.cfg)
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["files"][0]["relative_path"], "orders/S27/BOM.xlsx")
        self.assertEqual(search_files("s27", settings=self.cfg)["count"], 2)
        self.assertFalse(result["truncated"])
        scoped = search_files("bom", root="orders/S27", settings=self.cfg)
        self.assertEqual(scoped["files"][0]["relative_path"], "BOM.xlsx")

    def test_result_and_scan_limits_do_not_claim_complete_results(self):
        result = search_files("s27", limit=1, settings=self.cfg)
        self.assertTrue(result["truncated"])
        self.assertFalse(result["scan_truncated"])
        result = search_files("bom", scan_limit=1, settings=self.cfg)
        self.assertEqual(result["count"], 0)
        self.assertTrue(result["scan_truncated"])

    def test_invalid_input_and_roots(self):
        for params in ({"query": " "}, {"query": "a", "limit": 0},
                       {"query": "a", "scan_limit": -1}):
            with self.assertRaises(ValidationError):
                search_files(settings=self.cfg, **params)
        with self.assertRaises(PathOutsideRootError):
            search_files("a", root=str(self.cfg.project_root), settings=self.cfg)
        with self.assertRaises(ValidationError):
            build_tree(max_depth=0, settings=self.cfg)

    def test_symlink_outside_roots_is_not_exposed(self):
        outside = self.cfg.project_root / "private.txt"
        outside.write_text("private")
        (self.cfg.raw_dir / "alias.txt").symlink_to(outside)
        self.assertEqual(search_files("alias", settings=self.cfg)["count"], 0)

    def test_tree_depth_and_sources(self):
        result = build_tree(root="raw", max_depth=1, settings=self.cfg)
        children = result["tree"][0]["children"]
        self.assertEqual(children[1]["name"], "orders")
        self.assertTrue(children[1]["collapsed"])
        self.assertTrue(result["depth_limited"])
        self.assertEqual(result["file_count"], 3)
        self.assertEqual(len(result["sources"]), 3)
        complete = build_tree(root="raw", settings=self.cfg)
        self.assertFalse(complete["depth_limited"])

    @patch("lsth_mcp.io.discovery.get_store")
    def test_minio_prefix_search_and_tree_keep_s3_sources(self, get_store):
        get_store.return_value = FakeStore()
        root = "s3://lsth-raw/orders/S27/"
        result = search_files("BOM", root=root, scan_limit=2, settings=self.cfg)
        self.assertEqual(result["files"][0]["path"], root + "BOM.xlsx")
        self.assertFalse(result["scan_truncated"])
        tree = build_tree(root=root, settings=self.cfg)
        self.assertEqual(tree["file_count"], 2)
        self.assertEqual(tree["tree"][0]["children"][0]["path"], root + "BOM.xlsx")
        self.assertEqual(tree["sources"][0]["file"], root + "BOM.xlsx")
        self.assertEqual(self.cfg.storage, "local")

    def test_minio_rejects_unknown_bucket_and_traversal(self):
        for root in ("s3://unknown/", "s3://lsth-raw/../"):
            with self.assertRaises(ValidationError):
                search_files("bom", root=root, settings=self.cfg)

    @patch("lsth_mcp.io.discovery.get_store")
    def test_tree_search_keeps_parents_and_filters_before_limit(self, get_store):
        get_store.return_value = FakeStore()
        tree = build_tree(root="s3://lsth-raw/", query="s27 BOM", limit=1, settings=self.cfg)
        self.assertEqual(tree["file_count"], 1)
        self.assertEqual(tree["matched_count"], 1)
        self.assertFalse(tree["truncated"])
        self.assertEqual(tree["sources"], [{"file": "s3://lsth-raw/orders/S27/BOM.xlsx"}])
        self.assertEqual(tree["tree_text"],
                         "└── s3://lsth-raw/\n    └── orders/\n        └── S27/\n            └── BOM.xlsx")
        self.assertNotIn("pack.pdf", tree["tree_text"])

    @patch("lsth_mcp.io.discovery.get_store")
    def test_tree_search_folder_includes_descendants_and_empty_result(self, get_store):
        get_store.return_value = FakeStore()
        result = build_tree(root="s3://lsth-raw/", query="orders", settings=self.cfg)
        self.assertEqual(result["matched_count"], 2)
        self.assertIn("BOM.xlsx", result["tree_text"])
        self.assertIn("pack.pdf", result["tree_text"])
        empty = build_tree(root="s3://lsth-raw/", query="missing", settings=self.cfg)
        self.assertEqual(empty["tree"], [])
        self.assertEqual(empty["sources"], [])
        self.assertEqual(empty["tree_text"], "")
        self.assertEqual(empty["matched_count"], 0)
        self.assertFalse(empty["truncated"])

    @patch("lsth_mcp.io.discovery.get_store")
    def test_vietnamese_search_preserves_original_s3_key(self, get_store):
        store = FakeStore()
        key = unicodedata.normalize("NFD", "công việc/Đặng Thương.xlsx")
        store.objects = [ObjectInfo(key=key, size=20)]
        get_store.return_value = store
        for query in ("cong viec dang", "CÔNG VIỆC ĐẶNG", "thuong"):
            result = build_tree(root="s3://lsth-raw/", query=query, settings=self.cfg)
            self.assertEqual(result["matched_count"], 1)
            self.assertEqual(result["sources"][0]["file"], store.uri(key))
            flat = search_files(query, root="s3://lsth-raw/", settings=self.cfg)
            self.assertEqual(flat["files"][0]["path"], store.uri(key))

    def test_filtered_tree_reports_scan_limit_and_collapsed_nodes(self):
        result = build_tree(root="raw", query="BOM", scan_limit=1, settings=self.cfg)
        self.assertEqual(result["matched_count"], 0)
        self.assertTrue(result["scan_truncated"])
        self.assertTrue(result["truncated"])
        result = build_tree(root="raw", query="s27", limit=1, max_depth=1, settings=self.cfg)
        self.assertEqual(result["matched_count"], 2)
        self.assertEqual(result["file_count"], 1)
        self.assertTrue(result["truncated"])
        self.assertTrue(result["depth_limited"])
        self.assertIn("orders/ [thu gọn]", result["tree_text"])

    def test_gateway_tree_passes_query_and_audits_it(self):
        from lsth_mcp import server
        from lsth_mcp.core.audit import AuditLog
        with patch("lsth_mcp.server.get_settings", return_value=self.cfg), \
             patch("lsth_mcp.io.discovery.get_settings", return_value=self.cfg):
            result = server.file_tree(root="raw", query="S27 BOM")
        self.assertTrue(result["ok"])
        self.assertEqual(result["data"]["matched_count"], 1)
        self.assertEqual(len(result["sources"]), 1)
        self.assertEqual(AuditLog(self.cfg.audit_dir).tail(1)[0]["params"]["query"], "S27 BOM")

    def test_tools_registered_and_audited_with_error_envelopes(self):
        from lsth_mcp import server
        from lsth_mcp.core.audit import AuditLog
        self.assertIn(server.file_search, server.TOOLS)
        self.assertIn(server.file_tree, server.TOOLS)
        with patch("lsth_mcp.server.get_settings", return_value=self.cfg), \
             patch("lsth_mcp.io.discovery.get_settings", return_value=self.cfg):
            result = server.file_search("BOM", root="raw")
            self.assertTrue(result["ok"])
            self.assertTrue(result["sources"])
            self.assertTrue(server.file_tree(root="raw")["ok"])
            error = server.file_search("")
            self.assertFalse(error["ok"])
            self.assertEqual(error["error"]["code"], "validation_error")
        records = AuditLog(self.cfg.audit_dir).tail(3)
        self.assertEqual(len(records), 3)
        self.assertFalse(records[0]["ok"])
