"""binner_formatter.py — text/json formatting for BinReport."""
from __future__ import annotations
import json
from batchmark.binner import BinReport


def format_bin_text(report: BinReport) -> str:
    if not report.bins or report.total == 0:
        return "No binned results.\n"

    lines = [f"Bin width: {report.bin_width}s  |  Total results: {report.total}"]
    lines.append("-" * 52)
    for b in report.bins:
        if b.count == 0:
            continue
        avg = f"{b.avg_duration:.3f}s" if b.avg_duration is not None else "N/A"
        bar = "#" * min(b.count, 40)
        lines.append(
            f"{b.label:<18}  count={b.count:>4}  ok={b.success_count:>4}  avg={avg:>8}  {bar}"
        )
    return "\n".join(lines) + "\n"


def format_bin_json(report: BinReport) -> str:
    return json.dumps(report.to_dict(), indent=2)


def format_bin(report: BinReport, fmt: str = "text") -> str:
    if fmt == "json":
        return format_bin_json(report)
    return format_bin_text(report)
