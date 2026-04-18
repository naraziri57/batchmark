"""Summarize a list of TimingResult objects into aggregate stats."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from batchmark.timer import TimingResult


@dataclass
class Summary:
    total: int = 0
    succeeded: int = 0
    failed: int = 0
    total_duration: float = 0.0
    min_duration: float = float("inf")
    max_duration: float = float("-inf")
    durations: List[float] = field(default_factory=list, repr=False)

    @property
    def avg_duration(self) -> float:
        if not self.durations:
            return 0.0
        return self.total_duration / len(self.durations)

    @property
    def median_duration(self) -> float:
        if not self.durations:
            return 0.0
        sorted_d = sorted(self.durations)
        mid = len(sorted_d) // 2
        if len(sorted_d) % 2 == 0:
            return (sorted_d[mid - 1] + sorted_d[mid]) / 2
        return sorted_d[mid]

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "succeeded": self.succeeded,
            "failed": self.failed,
            "total_duration_s": round(self.total_duration, 4),
            "min_duration_s": round(self.min_duration, 4) if self.total else None,
            "max_duration_s": round(self.max_duration, 4) if self.total else None,
            "avg_duration_s": round(self.avg_duration, 4),
            "median_duration_s": round(self.median_duration, 4),
        }


def summarize(results: List[TimingResult]) -> Summary:
    """Build a Summary from a list of TimingResult objects."""
    s = Summary()
    for r in results:
        s.total += 1
        if r.success:
            s.succeeded += 1
        else:
            s.failed += 1
        s.total_duration += r.duration
        s.durations.append(r.duration)
        if r.duration < s.min_duration:
            s.min_duration = r.duration
        if r.duration > s.max_duration:
            s.max_duration = r.duration
    return s
