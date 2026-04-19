"""Format StreakerReport as text or JSON."""
import json
from batchmark.streaker import StreakerReport


def format_streaker_text(report: StreakerReport) -> str:
    if not report.streaks:
        return "No streaks detected.\n"
    lines = ["Streak Report", "=" * 30]
    for s in report.streaks:
        lines.append(f"  {s.job_id}: {s.length}x {s.status}")
    longest = report.longest()
    if longest:
        lines.append("")
        lines.append(f"Longest: {longest.job_id} — {longest.length}x {longest.status}")
    return "\n".join(lines) + "\n"


def format_streaker_json(report: StreakerReport) -> str:
    return json.dumps(report.to_dict(), indent=2)


def format_streaker(report: StreakerReport, fmt: str = "text") -> str:
    if fmt == "json":
        return format_streaker_json(report)
    return format_streaker_text(report)
