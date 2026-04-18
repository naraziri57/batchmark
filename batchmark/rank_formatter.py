"""Format ranked results for display."""

import json
from typing import List
from batchmark.ranker import RankedResult


def format_rank_text(ranked: List[RankedResult]) -> str:
    if not ranked:
        return "No results to rank.\n"

    lines = ["Ranking Report", "=" * 40]
    for r in ranked:
        dur = f"{r.result.duration:.3f}s" if r.result.duration is not None else "N/A"
        status = "OK" if r.result.success else "FAIL"
        lines.append(
            f"#{r.rank:>3}  {r.result.job_id:<20}  score={r.score:.4f}  "
            f"dur={dur}  [{status}]"
        )
    lines.append("")
    return "\n".join(lines)


def format_rank_json(ranked: List[RankedResult]) -> str:
    return json.dumps([r.to_dict() for r in ranked], indent=2)


def format_rank(ranked: List[RankedResult], fmt: str = "text") -> str:
    if fmt == "json":
        return format_rank_json(ranked)
    return format_rank_text(ranked)
