"""Format ThrottleReport for display."""
from __future__ import annotations

import json

from batchmark.throttle import ThrottleReport


def format_throttle_text(report: ThrottleReport) -> str:
    if report.total_jobs == 0:
        return "Throttle report: no jobs.\n"
    lines = [
        "Throttle Report",
        f"  Total jobs      : {report.total_jobs}",
        f"  Total wait (s)  : {report.total_wait_seconds:.4f}",
        f"  Avg wait   (s)  : {report.avg_wait():.4f}",
    ]
    if report.config.max_per_second is not None:
        lines.append(f"  Max per second  : {report.config.max_per_second}")
    if report.config.min_gap_seconds:
        lines.append(f"  Min gap (s)     : {report.config.min_gap_seconds}")
    return "\n".join(lines) + "\n"


def format_throttle_json(report: ThrottleReport) -> str:
    return json.dumps(report.to_dict(), indent=2)


def format_throttle(report: ThrottleReport, fmt: str = "text") -> str:
    if fmt == "json":
        return format_throttle_json(report)
    return format_throttle_text(report)
