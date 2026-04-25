"""Formatters for RollingReport output."""
from __future__ import annotations

import json

from batchmark.roller import RollingReport


def format_roller_text(report: RollingReport) -> str:
    if not report.points:
        return "No data for rolling stats.\n"

    lines = [f"Rolling window: {report.window}\n"]
    lines.append(f"{'#':<5} {'job_id':<24} {'raw':>8} {'avg':>8} {'min':>8} {'max':>8}")
    lines.append("-" * 68)
    for p in report.points:
        raw = f"{p.raw_duration:.3f}" if p.raw_duration is not None else "  None"
        avg = f"{p.rolling_avg:.3f}" if p.rolling_avg is not None else "  None"
        mn  = f"{p.rolling_min:.3f}" if p.rolling_min is not None else "  None"
        mx  = f"{p.rolling_max:.3f}" if p.rolling_max is not None else "  None"
        lines.append(f"{p.index:<5} {p.job_id:<24} {raw:>8} {avg:>8} {mn:>8} {mx:>8}")
    return "\n".join(lines) + "\n"


def format_roller_json(report: RollingReport) -> str:
    return json.dumps(report.to_dict(), indent=2)


def format_roller(report: RollingReport, fmt: str = "text") -> str:
    if fmt == "json":
        return format_roller_json(report)
    return format_roller_text(report)
