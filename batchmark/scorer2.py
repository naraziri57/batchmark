"""Weighted multi-metric scorer for batch job results."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from batchmark.timer import TimingResult


@dataclass
class WeightedScore:
    job_id: str
    duration_score: float
    success_score: float
    weighted_total: float
    tags: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "duration_score": round(self.duration_score, 4),
            "success_score": round(self.success_score, 4),
            "weighted_total": round(self.weighted_total, 4),
            "tags": {k: round(v, 4) for k, v in self.tags.items()},
        }


@dataclass
class WeightedScoringReport:
    scores: List[WeightedScore] = field(default_factory=list)

    def overall(self) -> Optional[float]:
        if not self.scores:
            return None
        return sum(s.weighted_total for s in self.scores) / len(self.scores)

    def to_dict(self) -> dict:
        return {
            "scores": [s.to_dict() for s in self.scores],
            "overall": self.overall(),
        }


def weighted_score(
    results: List[TimingResult],
    duration_weight: float = 0.6,
    success_weight: float = 0.4,
    baseline_durations: Optional[Dict[str, float]] = None,
) -> WeightedScoringReport:
    if not results:
        return WeightedScoringReport()

    valid_durations = [r.duration for r in results if r.duration is not None]
    max_dur = max(valid_durations) if valid_durations else None

    scores = []
    for r in results:
        if r.duration is not None and max_dur and max_dur > 0:
            dur_score = 1.0 - (r.duration / max_dur)
        else:
            dur_score = 0.0

        suc_score = 1.0 if r.success else 0.0
        total = duration_weight * dur_score + success_weight * suc_score

        extra: Dict[str, float] = {}
        if baseline_durations and r.job_id in baseline_durations:
            base = baseline_durations[r.job_id]
            if base and r.duration is not None:
                extra["vs_baseline"] = max(0.0, 1.0 - r.duration / base)

        scores.append(
            WeightedScore(
                job_id=r.job_id,
                duration_score=dur_score,
                success_score=suc_score,
                weighted_total=total,
                tags=extra,
            )
        )

    return WeightedScoringReport(scores=scores)
