from __future__ import annotations
import json
from batchmark.grouper import GroupReport


def _fmt_dur(v) -> str:
    if v is None:
        return "N/A"
    return f"{v:.3f}s"


def format_group_text(report: GroupReport) -> str:
    if not report.groups:
        return "No groups."
    lines = []
    for g in report.groups:
        s = g.summary
        lines.append(
            f"[{g.label}] count={g.count} "
            f"ok={g.success_count} fail={g.failure_count} "
            f"avg={_fmt_dur(s.avg_duration)} "
            f"median={_fmt_dur(s.median_duration)}"
        )
    return "\n".join(lines)


def format_group_json(report: GroupReport) -> str:
    return json.dumps(report.to_dict(), indent=2)


def format_group(report: GroupReport, fmt: str = "text") -> str:
    if fmt == "json":
        return format_group_json(report)
    return format_group_text(report)
