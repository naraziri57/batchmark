"""Smooth a sequence of TimingResults using a rolling average window."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from batchmark.timer import TimingResult


@dataclass
class SmoothedPoint:
    job_id: str
    index: int
    raw_duration: Optional[float]
    smoothed_duration: Optional[float]

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "index": self.index,
            "raw_duration": self.raw_duration,
            "smoothed_duration": (
                round(self.smoothed_duration, 4)
                if self.smoothed_duration is not None
                else None
            ),
        }


@dataclass
class SmoothedReport:
    job_id: str
    points: List[SmoothedPoint] = field(default_factory=list)
    window: int = 3

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "window": self.window,
            "points": [p.to_dict() for p in self.points],
        }


def smooth_results(
    results: List[TimingResult],
    window: int = 3,
) -> List[SmoothedReport]:
    """Group results by job_id and produce a rolling-average smoothed report."""
    if window < 1:
        raise ValueError("window must be >= 1")

    from collections import defaultdict

    grouped: dict[str, List[TimingResult]] = defaultdict(list)
    for r in results:
        grouped[r.job_id].append(r)

    reports: List[SmoothedReport] = []
    for job_id, job_results in sorted(grouped.items()):
        points: List[SmoothedPoint] = []
        for i, r in enumerate(job_results):
            raw = r.duration
            # Collect up to `window` durations ending at index i
            start = max(0, i - window + 1)
            window_vals = [
                job_results[j].duration
                for j in range(start, i + 1)
                if job_results[j].duration is not None
            ]
            smoothed = (
                sum(window_vals) / len(window_vals) if window_vals else None
            )
            points.append(SmoothedPoint(job_id=job_id, index=i, raw_duration=raw, smoothed_duration=smoothed))
        reports.append(SmoothedReport(job_id=job_id, points=points, window=window))
    return reports
