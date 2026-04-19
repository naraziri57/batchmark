"""Format DiffReport as text or JSON."""
from __future__ import annotations
import json
from batchmark.differ import DiffReport


def _arrow(delta: float | None) -> str:
    if delta is None:
        return ""
    if delta < 0:
        return f"↓ {abs(delta):.3f}s"
    if delta > 0:
        return f"↑ {delta:.3f}s"
    return "±0"


def format_diff_text(report: DiffReport) -> str:
    if not report.entries:
        return "No differences found."
    lines = ["Diff Report", "=" * 40]
    for e in report.entries:
        if e.status == "added":
            tag = "[+]"
            detail = f"duration={e.candidate_duration:.3f}s" if e.candidate_duration is not None else "duration=N/A"
        elif e.status == "removed":
            tag = "[-]"
            detail = f"duration={e.baseline_duration:.3f}s" if e.baseline_duration is not None else "duration=N/A"
        elif e.status == "changed":
            tag = "[~]"
            detail = f"{e.baseline_duration:.3f}s -> {e.candidate_duration:.3f}s {_arrow(e.delta)}"
        else:
            tag = "[ ]"
            detail = f"duration={e.candidate_duration:.3f}s" if e.candidate_duration is not None else "duration=N/A"
        lines.append(f"{tag} {e.job_id}: {detail}")
    lines.append(f"\nSummary: +{len(report.added)} added, -{len(report.removed)} removed, ~{len(report.changed)} changed")
    return "\n".join(lines)


def format_diff_json(report: DiffReport) -> str:
    return json.dumps(report.to_dict(), indent=2)


def format_diff(report: DiffReport, fmt: str = "text") -> str:
    if fmt == "json":
        return format_diff_json(report)
    return format_diff_text(report)
