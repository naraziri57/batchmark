"""Text / JSON formatters for BucketReport."""
from __future__ import annotations
import json
from batchmark.bucketer import BucketReport


def format_bucket_text(report: BucketReport) -> str:
    if not report.buckets:
        return "No buckets."
    lines = ["Duration Buckets", "=" * 40]
    for b in report.buckets:
        s = b.summary
        if s:
            avg = f"{s.avg_duration:.3f}s" if s.avg_duration is not None else "n/a"
            lines.append(
                f"  [{b.label}]  count={b.count}  "
                f"ok={s.success_count}  fail={s.failure_count}  avg={avg}"
            )
        else:
            lines.append(f"  [{b.label}]  count=0")
    return "\n".join(lines)


def format_bucket_json(report: BucketReport) -> str:
    return json.dumps(report.to_dict(), indent=2)


def format_bucket(report: BucketReport, fmt: str = "text") -> str:
    if fmt == "json":
        return format_bucket_json(report)
    return format_bucket_text(report)
