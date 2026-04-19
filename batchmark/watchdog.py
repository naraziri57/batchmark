"""Watchdog: enforce per-job time limits and collect timeout violations."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from batchmark.timer import TimingResult


@dataclass
class TimeoutViolation:
    job_id: str
    duration: Optional[float]
    limit: float

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "duration": self.duration,
            "limit": self.limit,
        }


@dataclass
class WatchdogReport:
    violations: List[TimeoutViolation] = field(default_factory=list)

    @property
    def has_violations(self) -> bool:
        return len(self.violations) > 0

    def to_dict(self) -> dict:
        return {
            "has_violations": self.has_violations,
            "violations": [v.to_dict() for v in self.violations],
        }


def check_timeouts(
    results: List[TimingResult],
    global_limit: Optional[float] = None,
    per_job_limits: Optional[Dict[str, float]] = None,
) -> WatchdogReport:
    """Check results against time limits and return a WatchdogReport."""
    per_job_limits = per_job_limits or {}
    violations: List[TimeoutViolation] = []

    for r in results:
        limit = per_job_limits.get(r.job_id, global_limit)
        if limit is None:
            continue
        if r.duration is not None and r.duration > limit:
            violations.append(TimeoutViolation(r.job_id, r.duration, limit))

    return WatchdogReport(violations=violations)
