"""Format outlier reports as text or JSON."""
from __future__ import annotations
import json
from batchmark.outlier import OutlierReport


def format_outlier_text(report: OutlierReport) -> str:
    if not report.results:
        return "No results to analyze.\n"

    lines = []
    mean_str = f"{report.mean:.4f}s" if report.mean is not None else "n/a"
    stdev_str = f"{report.stdev:.4f}s" if report.stdev is not None else "n/a"
    lines.append(f"Outlier Detection  mean={mean_str}  stdev={stdev_str}")
    lines.append("-" * 56)
    for r in report.results:
        flag = " [OUTLIER]" if r.is_outlier else ""
        dur = f"{r.result.duration:.4f}s" if r.result.duration is not None else "n/a"
        lines.append(
            f"  {r.result.job_id:<24} dur={dur:<12} z={r.z_score:.2f}{flag}"
        )
    lines.append("")
    lines.append(f"Total outliers: {len(report.outliers)} / {len(report.results)}")
    return "\n".join(lines) + "\n"


def format_outlier_json(report: OutlierReport) -> str:
    return json.dumps(report.to_dict(), indent=2)


def format_outlier(report: OutlierReport, fmt: str = "text") -> str:
    if fmt == "json":
        return format_outlier_json(report)
    return format_outlier_text(report)
