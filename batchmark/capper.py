"""Cap (clamp) result durations to a maximum value, flagging those that exceeded the cap."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from batchmark.timer import TimingResult


@dataclass
class CappedResult:
    result: TimingResult
    original_duration: Optional[float]
    capped: bool

    def to_dict(self) -> dict:
        d = self.result.to_dict()
        d["original_duration"] = (
            round(self.original_duration, 4) if self.original_duration is not None else None
        )
        d["capped"] = self.capped
        return d


@dataclass
class CapReport:
    results: List[CappedResult] = field(default_factory=list)

    @property
    def capped_count(self) -> int:
        return sum(1 for r in self.results if r.capped)

    @property
    def total(self) -> int:
        return len(self.results)

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "capped_count": self.capped_count,
            "results": [r.to_dict() for r in self.results],
        }


def cap_results(
    results: List[TimingResult],
    max_duration: float,
    per_job: Optional[dict] = None,
) -> CapReport:
    """Clamp durations to *max_duration* (or a per-job override).

    Args:
        results: list of TimingResult objects.
        max_duration: global ceiling in seconds.
        per_job: optional mapping of job_id -> ceiling that overrides the global value.

    Returns:
        CapReport with each result wrapped in a CappedResult.
    """
    per_job = per_job or {}
    capped: List[CappedResult] = []

    for r in results:
        limit = per_job.get(r.job_id, max_duration)
        original = r.duration
        if original is not None and original > limit:
            # Build a new TimingResult with the clamped duration
            clipped = TimingResult(
                job_id=r.job_id,
                duration=limit,
                success=r.success,
                error=r.error,
            )
            capped.append(CappedResult(result=clipped, original_duration=original, capped=True))
        else:
            capped.append(CappedResult(result=r, original_duration=original, capped=False))

    return CapReport(results=capped)
