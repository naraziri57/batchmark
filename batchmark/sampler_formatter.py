"""Format SampleReport for display."""
from __future__ import annotations

import json

from batchmark.sampler import SampleReport


def format_sample_text(report: SampleReport) -> str:
    if not report.results:
        return "No samples."
    lines = [f"Sample: {report.sampled}/{report.total} results"]
    for r in report.results:
        status = "OK" if r.success else "FAIL"
        dur = f"{r.duration:.4f}s" if r.duration is not None else "n/a"
        lines.append(f"  [{status}] {r.job_id}  {dur}")
    return "\n".join(lines)


def format_sample_json(report: SampleReport) -> str:
    return json.dumps(report.to_dict(), indent=2)


def format_sample(report: SampleReport, fmt: str = "text") -> str:
    if fmt == "json":
        return format_sample_json(report)
    return format_sample_text(report)
