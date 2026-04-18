"""Rank timing results by a composite score across multiple criteria."""

from dataclasses import dataclass, field
from typing import List, Optional
from batchmark.timer import TimingResult


@dataclass
class RankedResult:
    result: TimingResult
    rank: int
    score: float
    breakdown: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "rank": self.rank,
            "job_id": self.result.job_id,
            "score": round(self.score, 4),
            "duration": self.result.duration,
            "success": self.result.success,
            "breakdown": self.breakdown,
        }


def _duration_score(result: TimingResult, max_duration: float) -> float:
    """Lower duration => higher score (0.0 to 1.0)."""
    if result.duration is None or max_duration == 0:
        return 0.0
    return 1.0 - (result.duration / max_duration)


def rank_results(
    results: List[TimingResult],
    success_bonus: float = 0.3,
    duration_weight: float = 0.7,
) -> List[RankedResult]:
    """Rank results by weighted score of duration and success status."""
    if not results:
        return []

    durations = [r.duration for r in results if r.duration is not None]
    max_dur = max(durations) if durations else 1.0

    scored = []
    for r in results:
        dur_score = _duration_score(r, max_dur) * duration_weight
        suc_score = success_bonus if r.success else 0.0
        total = dur_score + suc_score
        scored.append((r, total, {"duration_score": round(dur_score, 4), "success_bonus": round(suc_score, 4)}))

    scored.sort(key=lambda x: x[1], reverse=True)

    return [
        RankedResult(result=r, rank=i + 1, score=s, breakdown=b)
        for i, (r, s, b) in enumerate(scored)
    ]
