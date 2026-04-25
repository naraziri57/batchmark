"""Formatters for PivotReport."""
from __future__ import annotations
import json
from batchmark.pivotter import PivotReport


def format_pivot_text(report: PivotReport) -> str:
    if not report.job_ids:
        return "No pivot data."

    col_w = 14
    header_parts = [f"{'job_id':<20}"] + [f"{pv[:col_w]:>{col_w}}" for pv in report.pivot_values]
    lines = [" ".join(header_parts)]
    lines.append("-" * len(lines[0]))

    for job_id in report.job_ids:
        row = [f"{job_id:<20}"]
        for pv in report.pivot_values:
            cell = report.get(job_id, pv)
            if cell is None:
                row.append(f"{'—':>{col_w}}")
            elif cell.avg_duration is None:
                row.append(f"{'n/a':>{col_w}}")
            else:
                val = f"{cell.avg_duration:.3f}s"
                row.append(f"{val:>{col_w}}")
        lines.append(" ".join(row))

    return "\n".join(lines)


def format_pivot_json(report: PivotReport) -> str:
    return json.dumps(report.to_dict(), indent=2)


def format_pivot(report: PivotReport, fmt: str = "text") -> str:
    if fmt == "json":
        return format_pivot_json(report)
    return format_pivot_text(report)
