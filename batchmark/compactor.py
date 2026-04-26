"""Compactor: reduce a list of TimingResults by merging runs of the same
job_id into a single representative result (e.g. best, worst, or mean)."""
from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean
from typing import Callable, Dict, List, Literal, Optional

from batchmark.timer import TimingResult

Strategy = Literal["best", "worst", "mean", "first", "last"]


@dataclass
class CompactedResult:
    job_id: str
    duration: Optional[float]
    success: bool
    source_count: int
    strategy: str
    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "duration": self.duration,
            "success": self.success,
            "source_count": self.source_count,
            "strategy": self.strategy,
            "tags": self.tags,
        }


@dataclass
class CompactReport:
    results: List[CompactedResult]
    strategy: str

    @property
    def total(self) -> int:
        return len(self.results)

    def to_dict(self) -> dict:
        return {
            "strategy": self.strategy,
            "total": self.total,
            "results": [r.to_dict() for r in self.results],
        }


def _pick(durations: List[float], strategy: Strategy) -> Optional[float]:
    if not durations:
        return None
    if strategy == "best":
        return min(durations)
    if strategy == "worst":
        return max(durations)
    if strategy == "mean":
        return mean(durations)
    # first / last handled outside
    return durations[0]


def compact_results(
    results: List[TimingResult],
    strategy: Strategy = "best",
) -> CompactReport:
    """Merge multiple results for the same job_id into one CompactedResult."""
    groups: Dict[str, List[TimingResult]] = {}
    for r in results:
        groups.setdefault(r.job_id, []).append(r)

    compacted: List[CompactedResult] = []
    for job_id, group in groups.items():
        durations = [r.duration for r in group if r.duration is not None]
        any_success = any(r.success for r in group)

        if strategy == "first":
            rep = group[0]
            duration = rep.duration
        elif strategy == "last":
            rep = group[-1]
            duration = rep.duration
        else:
            rep = group[0]
            duration = _pick(durations, strategy)

        compacted.append(
            CompactedResult(
                job_id=job_id,
                duration=duration,
                success=any_success,
                source_count=len(group),
                strategy=strategy,
            )
        )

    return CompactReport(results=compacted, strategy=strategy)
