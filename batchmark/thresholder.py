"""Threshold checking: flag results that exceed duration limits."""

from dataclasses import dataclass, field
from typing import Optional, List
from batchmark.timer import TimingResult


@dataclass
class ThresholdViolation:
    job_id: str
    duration: Optional[float]
    threshold: float
    message: str

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "duration": self.duration,
            "threshold": self.threshold,
            "message": self.message,
        }


@dataclass
class ThresholdReport:
    violations: List[ThresholdViolation] = field(default_factory=list)

    @property
    def has_violations(self) -> bool:
        return len(self.violations) > 0

    def to_dict(self) -> dict:
        return {
            "has_violations": self.has_violations,
            "violations": [v.to_dict() for v in self.violations],
        }


def check_thresholds(
    results: List[TimingResult],
    global_threshold: Optional[float] = None,
    per_job_thresholds: Optional[dict] = None,
) -> ThresholdReport:
    """Check results against duration thresholds.

    Args:
        results: list of TimingResult to check
        global_threshold: max allowed duration in seconds for all jobs
        per_job_thresholds: dict mapping job_id to max allowed duration
    """
    per_job_thresholds = per_job_thresholds or {}
    violations = []

    for r in results:
        limit = per_job_thresholds.get(r.job_id, global_threshold)
        if limit is None:
            continue
        duration = r.duration
        if duration is None:
            continue
        if duration > limit:
            violations.append(
                ThresholdViolation(
                    job_id=r.job_id,
                    duration=duration,
                    threshold=limit,
                    message=f"{r.job_id} took {duration:.3f}s, exceeds limit of {limit:.3f}s",
                )
            )

    return ThresholdReport(violations=violations)
