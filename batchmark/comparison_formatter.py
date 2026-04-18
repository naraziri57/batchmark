"""Render a ComparisonReport as text or JSON."""

import json
from batchmark.comparator import ComparisonReport


def _fmt(val: float | None, decimals: int = 3) -> str:
    if val is None:
        return "N/A"
    return f"{val:.{decimals}f}"


def format_comparison_text(report: ComparisonReport) -> str:
    if not report.comparisons:
        return "No comparisons available.\n"

    lines = [
        f"{'Job ID':<30} {'Baseline':>10} {'Candidate':>10} {'Delta':>10} {'Change':>10}",
        "-" * 74,
    ]
    for c in report.comparisons:
        change = _fmt(c.pct_change, 1) + "%" if c.pct_change is not None else "N/A"
        arrow = ""
        if c.improved is True:
            arrow = " ↓"
        elif c.improved is False:
            arrow = " ↑"
        lines.append(
            f"{c.job_id:<30} {_fmt(c.baseline_avg):>10} {_fmt(c.candidate_avg):>10}"
            f" {_fmt(c.delta):>10} {change:>10}{arrow}"
        )
    return "\n".join(lines) + "\n"


def format_comparison_json(report: ComparisonReport) -> str:
    return json.dumps(report.to_dict(), indent=2)


def format_comparison(report: ComparisonReport, fmt: str = "text") -> str:
    if fmt == "json":
        return format_comparison_json(report)
    return format_comparison_text(report)
