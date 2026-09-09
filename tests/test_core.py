"""Kiểm thử lớp nền: nguồn gốc dữ liệu, khung trả về, quyền, vùng, nhật ký."""
from __future__ import annotations

import unittest

from lsth_mcp.core.audit import AuditLog, audited
from lsth_mcp.core.envelope import fail, ok
from lsth_mcp.core.errors import (
    NotFoundError,
    PermissionDeniedError,
    WriteNotAllowedError,
    ZoneViolationError,
)
from lsth_mcp.core.models import BomLine, PackingSpec
from lsth_mcp.core.paths import render_name, slugify
from lsth_mcp.core.permissions import Access, WriteGateStore, require
from lsth_mcp.core.provenance import Collector, Source, Sourced
from lsth_mcp.core.zones import Zone, ZoneClassifier
from helpers import temp_settings


class TestProvenance(unittest.TestCase):
    def test_label_reads_like_a_human_wrote_it(self):
        source = Source(file="BOM_66P866.xlsx", sheet="BOM", row=42)
        self.assertEqual(source.label(), "BOM_66P866.xlsx · sheet BOM · dòng 42")

    def test_unknown_value_is_flagged_for_a_person(self):
        value = Sourced.unknown("không tra được UPC trong ổ chung")
        self.assertFalse(value.is_trusted)
        self.assertTrue(value.needs_human)

    def test_collector_dedupes(self):
        collector = Collector()
        collector.add(Source(file="a.xlsx", row=1))
        collector.add(Source(file="a.xlsx", row=1))
        collector.add(Source(file="a.xlsx", row=2))
        self.assertEqual(len(collector.as_list()), 2)
        self.assertEqual(collector.files(), ["a.xlsx"])


class TestEnvelope(unittest.TestCase):
    def test_shape_is_always_the_same(self):
        for payload in (ok({"x": 1}), fail(NotFoundError("mất", hint="tìm lại"))):
            self.assertEqual(set(payload), {"ok", "data", "sources", "warnings", "error"})

    def test_error_carries_actionable_hint(self):
        payload = fail(NotFoundError("Không thấy UPC", hint="Tra trên hệ thống khách"))
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["error"]["hint"], "Tra trên hệ thống khách")


class TestModels(unittest.TestCase):
    def test_bom_row_maps_real_column_names(self):
        row = {"Item No": "1001", "Style": "66P866", "Material Code": "FB-K0007-HD",
               "Consumption": "0.216", "Unit BOM": "YD", "Wastage %": "1.0",
               "Cột lạ": "giữ nguyên"}
        line = BomLine.from_row(row, source=Source(file="bom.xlsx", row=5))
        self.assertEqual(line.style, "66P866")
        self.assertAlmostEqual(line.consumption, 0.216)
        self.assertEqual(line.extra["Cột lạ"], "giữ nguyên")
        self.assertEqual(line.validate(), [])

    def test_net_consumption_refuses_to_assume_zero_wastage(self):
        line = BomLine(style="X", material_code="M", consumption=1.0)
        self.assertIsNone(line.net_consumption())
        line.wastage_pct = 3.0
        self.assertAlmostEqual(line.net_consumption(), 1.03)

    def test_packing_spec_flags_safety_fields(self):
        spec = PackingSpec(style="66P866", market="US")
        self.assertEqual(sorted(spec.validate()), ["hangtag_position", "sticker_rule"])


class TestPermissions(unittest.TestCase):
    def test_engineer_has_no_rights_on_live_data(self):
        with self.assertRaises(PermissionDeniedError):
            require("engineer", "erp", Access.READ)

    def test_merchandiser_can_only_draft_in_erp(self):
        require("merchandiser_owner", "erp", Access.DRAFT)
        with self.assertRaises(PermissionDeniedError):
            require("merchandiser_owner", "erp", Access.WRITE)

    def test_write_gate_opens_only_after_five_styles(self):
        settings = temp_settings()
        store = WriteGateStore(settings.state_dir / "write_gates.json")
        with self.assertRaises(WriteNotAllowedError):
            store.unlock("s2_erp", "phi")
        for i in range(5):
            store.record_style("s2_erp", f"S{i}")
        gate = store.unlock("s2_erp", "phi")
        self.assertTrue(gate.unlocked)
        store.get("s2_erp").assert_can_write()

    def test_gate_message_says_how_many_styles_are_missing(self):
        settings = temp_settings()
        store = WriteGateStore(settings.state_dir / "write_gates.json")
        store.record_style("s6_packing", "A")
        with self.assertRaises(WriteNotAllowedError) as ctx:
            store.get("s6_packing").assert_can_write()
        self.assertIn("4/5", str(ctx.exception))


class TestZones(unittest.TestCase):
    def test_techpack_is_customer_zone_and_blocked_from_external_ai(self):
        classifier = ZoneClassifier.load(None)
        self.assertEqual(classifier.classify("S2749189 - PRODUCTION TECH PACK.pdf"), Zone.CUSTOMER)
        with self.assertRaises(ZoneViolationError):
            classifier.assert_external_ai_allowed("S2749189 - PRODUCTION TECH PACK.pdf")

    def test_strictest_rule_wins(self):
        classifier = ZoneClassifier.load(None)
        self.assertEqual(classifier.classify("BOM_price_2026.xlsx"), Zone.RESTRICTED)


class TestPaths(unittest.TestCase):
    def test_slugify_strips_vietnamese_accents(self):
        self.assertEqual(slugify("Tài liệu đóng gói"), "Tai-lieu-dong-goi")

    def test_render_name_reports_the_missing_variable(self):
        name = render_name("{style}_{market}_TLDG_v{rev}.xlsx",
                           {"style": "66P866", "market": "US", "rev": 1})
        self.assertEqual(name, "66P866_US_TLDG_v1.xlsx")
        with self.assertRaises(Exception) as ctx:
            render_name("{style}_{market}.xlsx", {"style": "X"})
        self.assertIn("market", str(ctx.exception))


class TestAudit(unittest.TestCase):
    def test_records_six_fields_and_survives_errors(self):
        settings = temp_settings()
        log = AuditLog(settings.audit_dir)
        with audited(log, "lsth-techpack.bom_extract", {"file": "a.xlsx"},
                     actor="phi", role="engineer_sandbox") as trace:
            trace.read("/tmp/a.xlsx")

        with self.assertRaises(ValueError):
            with audited(log, "x.y", {"password": "hunter2"}, actor="phi"):
                raise ValueError("hỏng")

        rows = log.tail(10)
        self.assertEqual(len(rows), 2)
        failed = next(r for r in rows if not r["ok"])
        self.assertEqual(failed["params"]["password"], "***")   # không ghi bí mật
        succeeded = next(r for r in rows if r["ok"])
        for field in ("actor", "ts", "tool", "params", "files_read", "ok"):
            self.assertIn(field, succeeded)
        self.assertEqual(succeeded["files_read"], ["/tmp/a.xlsx"])


if __name__ == "__main__":
    unittest.main()


class TestErpKnowledge(unittest.TestCase):
    """Kiến thức rút từ cẩm nang ERP nội bộ — xem docs/ERP_MAP.md."""

    def test_style_number_rule_matches_the_written_guide(self):
        from lsth_mcp.core.erp import style_number_rule
        for brand in ("Haddad", "IFG", "Jako", "Osaka"):
            self.assertEqual(style_number_rule(brand)[0], "contract_no", brand)
        for brand in ("Garan", "LTD", "H&M", "Decathlon"):
            self.assertEqual(style_number_rule(brand)[0], "customer_style", brand)

    def test_erp_style_number_refuses_to_fall_back_to_the_other_field(self):
        from lsth_mcp.domain.identity import erp_style_number
        self.assertEqual(
            erp_style_number("Haddad", contract_no="REF-1", customer_style="66P866")["style_number"],
            "REF-1")
        with self.assertRaises(NotFoundError):
            erp_style_number("Haddad", customer_style="66P866")   # thiếu contract_no

    def test_survey_covered_only_half_the_brands_in_erp(self):
        from lsth_mcp.core.erp import BRANDS, unsurveyed_brands
        self.assertEqual(len(BRANDS), 12)
        self.assertEqual(len(unsurveyed_brands()), 6)

    def test_export_fallback_path_exists_for_most_modules(self):
        from lsth_mcp.core.erp import MODULES, exportable_modules
        self.assertGreater(len(exportable_modules()), len(MODULES) * 0.7)

    def test_vendor_id_rule(self):
        from lsth_mcp.core.erp import valid_vendor_id
        self.assertTrue(valid_vendor_id("HENGDA"))
        self.assertFalse(valid_vendor_id("Heng Da"))
        self.assertFalse(valid_vendor_id("hengda"))
