"""Summarize tagged results grouped by a given tag key."""
import json
from typing import Any, Dict, List, Optional
from batchmark.tagger import TaggedResult
from batchmark.summary import summarize


def group_by_tag(
    tagged: List[TaggedResult],
    tag_key: str,
) -> Dict[Any, List[TaggedResult]]:
    """Group TaggedResults by the value of tag_key."""
    groups: Dict[Any, List[TaggedResult]] = {}
    for t in tagged:
        val = t.tags.get(tag_key)
        groups.setdefault(val, []).append(t)
    return groups


def summarize_by_tag(
    tagged: List[TaggedResult],
    tag_key: str,
) -> Dict[Any, Dict[str, Any]]:
    """Return a summary dict keyed by tag value."""
    groups = group_by_tag(tagged, tag_key)
    return {
        val: summarize([t.result for t in items]).to_dict()
        for val, items in groups.items()
    }


def format_tag_report_text(
    tagged: List[TaggedResult],
    tag_key: str,
) -> str:
    summaries = summarize_by_tag(tagged, tag_key)
    if not summaries:
        return f"No results for tag '{tag_key}'."
    lines = [f"Tag report — key: {tag_key}"]
    for val, s in sorted(summaries.items(), key=lambda x: str(x[0])):
        lines.append(
            f"  [{val}] total={s['total']} success={s['success']} "
            f"failed={s['failed']} avg={s.get('avg_duration', 'N/A'):.3f}s "
            f"median={s.get('median_duration', 'N/A'):.3f}s"
        )
    return "\n".join(lines)


def format_tag_report_json(
    tagged: List[TaggedResult],
    tag_key: str,
) -> str:
    summaries = summarize_by_tag(tagged, tag_key)
    return json.dumps({str(k): v for k, v in summaries.items()}, indent=2)


def format_tag_report(tagged: List[TaggedResult], tag_key: str, fmt: str = "text") -> str:
    if fmt == "json":
        return format_tag_report_json(tagged, tag_key)
    return format_tag_report_text(tagged, tag_key)
