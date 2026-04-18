"""Format aggregated results into human-readable or structured output."""

import json
from typing import Dict
from batchmark.summary import Summary


def format_aggregation_text(agg: Dict[str, Summary]) -> str:
    """Render aggregated summaries as plain text."""
    if not agg:
        return "No results to display.\n"
    lines = []
    for job_id, summary in sorted(agg.items()):
        avg = f"{summary.avg_duration():.4f}s" if summary.avg_duration() is not None else "N/A"
        med = f"{summary.median_duration():.4f}s" if summary.median_duration() is not None else "N/A"
        lines.append(
            f"[{job_id}] total={summary.total} "
            f"ok={summary.success_count} fail={summary.failure_count} "
            f"avg={avg} median={med}"
        )
    return "\n".join(lines) + "\n"


def format_aggregation_json(agg: Dict[str, Summary]) -> str:
    """Render aggregated summaries as JSON."""
    data = {job_id: summary.to_dict() for job_id, summary in agg.items()}
    return json.dumps(data, indent=2)


def format_aggregation(agg: Dict[str, Summary], fmt: str = "text") -> str:
    """Dispatch to the correct formatter."""
    if fmt == "json":
        return format_aggregation_json(agg)
    return format_aggregation_text(agg)
