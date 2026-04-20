"""Format snapshot diff reports for display."""
from __future__ import annotations

import json
from typing import Literal

from batchmark.snapshot_diff import SnapshotDiffReport


def _arrow(delta: float | None) -> str:
    if delta is None:
        return "n/a"
    if delta < 0:
        return f"{delta:+.3f}s ↑"
    if delta > 0:
        return f"{delta:+.3f}s ↓"
    return "0.000s ="


def format_snapshot_diff_text(report: SnapshotDiffReport) -> str:
    if not report.entries:
        return "No jobs to compare."
    lines = [
        f"Snapshot diff: {report.before_label} → {report.after_label}",
        "-" * 54,
    ]
    for e in report.entries:
        status = "" if not e.status_changed else " [STATUS CHANGED]"
        lines.append(
            f"  {e.job_id:<24} {_arrow(e.delta)}{status}"
        )
    changed = report.changed()
    lines.append("-" * 54)
    lines.append(f"Total jobs: {len(report.entries)}  Changed: {len(changed)}")
    return "\n".join(lines)


def format_snapshot_diff_json(report: SnapshotDiffReport) -> str:
    return json.dumps(report.to_dict(), indent=2)


def format_snapshot_diff(
    report: SnapshotDiffReport,
    fmt: Literal["text", "json"] = "text",
) -> str:
    if fmt == "json":
        return format_snapshot_diff_json(report)
    return format_snapshot_diff_text(report)
