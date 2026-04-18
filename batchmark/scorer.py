"""Score timing results against a baseline using a simple weighted formula."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from batchmark.timer import TimingResult


@dataclass
class JobScore:
    job_id: str
    score: float  # 0.0 (worst) to 1.0 (best)
    duration: Optional[float]
    baseline_duration: Optional[float]
    penalty: float = 0.0
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "score": round(self.score, 4),
            "duration": self.duration,
            "baseline_duration": self.baseline_duration,
            "penalty": round(self.penalty, 4),
            "notes": self.notes,
        }


@dataclass
class ScoringReport:
    scores: List[JobScore] = field(default_factory=list)

    @property
    def overall(self) -> float:
        if not self.scores:
            return 0.0
        return round(sum(s.score for s in self.scores) / len(self.scores), 4)

    def to_dict(self) -> dict:
        return {
            "overall": self.overall,
            "jobs": [s.to_dict() for s in self.scores],
        }


def score_results(
    results: List[TimingResult],
    baselines: Dict[str, float],
    failure_penalty: float = 0.5,
    regression_weight: float = 1.0,
) -> ScoringReport:
    """Score each result relative to baseline durations."""
    report = ScoringReport()

    for r in results:
        notes: List[str] = []
        penalty = 0.0
        baseline = baselines.get(r.job_id)

        if not r.success:
            score = max(0.0, 1.0 - failure_penalty)
            penalty = failure_penalty
            notes.append("job failed")
        elif r.duration is None:
            score = 0.5
            notes.append("no duration recorded")
        elif baseline is None:
            score = 1.0
            notes.append("no baseline available")
        else:
            ratio = r.duration / baseline
            raw_penalty = max(0.0, ratio - 1.0) * regression_weight
            penalty = min(raw_penalty, 1.0)
            score = round(max(0.0, 1.0 - penalty), 4)
            if ratio > 1.0:
                notes.append(f"regression: {ratio:.2f}x baseline")
            elif ratio < 1.0:
                notes.append(f"improvement: {ratio:.2f}x baseline")

        report.scores.append(
            JobScore(
                job_id=r.job_id,
                score=score,
                duration=r.duration,
                baseline_duration=baseline,
                penalty=penalty,
                notes=notes,
            )
        )

    return report
