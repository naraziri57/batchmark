"""shrinker.py — drop results that exceed a max count per job_id, keeping the N most recent."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from batchmark.timer import TimingResult


@dataclass
class ShrinkReport:
    kept: List[TimingResult]
    dropped: List[TimingResult]
    per_job_dropped: Dict[str, int] = field(default_factory=dict)

    @property
    def total(self) -> int:
        return len(self.kept) + len(self.dropped)

    @property
    def dropped_count(self) -> int:
        return len(self.dropped)

    @property
    def kept_count(self) -> int:
        return len(self.kept)

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "kept": self.kept_count,
            "dropped": self.dropped_count,
            "per_job_dropped": self.per_job_dropped,
        }


def shrink_results(
    results: List[TimingResult],
    max_per_job: Optional[int] = None,
    keep: str = "latest",
) -> ShrinkReport:
    """Limit results to *max_per_job* entries per job_id.

    Args:
        results: flat list of TimingResult.
        max_per_job: maximum number of results to keep per job_id.
                     None means keep everything.
        keep: 'latest' keeps the last N (by list order), 'earliest' keeps the first N.
    """
    if max_per_job is None or max_per_job < 0:
        return ShrinkReport(kept=list(results), dropped=[], per_job_dropped={})

    if keep not in ("latest", "earliest"):
        raise ValueError(f"keep must be 'latest' or 'earliest', got {keep!r}")

    grouped: Dict[str, List[TimingResult]] = {}
    for r in results:
        grouped.setdefault(r.job_id, []).append(r)

    kept: List[TimingResult] = []
    dropped: List[TimingResult] = []
    per_job_dropped: Dict[str, int] = {}

    for job_id, items in grouped.items():
        if len(items) <= max_per_job:
            kept.extend(items)
        else:
            if keep == "latest":
                keep_items = items[-max_per_job:]
                drop_items = items[: len(items) - max_per_job]
            else:
                keep_items = items[:max_per_job]
                drop_items = items[max_per_job:]
            kept.extend(keep_items)
            dropped.extend(drop_items)
            per_job_dropped[job_id] = len(drop_items)

    return ShrinkReport(kept=kept, dropped=dropped, per_job_dropped=per_job_dropped)
