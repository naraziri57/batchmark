"""cruncher.py — reduce a list of TimingResults into aggregate statistics per job."""
from __future__ import annotations

import math
import statistics
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from batchmark.timer import TimingResult


@dataclass
class CrunchedJob:
    job_id: str
    count: int
    success_count: int
    failure_count: int
    min_duration: Optional[float]
    max_duration: Optional[float]
    mean_duration: Optional[float]
    stdev_duration: Optional[float]
    p50: Optional[float]
    p95: Optional[float]

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "count": self.count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "min_duration": self.min_duration,
            "max_duration": self.max_duration,
            "mean_duration": round(self.mean_duration, 4) if self.mean_duration is not None else None,
            "stdev_duration": round(self.stdev_duration, 4) if self.stdev_duration is not None else None,
            "p50": self.p50,
            "p95": self.p95,
        }


@dataclass
class CrunchReport:
    jobs: List[CrunchedJob] = field(default_factory=list)

    def get(self, job_id: str) -> Optional[CrunchedJob]:
        for j in self.jobs:
            if j.job_id == job_id:
                return j
        return None

    def to_dict(self) -> dict:
        return {"jobs": [j.to_dict() for j in self.jobs]}


def _percentile(sorted_vals: List[float], pct: float) -> Optional[float]:
    if not sorted_vals:
        return None
    k = (len(sorted_vals) - 1) * pct / 100
    lo, hi = int(math.floor(k)), int(math.ceil(k))
    if lo == hi:
        return sorted_vals[lo]
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (k - lo)


def crunch(results: List[TimingResult]) -> CrunchReport:
    groups: Dict[str, List[TimingResult]] = {}
    for r in results:
        groups.setdefault(r.job_id, []).append(r)

    jobs: List[CrunchedJob] = []
    for job_id, items in groups.items():
        durations = [r.duration for r in items if r.duration is not None]
        durations_sorted = sorted(durations)
        success_count = sum(1 for r in items if r.success)
        jobs.append(CrunchedJob(
            job_id=job_id,
            count=len(items),
            success_count=success_count,
            failure_count=len(items) - success_count,
            min_duration=min(durations_sorted) if durations_sorted else None,
            max_duration=max(durations_sorted) if durations_sorted else None,
            mean_duration=statistics.mean(durations_sorted) if durations_sorted else None,
            stdev_duration=statistics.stdev(durations_sorted) if len(durations_sorted) >= 2 else None,
            p50=_percentile(durations_sorted, 50),
            p95=_percentile(durations_sorted, 95),
        ))
    return CrunchReport(jobs=jobs)
