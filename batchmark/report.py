import json
import csv
import io
from typing import Literal
from batchmark.timer import JobTimer


ReportFormat = Literal["json", "csv", "text"]


def render_report(timer: JobTimer, fmt: ReportFormat = "text") -> str:
    if fmt == "json":
        return _render_json(timer)
    elif fmt == "csv":
        return _render_csv(timer)
    else:
        return _render_text(timer)


def _render_json(timer: JobTimer) -> str:
    payload = {
        "summary": timer.summary(),
        "jobs": [r.to_dict() for r in timer.results()],
    }
    return json.dumps(payload, indent=2)


def _render_csv(timer: JobTimer) -> str:
    results = timer.results()
    if not results:
        return ""
    buf = io.StringIO()
    fieldnames = ["name", "elapsed", "success", "error"]
    writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for r in results:
        writer.writerow(r.to_dict())
    return buf.getvalue()


def _render_text(timer: JobTimer) -> str:
    lines = []
    summary = timer.summary()
    lines.append("=== batchmark report ===")
    lines.append(f"  jobs      : {summary.get('completed', 0)}/{summary.get('total_jobs', 0)}")
    lines.append(f"  failed    : {summary.get('failed', 0)}")
    lines.append(f"  total     : {summary.get('total_elapsed', 0.0):.4f}s")
    if summary.get("completed", 0) > 0:
        lines.append(f"  avg       : {summary.get('avg_elapsed', 0.0):.4f}s")
        lines.append(f"  min/max   : {summary.get('min_elapsed', 0.0):.4f}s / {summary.get('max_elapsed', 0.0):.4f}s")
    lines.append("")
    lines.append(f"{'JOB':<30} {'ELAPSED':>10} {'STATUS':>8}")
    lines.append("-" * 52)
    for r in timer.results():
        status = "OK" if r.success else "FAIL"
        elapsed_str = f"{r.elapsed:.4f}s" if r.elapsed is not None else "--"
        lines.append(f"{r.name:<30} {elapsed_str:>10} {status:>8}")
    return "\n".join(lines)
