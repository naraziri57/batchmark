"""clamper.py — clamp result durations into a [min, max] range."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from batchmark.timer import TimingResult


@dataclass
class ClampedResult:
    result: TimingResult
    original_duration: Optional[float]
    clamped: bool

    def to_dict(self) -> dict:
        d = self.result.to_dict()
        d["original_duration"] = self.original_duration
        d["clamped"] = self.clamped
        return d


@dataclass
class ClampReport:
    entries: List[ClampedResult] = field(default_factory=list)

    @property
    def clamped_count(self) -> int:
        return sum(1 for e in self.entries if e.clamped)

    @property
    def total(self) -> int:
        return len(self.entries)

    @property
    def clamped_entries(self) -> List[ClampedResult]:
        """Return only the entries whose duration was actually clamped."""
        return [e for e in self.entries if e.clamped]

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "clamped_count": self.clamped_count,
            "entries": [e.to_dict() for e in self.entries],
        }


def clamp_results(
    results: List[TimingResult],
    min_duration: Optional[float] = None,
    max_duration: Optional[float] = None,
) -> ClampReport:
    """Return a ClampReport where each result's duration is clamped to [min_duration, max_duration].

    Results with no duration are left unchanged.

    Args:
        results: List of TimingResult objects to process.
        min_duration: Lower bound for clamping. If None, no lower bound is applied.
        max_duration: Upper bound for clamping. If None, no upper bound is applied.

    Raises:
        ValueError: If min_duration and max_duration are both provided and
            min_duration is greater than max_duration.
    """
    if min_duration is not None and max_duration is not None and min_duration > max_duration:
        raise ValueError(f"min_duration ({min_duration}) must be <= max_duration ({max_duration})")

    entries: List[ClampedResult] = []
    for r in results:
        original = r.duration
        if original is None:
            entries.append(ClampedResult(result=r, original_duration=None, clamped=False))
            continue

        new_duration = original
        if min_duration is not None:
            new_duration = max(new_duration, min_duration)
        if max_duration is not None:
            new_duration = min(new_duration, max_duration)

        clamped = new_duration != original
        new_result = TimingResult(
            job_id=r.job_id,
            duration=new_duration,
            success=r.success,
            error=r.error,
        )
        entries.append(ClampedResult(result=new_result, original_duration=original, clamped=clamped))

    return ClampReport(entries=entries)
