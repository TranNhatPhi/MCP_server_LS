"""F5 · Bộ đánh giá chất lượng.

Buổi thử ngày 07/09 ghi nhận mô hình giải thích sai 3 thuật ngữ ngành và bịa 2 từ
viết tắt. Không đo thì không biết đang tốt lên hay xấu đi — nên mỗi lần sửa server
đều chạy lại bộ này trước khi mở cho người dùng thật.

Hạt giống: 36 cặp hỏi đáp trong erp_pilot.jsonl, cộng 5 mã hàng có BOM và TLĐG đã
duyệt làm đáp án.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from ..core.errors import NotFoundError
from ..io.readers.jsonio import read_json


@dataclass
class EvalCase:
    id: str
    question: str
    expected: Any
    kind: str = "qa"          # qa | field | file
    tags: List[str] = field(default_factory=list)
    must_cite: bool = True    # nguyên tắc 4: trả lời không dẫn nguồn là trượt


@dataclass
class CaseResult:
    case_id: str
    passed: bool
    got: Any = None
    reason: str = ""


@dataclass
class EvalReport:
    total: int
    passed: int
    results: List[CaseResult] = field(default_factory=list)
    ran_at: str = ""

    @property
    def score(self) -> float:
        return round(100.0 * self.passed / self.total, 1) if self.total else 0.0

    def failures(self) -> List[CaseResult]:
        return [r for r in self.results if not r.passed]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ran_at": self.ran_at,
            "total": self.total,
            "passed": self.passed,
            "score_pct": self.score,
            "failures": [
                {"case_id": r.case_id, "reason": r.reason, "got": r.got}
                for r in self.failures()
            ],
        }


def load_cases(path: Any) -> List[EvalCase]:
    path = Path(path)
    if not path.exists():
        raise NotFoundError(
            f"Chưa có bộ ca kiểm thử: {path}",
            hint="Bắt đầu từ data/eval/cases.example.jsonl, và bổ sung 36 cặp hỏi đáp "
                 "trong erp_pilot.jsonl cùng 5 mã hàng đã duyệt.",
        )
    return [
        EvalCase(
            id=str(row.get("id") or f"case-{index}"),
            question=row.get("question", ""),
            expected=row.get("expected"),
            kind=row.get("kind", "qa"),
            tags=row.get("tags") or [],
            must_cite=bool(row.get("must_cite", True)),
        )
        for index, row in enumerate(read_json(path).rows, start=1)
    ]


def run(cases: List[EvalCase], answer_fn: Callable[[EvalCase], Dict[str, Any]]) -> EvalReport:
    """Chạy bộ ca qua một hàm trả lời trả về envelope {ok, data, sources...}."""
    results: List[CaseResult] = []
    for case in cases:
        try:
            envelope = answer_fn(case)
        except Exception as exc:
            results.append(CaseResult(case.id, False, None, f"lỗi: {exc}"))
            continue

        got = envelope.get("data")
        if not envelope.get("ok"):
            results.append(CaseResult(case.id, False, got,
                                      f"tool báo lỗi: {(envelope.get('error') or {}).get('message')}"))
            continue
        if case.must_cite and not envelope.get("sources"):
            results.append(CaseResult(case.id, False, got,
                                      "trả lời không dẫn nguồn (nguyên tắc 4)"))
            continue
        if not _matches(got, case.expected):
            results.append(CaseResult(case.id, False, got, "khác đáp án"))
            continue
        results.append(CaseResult(case.id, True, got))

    return EvalReport(
        total=len(cases),
        passed=sum(1 for r in results if r.passed),
        results=results,
        ran_at=datetime.now().isoformat(timespec="seconds"),
    )


def _matches(got: Any, expected: Any) -> bool:
    if expected is None:
        return True
    if isinstance(expected, str) and isinstance(got, str):
        return expected.strip().casefold() in got.strip().casefold()
    if isinstance(expected, dict) and isinstance(got, dict):
        return all(_matches(got.get(k), v) for k, v in expected.items())
    return got == expected
