"""Formatters for CompactReport output."""
from __future__ import annotations

import json
from typing import Literal

from batchmark.compactor import CompactReport

Format = Literal["text", "json"]


def _fmt_dur(d) -> str:
    if d is None:
        return "N/A"
    return f"{d:.3f}s"


def format_compact_text(report: CompactReport) -> str:
    if not report.results:
        return "No compacted results."

    lines = [f"Compact report  strategy={report.strategy}  jobs={report.total}"]
    lines.append("-" * 52)
    for r in report.results:
        status = "OK" if r.success else "FAIL"
        lines.append(
            f"  {r.job_id:<24} {_fmt_dur(r.duration):>10}  "
            f"{status:<4}  (n={r.source_count})"
        )
    return "\n".join(lines)


def format_compact_json(report: CompactReport) -> str:
    return json.dumps(report.to_dict(), indent=2)


def format_compact(report: CompactReport, fmt: Format = "text") -> str:
    if fmt == "json":
        return format_compact_json(report)
    return format_compact_text(report)
