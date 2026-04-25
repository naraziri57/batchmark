"""Format ClassificationReport as text, JSON, or CSV."""
from __future__ import annotations

import csv
import io
import json

from batchmark.classifier import ClassificationReport


def format_classifier_text(report: ClassificationReport) -> str:
    if not report.classified:
        return "No classified results."
    lines = ["Classification Report", "=" * 40]
    for cat, items in sorted(report.by_category().items()):
        lines.append(f"[{cat}] ({len(items)} results)")
        for cr in items:
            dur = f"{cr.result.duration:.4f}s" if cr.result.duration is not None else "n/a"
            status = "OK" if cr.result.success else "FAIL"
            lines.append(f"  {cr.result.job_id:<30} {status:<6} {dur}")
    return "\n".join(lines)


def format_classifier_json(report: ClassificationReport) -> str:
    return json.dumps(report.to_dict(), indent=2)


def format_classifier_csv(report: ClassificationReport) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["job_id", "category", "success", "duration"])
    for cr in report.classified:
        writer.writerow([
            cr.result.job_id,
            cr.category,
            cr.result.success,
            cr.result.duration if cr.result.duration is not None else "",
        ])
    return buf.getvalue()


def format_classifier(report: ClassificationReport, fmt: str = "text") -> str:
    if fmt == "json":
        return format_classifier_json(report)
    if fmt == "csv":
        return format_classifier_csv(report)
    return format_classifier_text(report)
