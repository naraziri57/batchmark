"""Format segmenter output as text or JSON."""
from __future__ import annotations
import json
from typing import List
from batchmark.segmenter import Segment


def format_segment_text(segments: List[Segment]) -> str:
    if not segments:
        return "No segments."
    lines = ["Segments:", ""]
    for seg in segments:
        avg = seg.avg_duration()
        avg_str = f"{avg:.4f}s" if avg is not None else "n/a"
        lines.append(
            f"  [{seg.label}]  count={seg.count()}  "
            f"success={seg.success_count()}  avg={avg_str}"
        )
    return "\n".join(lines)


def format_segment_json(segments: List[Segment]) -> str:
    return json.dumps([s.to_dict() for s in segments], indent=2)


def format_segment(segments: List[Segment], fmt: str = "text") -> str:
    if fmt == "json":
        return format_segment_json(segments)
    return format_segment_text(segments)
