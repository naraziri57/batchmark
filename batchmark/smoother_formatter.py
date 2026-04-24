"""Format SmoothedReport objects for display."""
from __future__ import annotations

import json
from typing import List

from batchmark.smoother import SmoothedReport


def format_smoother_text(reports: List[SmoothedReport]) -> str:
    if not reports:
        return "No smoothed data."
    lines: List[str] = []
    for report in reports:
        lines.append(f"Job: {report.job_id}  (window={report.window})")
        lines.append(f"  {'#':<5} {'raw':>10} {'smoothed':>12}")
        for p in report.points:
            raw = f"{p.raw_duration:.4f}" if p.raw_duration is not None else "N/A"
            sm = f"{p.smoothed_duration:.4f}" if p.smoothed_duration is not None else "N/A"
            lines.append(f"  {p.index:<5} {raw:>10} {sm:>12}")
        lines.append("")
    return "\n".join(lines).rstrip()


def format_smoother_json(reports: List[SmoothedReport]) -> str:
    return json.dumps([r.to_dict() for r in reports], indent=2)


def format_smoother(
    reports: List[SmoothedReport],
    fmt: str = "text",
) -> str:
    if fmt == "json":
        return format_smoother_json(reports)
    return format_smoother_text(reports)
