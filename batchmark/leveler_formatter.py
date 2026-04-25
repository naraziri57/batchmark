"""Format LevelReport as text, JSON, or CSV."""
from __future__ import annotations
import json
from batchmark.leveler import LevelReport

_ICONS = {"ok": "✓", "warn": "!", "critical": "✗"}


def format_level_text(report: LevelReport) -> str:
    if not report.items:
        return "No results to level.\n"
    lines = [f"{'JOB':<30} {'LEVEL':<10} REASON"]
    lines.append("-" * 70)
    for item in report.items:
        icon = _ICONS.get(item.level, "?")
        lines.append(f"{item.result.job_id:<30} {icon} {item.level:<8} {item.reason}")
    lines.append("")
    lines.append(
        f"Summary: ok={report.to_dict()['ok']}  "
        f"warn={report.warn_count}  critical={report.critical_count}"
    )
    return "\n".join(lines) + "\n"


def format_level_json(report: LevelReport) -> str:
    return json.dumps(report.to_dict(), indent=2)


def format_level_csv(report: LevelReport) -> str:
    lines = ["job_id,duration,success,level,reason"]
    for item in report.items:
        d = item.to_dict()
        dur = "" if d["duration"] is None else f"{d['duration']:.6f}"
        reason = d["reason"].replace(",", ";")
        lines.append(f"{d['job_id']},{dur},{d['success']},{d['level']},{reason}")
    return "\n".join(lines) + "\n"


def format_level(report: LevelReport, fmt: str = "text") -> str:
    if fmt == "json":
        return format_level_json(report)
    if fmt == "csv":
        return format_level_csv(report)
    return format_level_text(report)
