"""Format flat records for display or export."""

from __future__ import annotations

import csv
import io
import json
from typing import List

from batchmark.flattener import FlatRecord


def format_flat_text(records: List[FlatRecord]) -> str:
    if not records:
        return "No records.\n"
    lines: List[str] = []
    for rec in records:
        dur = f"{rec.duration:.4f}s" if rec.duration is not None else "N/A"
        status = "OK" if rec.success else "FAIL"
        tag_str = ""
        if rec.tags:
            tag_str = "  tags=" + ",".join(f"{k}:{v}" for k, v in sorted(rec.tags.items()))
        lines.append(f"  [{status}] {rec.job_id:<30} {dur}{tag_str}")
    return "\n".join(lines) + "\n"


def format_flat_json(records: List[FlatRecord]) -> str:
    return json.dumps([r.to_dict() for r in records], indent=2)


def format_flat_csv(records: List[FlatRecord]) -> str:
    if not records:
        return ""
    buf = io.StringIO()
    all_dicts = [r.to_dict() for r in records]
    fieldnames = list(all_dicts[0].keys())
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_dicts)
    return buf.getvalue()


def format_flat(records: List[FlatRecord], fmt: str = "text") -> str:
    if fmt == "json":
        return format_flat_json(records)
    if fmt == "csv":
        return format_flat_csv(records)
    return format_flat_text(records)
