"""Deduplicator: remove duplicate TimingResult entries by job_id, keeping the best or latest."""

from typing import List, Literal
from batchmark.timer import TimingResult


Strategy = Literal["latest", "fastest", "first"]


def deduplicate(
    results: List[TimingResult],
    strategy: Strategy = "latest",
) -> List[TimingResult]:
    """Return results with duplicates removed according to *strategy*.

    - ``latest`` – keep the last occurrence of each job_id (default)
    - ``first``  – keep the first occurrence of each job_id
    - ``fastest`` – keep the entry with the lowest duration; entries with
      ``None`` duration are treated as infinitely slow.
    """
    if strategy not in ("latest", "fastest", "first"):
        raise ValueError(f"Unknown deduplication strategy: {strategy!r}")

    seen: dict[str, TimingResult] = {}

    for result in results:
        jid = result.job_id
        if jid not in seen:
            seen[jid] = result
            continue

        if strategy == "latest":
            seen[jid] = result
        elif strategy == "fastest":
            current_dur = seen[jid].duration
            new_dur = result.duration
            if current_dur is None:
                seen[jid] = result
            elif new_dur is not None and new_dur < current_dur:
                seen[jid] = result
        # strategy == "first": do nothing

    # preserve original relative order using insertion-order of seen
    return list(seen.values())


def dedup_stats(original: List[TimingResult], deduped: List[TimingResult]) -> dict:
    """Return a small stats dict describing what was removed."""
    removed = len(original) - len(deduped)
    return {
        "original_count": len(original),
        "deduped_count": len(deduped),
        "removed_count": removed,
        "duplicate_job_ids": sorted(
            {r.job_id for r in original} - {r.job_id for r in original if original.count(r) == 1}
        ),
    }
