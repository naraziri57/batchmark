"""Formatters for ZipReport output."""
from __future__ import annotations
import json
from batchmark.zipper import ZipReport


def _arrow(delta: float | None) -> str:
    if delta is None:
        return "?"
    if delta < 0:
        return f"▼ {abs(delta):.4f}s"
    if delta > 0:
        return f"▲ {delta:.4f}s"
    return "= 0.0000s"


def format_zip_text(report: ZipReport) -> str:
    if not report.pairs:
        return "No pairs to display."
    lines = [f"{'JOB ID':<30} {'LEFT':>10} {'RIGHT':>10} {'DELTA':>14}"]
    lines.append("-" * 68)
    for p in report.pairs:
        left_s = f"{p.left_duration:.4f}s" if p.left_duration is not None else "--"
        right_s = f"{p.right_duration:.4f}s" if p.right_duration is not None else "--"
        arrow = _arrow(p.delta)
        lines.append(f"{p.job_id:<30} {left_s:>10} {right_s:>10} {arrow:>14}")
    lines.append("-" * 68)
    lines.append(
        f"Matched: {len(report.matched)}  "
        f"Left only: {len(report.only_in_left)}  "
        f"Right only: {len(report.only_in_right)}"
    )
    return "\n".join(lines)


def format_zip_json(report: ZipReport) -> str:
    return json.dumps(report.to_dict(), indent=2)


def format_zip(report: ZipReport, fmt: str = "text") -> str:
    if fmt == "json":
        return format_zip_json(report)
    return format_zip_text(report)
