"""Composite scorer: combines duration, success rate, and consistency into one score."""
from __future__ import annotations
from dataclasses import dataclass, field
from statistics import stdev
from typing import List, Optional
from batchmark.timer import TimingResult


@dataclass
class CompositeScore:
    job_id: str
    duration_score: float   # 0-100, lower duration = higher score
    success_score: float    # 0 or 100
    consistency_score: float  # 0-100, lower stdev = higher score
    composite: float        # weighted average

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "duration_score": round(self.duration_score, 2),
            "success_score": round(self.success_score, 2),
            "consistency_score": round(self.consistency_score, 2),
            "composite": round(self.composite, 2),
        }


@dataclass
class CompositeReport:
    scores: List[CompositeScore] = field(default_factory=list)

    def overall(self) -> Optional[float]:
        if not self.scores:
            return None
        return round(sum(s.composite for s in self.scores) / len(self.scores), 2)

    def to_dict(self) -> dict:
        return {
            "overall": self.overall(),
            "scores": [s.to_dict() for s in self.scores],
        }


def _duration_score(duration: Optional[float], max_duration: float) -> float:
    if duration is None or max_duration == 0:
        return 0.0
    return max(0.0, 100.0 * (1.0 - duration / max_duration))


def _consistency_score(durations: List[float]) -> float:
    if len(durations) < 2:
        return 100.0
    mean = sum(durations) / len(durations)
    if mean == 0:
        return 100.0
    cv = stdev(durations) / mean  # coefficient of variation
    return max(0.0, 100.0 * (1.0 - min(cv, 1.0)))


def score_composite(
    results: List[TimingResult],
    weights: Optional[dict] = None,
) -> CompositeReport:
    """Score results grouped by job_id using duration, success, and consistency."""
    if weights is None:
        weights = {"duration": 0.4, "success": 0.4, "consistency": 0.2}

    from collections import defaultdict
    groups: dict = defaultdict(list)
    for r in results:
        groups[r.job_id].append(r)

    all_durations = [r.duration for r in results if r.duration is not None]
    max_dur = max(all_durations) if all_durations else 0.0

    scores = []
    for job_id, job_results in sorted(groups.items()):
        durations = [r.duration for r in job_results if r.duration is not None]
        successes = [r for r in job_results if r.success]

        avg_dur = sum(durations) / len(durations) if durations else None
        d_score = _duration_score(avg_dur, max_dur)
        s_score = 100.0 * len(successes) / len(job_results) if job_results else 0.0
        c_score = _consistency_score(durations)

        composite = (
            weights["duration"] * d_score
            + weights["success"] * s_score
            + weights["consistency"] * c_score
        )
        scores.append(CompositeScore(job_id, d_score, s_score, c_score, composite))

    return CompositeReport(scores=scores)
