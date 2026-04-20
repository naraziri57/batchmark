"""Format PartitionReport as text, JSON, or CSV."""
from __future__ import annotations

import json
from typing import List

from batchmark.partitioner import PartitionReport


def format_partition_text(report: PartitionReport) -> str:
    if not report.partitions:
        return "No partitions."
    lines: List[str] = []
    for p in report.partitions:
        s = p.summary
        avg = f"{s.avg_duration:.3f}s" if s.avg_duration is not None else "n/a"
        med = f"{s.median_duration:.3f}s" if s.median_duration is not None else "n/a"
        lines.append(
            f"[{p.label}] count={len(p.results)} "
            f"ok={s.success_count} fail={s.failure_count} "
            f"avg={avg} median={med}"
        )
    return "\n".join(lines)


def format_partition_json(report: PartitionReport) -> str:
    return json.dumps(report.to_dict(), indent=2)


def format_partition_csv(report: PartitionReport) -> str:
    rows = ["label,count,success,failure,avg_duration,median_duration"]
    for p in report.partitions:
        s = p.summary
        avg = f"{s.avg_duration:.6f}" if s.avg_duration is not None else ""
        med = f"{s.median_duration:.6f}" if s.median_duration is not None else ""
        rows.append(
            f"{p.label},{len(p.results)},{s.success_count},{s.failure_count},{avg},{med}"
        )
    return "\n".join(rows)


def format_partition(
    report: PartitionReport, fmt: str = "text"
) -> str:
    if fmt == "json":
        return format_partition_json(report)
    if fmt == "csv":
        return format_partition_csv(report)
    return format_partition_text(report)
