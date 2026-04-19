"""Format WatchdogReport as text or JSON."""
from __future__ import annotations
import json
from batchmark.watchdog import WatchdogReport


def format_watchdog_text(report: WatchdogReport) -> str:
    if not report.has_violations:
        return "Watchdog: no timeout violations.\n"
    lines = ["Watchdog Timeout Violations:", ""]
    for v in report.violations:
        dur = f"{v.duration:.3f}s" if v.duration is not None else "N/A"
        lines.append(f"  {v.job_id}: {dur} > limit {v.limit:.3f}s")
    lines.append("")
    return "\n".join(lines)


def format_watchdog_json(report: WatchdogReport) -> str:
    return json.dumps(report.to_dict(), indent=2)


def format_watchdog(report: WatchdogReport, fmt: str = "text") -> str:
    if fmt == "json":
        return format_watchdog_json(report)
    return format_watchdog_text(report)
