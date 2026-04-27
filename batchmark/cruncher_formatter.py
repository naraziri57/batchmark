"""cruncher_formatter.py — text/json formatting for CrunchReport."""
from __future__ import annotations

import json
from typing import Optional

from batchmark.cruncher import CrunchReport


def _fmt(val: Optional[float]) -> str:
    return f"{val:.4f}s" if val is not None else "n/a"


def format_crunch_text(report: CrunchReport) -> str:
    if not report.jobs:
        return "no data"
    lines = []
    header = f"{'job_id':<24} {'count':>6} {'ok':>5} {'fail':>5} {'min':>10} {'max':>10} {'mean':>10} {'p50':>10} {'p95':>10} {'stdev':>10}"
    lines.append(header)
    lines.append("-" * len(header))
    for j in report.jobs:
        lines.append(
            f"{j.job_id:<24} {j.count:>6} {j.success_count:>5} {j.failure_count:>5}"
            f" {_fmt(j.min_duration):>10} {_fmt(j.max_duration):>10}"
            f" {_fmt(j.mean_duration):>10} {_fmt(j.p50):>10} {_fmt(j.p95):>10}"
            f" {_fmt(j.stdev_duration):>10}"
        )
    return "\n".join(lines)


def format_crunch_json(report: CrunchReport) -> str:
    return json.dumps(report.to_dict(), indent=2)


def format_crunch(report: CrunchReport, fmt: str = "text") -> str:
    if fmt == "json":
        return format_crunch_json(report)
    return format_crunch_text(report)
