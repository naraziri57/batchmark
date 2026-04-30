"""Rate capper: limits results to a maximum count per job_id within a time window."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from batchmark.timer import TimingResult


@dataclass
class RateCappedResult:
    result: TimingResult
    accepted: bool
    reason: Optional[str] = None

    def to_dict(self) -> dict:
        d = self.result.to_dict()
        d["accepted"] = self.accepted
        d["reason"] = self.reason
        return d


@dataclass
class RateCapReport:
    items: List[RateCappedResult] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.items)

    @property
    def accepted_count(self) -> int:
        return sum(1 for r in self.items if r.accepted)

    @property
    def rejected_count(self) -> int:
        return self.total - self.accepted_count

    def accepted(self) -> List[TimingResult]:
        return [r.result for r in self.items if r.accepted]

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "accepted": self.accepted_count,
            "rejected": self.rejected_count,
            "items": [r.to_dict() for r in self.items],
        }


def rate_cap(
    results: List[TimingResult],
    max_per_job: int,
    window_seconds: Optional[float] = None,
) -> RateCapReport:
    """Cap results to at most max_per_job per job_id.

    If window_seconds is given, the cap applies within each window independently.
    Otherwise the cap applies globally across all results for that job_id.
    """
    if max_per_job < 0:
        raise ValueError("max_per_job must be >= 0")

    counts: Dict[str, int] = {}
    items: List[RateCappedResult] = []

    for r in results:
        if window_seconds is not None and r.start_time is not None:
            bucket = int(r.start_time // window_seconds)
            key = f"{r.job_id}::{bucket}"
        else:
            key = r.job_id

        counts[key] = counts.get(key, 0) + 1
        if counts[key] <= max_per_job:
            items.append(RateCappedResult(result=r, accepted=True))
        else:
            items.append(
                RateCappedResult(
                    result=r,
                    accepted=False,
                    reason=f"exceeded max_per_job={max_per_job} for key '{key}'",
                )
            )

    return RateCapReport(items=items)
