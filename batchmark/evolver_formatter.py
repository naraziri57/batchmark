"""evolver_formatter.py — text and JSON rendering for EvolverReport."""
from __future__ import annotations

import json

from batchmark.evolver import EvolverReport


def _fmt_dur(d: float | None) -> str:
    return f"{d:.3f}s" if d is not None else "  n/a "


def format_evolver_text(report: EvolverReport) -> str:
    if not report.jobs:
        return "(no evolution data)\n"

    col_w = 10
    header_parts = [f"{'job_id':<24}"] + [
        f"{label:>{col_w}}" for label in report.run_labels
    ] + [f"{'net_change':>{col_w}}"]  
    lines = ["".join(header_parts)]
    lines.append("-" * len(lines[0]))

    for job in report.jobs:
        row = [f"{job.job_id:<24}"]
        for dur in job.durations:
            row.append(f"{_fmt_dur(dur):>{col_w}}")
        nc = job.net_change()
        if nc is None:
            nc_str = "  n/a "
        elif nc < 0:
            nc_str = f"-{abs(nc):.3f}s"
        else:
            nc_str = f"+{nc:.3f}s"
        row.append(f"{nc_str:>{col_w}}")
        lines.append("".join(row))

    return "\n".join(lines) + "\n"


def format_evolver_json(report: EvolverReport) -> str:
    return json.dumps(report.to_dict(), indent=2)


def format_evolver(report: EvolverReport, fmt: str = "text") -> str:
    if fmt == "json":
        return format_evolver_json(report)
    return format_evolver_text(report)
