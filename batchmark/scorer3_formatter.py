"""Formatters for CompositeReport."""
from __future__ import annotations
import json
from batchmark.scorer3 import CompositeReport


def format_composite_text(report: CompositeReport) -> str:
    if not report.scores:
        return "No composite scores available.\n"
    lines = [f"Composite Scores  (overall: {report.overall():.2f})"]
    lines.append("-" * 60)
    header = f"{'Job':<20} {'Duration':>9} {'Success':>9} {'Consist':>9} {'Score':>9}"
    lines.append(header)
    lines.append("-" * 60)
    for s in sorted(report.scores, key=lambda x: x.composite, reverse=True):
        lines.append(
            f"{s.job_id:<20} {s.duration_score:>9.1f} {s.success_score:>9.1f}"
            f" {s.consistency_score:>9.1f} {s.composite:>9.1f}"
        )
    lines.append("")
    return "\n".join(lines)


def format_composite_json(report: CompositeReport) -> str:
    return json.dumps(report.to_dict(), indent=2)


def format_composite(report: CompositeReport, fmt: str = "text") -> str:
    if fmt == "json":
        return format_composite_json(report)
    return format_composite_text(report)
