"""funneler_formatter.py — render FunnelReport as text or JSON."""
from __future__ import annotations
import json
from batchmark.funneler import FunnelReport


def format_funnel_text(report: FunnelReport) -> str:
    if not report.steps:
        return "No funnel stages."
    lines = ["Funnel stages:"]
    for step in report.steps:
        lines.append(
            f"  {step.stage}: passed={step.passed}  dropped={step.dropped}"
        )
    lines.append(f"Final count : {len(report.final_results)}")
    lines.append(f"Total dropped: {report.total_dropped}")
    return "\n".join(lines)


def format_funnel_json(report: FunnelReport) -> str:
    return json.dumps(report.to_dict(), indent=2)


def format_funnel(report: FunnelReport, fmt: str = "text") -> str:
    if fmt == "json":
        return format_funnel_json(report)
    return format_funnel_text(report)
