"""pruner.py — remove results that fall below a minimum duration or score threshold."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from batchmark.timer import TimingResult


@dataclass
class PruneReport:
    kept: List[TimingResult]
    dropped: List[TimingResult]
    min_duration: Optional[float]
    min_score: Optional[float]

    @property
    def dropped_count(self) -> int:
        return len(self.dropped)

    @property
    def kept_count(self) -> int:
        return len(self.kept)

    def to_dict(self) -> dict:
        return {
            "kept_count": self.kept_count,
            "dropped_count": self.dropped_count,
            "min_duration": self.min_duration,
            "min_score": self.min_score,
            "dropped_job_ids": [r.job_id for r in self.dropped],
        }


def prune_results(
    results: List[TimingResult],
    *,
    min_duration: Optional[float] = None,
    min_score: Optional[float] = None,
    scores: Optional[dict] = None,
) -> PruneReport:
    """Drop results that don't meet minimum thresholds.

    Args:
        results: list of TimingResult to evaluate.
        min_duration: if set, drop results whose duration is below this value
            (results with None duration are always kept unless min_score drops them).
        min_score: if set, drop results whose job_id maps to a score below this
            value in the *scores* dict.  Results not present in scores are kept.
        scores: mapping of job_id -> numeric score, used with min_score.
    """
    kept: List[TimingResult] = []
    dropped: List[TimingResult] = []

    for r in results:
        drop = False

        if min_duration is not None and r.duration is not None:
            if r.duration < min_duration:
                drop = True

        if not drop and min_score is not None and scores:
            job_score = scores.get(r.job_id)
            if job_score is not None and job_score < min_score:
                drop = True

        if drop:
            dropped.append(r)
        else:
            kept.append(r)

    return PruneReport(
        kept=kept,
        dropped=dropped,
        min_duration=min_duration,
        min_score=min_score,
    )
