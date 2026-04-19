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
        lines.append(f"Longest: {longest.job_id} \u2014 {longest.length}x {longest.status}")
    return "\n".join(lines) + "\n"


def format_streaker_json(report: StreakerReport) -> str:
    return json.dumps(report.to_dict(), indent=2)


def format_streaker_csv(report: StreakerReport) -> str:
    """Return streaks as a simple CSV string with header row."""
    lines = ["job_id,length,status"]
    for s in report.streaks:
        lines.append(f"{s.job_id},{s.length},{s.status}")
    return "\n".join(lines) + "\n"


def format_streaker(report: StreakerReport, fmt: str = "text") -> str:
    """Format a StreakerReport as text, json, or csv."""
    if fmt == "json":
        return format_streaker_json(report)
    if fmt == "csv":
        return format_streaker_csv(report)
    return format_streaker_text(report)
