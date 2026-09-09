#!/usr/bin/env python3
"""F5 — chạy bộ đánh giá chất lượng trước khi mở server cho người dùng thật.

    PYTHONPATH=src python3 scripts/run_eval.py [đường/dẫn/cases.jsonl]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lsth_mcp.core.config import get_settings      # noqa: E402
from lsth_mcp.core.envelope import ok              # noqa: E402
from lsth_mcp.core.errors import LsthError         # noqa: E402
from lsth_mcp.domain.evalset import load_cases, run  # noqa: E402


def answer(case):
    """Chỗ nối vào server thật. Hiện trả lời rỗng để bộ khung chạy được từ đầu.

    Khi S1 hoặc S2 đã dựng, thay thân hàm này bằng lệnh gọi tool tương ứng.
    """
    return ok(None, sources=[])


def main() -> int:
    cfg = get_settings()
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else cfg.eval_dir / "cases.jsonl"
    if not path.exists():
        path = cfg.eval_dir / "cases.example.jsonl"

    try:
        cases = load_cases(path)
    except LsthError as exc:
        print(f"LỖI: {exc.message}\n  -> {exc.hint}", file=sys.stderr)
        return 1

    report = run(cases, answer)
    print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    print(f"\nĐiểm: {report.score}%  ({report.passed}/{report.total})")
    if report.failures():
        print("\nCa trượt:")
        for result in report.failures():
            print(f"  {result.case_id:<12} {result.reason}")
    return 0 if report.score == 100.0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
