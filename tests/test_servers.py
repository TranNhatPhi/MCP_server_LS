"""Kiểm thử S1 và bảng đặc tả 17 thành phần."""
from __future__ import annotations

import unittest

from lsth_mcp.core.errors import NotImplementedYetError
from lsth_mcp.io.writers.excel import write_rows
from lsth_mcp.io.writers.safe import SafeWriter
from lsth_mcp.servers import ALL_SPECS, FOUNDATION, spec_by_code, specs_for_round
from lsth_mcp.servers.s1_techpack import TechpackServer
from lsth_mcp.servers.s2_erp import ErpServer
from helpers import temp_settings, unlock

BOM_ROWS = [
    {"Item No": "1001", "Style": "66P866", "Material Code": "FB-K0007-HD",
     "Consumption": 0.216, "Unit BOM": "YD", "Wastage %": 1.0},
    {"Item No": "1002", "Style": "66P866", "Material Code": "TR-0021",
     "Consumption": 1.5, "Unit BOM": "PCS", "Wastage %": 0.0},
    {"Item No": "1003", "Style": "66P866", "Material Code": "",
     "Consumption": None, "Unit BOM": "PCS"},
]


class TestSpecs(unittest.TestCase):
    def test_seventeen_components_are_accounted_for(self):
        self.assertEqual(len(FOUNDATION) + len(ALL_SPECS), 17)

    def test_round_order_matches_v2_roadmap(self):
        # v2.0 đảo thứ tự: S2 erp lên vòng 2 vì nhóm việc chiếm 30,2% quỹ thời gian.
        self.assertEqual(spec_by_code("S2").round, 2)
        self.assertEqual(spec_by_code("S6").round, 4)
        self.assertEqual(spec_by_code("M2").round, 1)
        self.assertEqual({s.code for s in specs_for_round(5)}, {"S7", "M5"})

    def test_every_server_declares_who_accepts_it(self):
        for spec in ALL_SPECS:
            self.assertTrue(spec.accepted_by, f"{spec.code} chưa ghi người nghiệm thu")
            self.assertTrue(spec.tools, f"{spec.code} chưa có hợp đồng tool")


class TestStubsFailLoudly(unittest.TestCase):
    def test_unbuilt_tool_names_the_blocking_gap(self):
        settings = temp_settings()
        server = ErpServer(settings=settings)
        with self.assertRaises(NotImplementedYetError) as ctx:
            server.bom_get("66P866")
        self.assertIn("G1", str(ctx.exception))


class TestTechpackServer(unittest.TestCase):
    def setUp(self):
        self.settings = temp_settings()
        unlock(self.settings, "seed")
        writer = SafeWriter.for_server("seed", settings=self.settings)
        # Ghi vào work/ rồi chép sang raw/ vì SafeWriter cố ý không ghi được vào raw.
        tmp = self.settings.work_dir / "bom.xlsx"
        write_rows(writer, tmp, BOM_ROWS, sheet_name="BOM", draft_banner=False)
        self.bom = self.settings.raw_dir / "BOM_66P866.xlsx"
        self.bom.write_bytes(tmp.read_bytes())
        self.server = TechpackServer(settings=self.settings)

    def test_bom_extract_returns_lines_with_sources(self):
        result = self.server.bom_extract(str(self.bom), sheet="BOM")
        self.assertTrue(result["ok"], result.get("error"))
        data = result["data"]
        self.assertEqual(data["line_count"], 3)
        self.assertEqual(data["styles"], ["66P866"])
        self.assertTrue(result["sources"])
        self.assertEqual(result["sources"][0]["sheet"], "BOM")

    def test_incomplete_rows_are_reported_not_guessed(self):
        data = self.server.bom_extract(str(self.bom), sheet="BOM")["data"]
        self.assertEqual(len(data["incomplete_rows"]), 1)
        missing = data["incomplete_rows"][0]["missing"]
        self.assertIn("material_code", missing)
        self.assertIn("consumption", missing)
        self.assertEqual(data["incomplete_rows"][0]["row"], 4)

    def test_errors_come_back_as_envelope_not_exceptions(self):
        result = self.server.bom_extract(str(self.settings.raw_dir / "khong-co.xlsx"))
        self.assertFalse(result["ok"])
        self.assertTrue(result["error"]["hint"])

    def test_every_call_lands_in_the_audit_log(self):
        self.server.bom_extract(str(self.bom), sheet="BOM")
        rows = self.server.audit.tail(5)
        self.assertEqual(rows[0]["tool"], "lsth-techpack.bom_extract")
        # Nhật ký ghi đường dẫn đã phân giải (macOS: /var -> /private/var).
        self.assertIn(str(self.bom.resolve()), rows[0]["files_read"])


if __name__ == "__main__":
    unittest.main()
