"""Format dispatch reports as text or JSON."""
from __future__ import annotations
import json
from batchmark.dispatcher import DispatchReport


def format_dispatch_text(report: DispatchReport) -> str:
    if not report.entries:
        return "No dispatched results."

    lines = ["Dispatch Report", "=" * 40]
    counts = report.route_counts()
    lines.append(f"Default route : {report.default_route}")
    lines.append(f"Total results : {len(report.entries)}")
    lines.append("")
    lines.append("Route Counts:")
    for route, count in sorted(counts.items()):
        lines.append(f"  {route:<20} {count}")
    lines.append("")
    lines.append("Entries:")
    for entry in report.entries:
        dur = (
            f"{entry.result.duration_seconds:.3f}s"
            if entry.result.duration_seconds is not None
            else "N/A"
        )
        status = "OK" if entry.result.success else "FAIL"
        lines.append(
            f"  [{entry.route:<12}] {entry.result.job_id:<20} {status:<6} {dur}"
        )
    return "\n".join(lines)


def format_dispatch_json(report: DispatchReport) -> str:
    return json.dumps(report.to_dict(), indent=2)


def format_dispatch(report: DispatchReport, fmt: str = "text") -> str:
    if fmt == "json":
        return format_dispatch_json(report)
    return format_dispatch_text(report)
