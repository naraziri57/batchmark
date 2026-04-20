"""Format MergeReport as text or JSON."""
from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from batchmark.merger import MergeReport


def format_merge_text(report: "MergeReport") -> str:
    lines: list[str] = []
    lines.append("=== Merge Report ===")
    lines.append(f"Sources  : {', '.join(report.source_labels)}")
    lines.append(f"Total    : {report.total()}")
    lines.append(f"Conflicts: {report.conflict_count()}")
    if report.conflicts:
        lines.append("Conflicting job IDs:")
        for jid in report.conflicts:
            lines.append(f"  - {jid}")
    return "\n".join(lines)


def format_merge_json(report: "MergeReport") -> str:
    payload = report.to_dict()
    payload["results"] = [
        {
            "job_id": r.job_id,
            "success": r.success,
            "duration": r.duration,
            "error": r.error,
        }
        for r in report.results
    ]
    return json.dumps(payload, indent=2)


def format_merge(report: "MergeReport", fmt: str = "text") -> str:
    if fmt == "json":
        return format_merge_json(report)
    return format_merge_text(report)
