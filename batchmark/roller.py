"""Rolling window statistics over ordered TimingResults."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from batchmark.timer import TimingResult


@dataclass
class RollingPoint:
    index: int
    job_id: str
    raw_duration: Optional[float]
    rolling_avg: Optional[float]
    rolling_min: Optional[float]
    rolling_max: Optional[float]
    window_size: int

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "job_id": self.job_id,
            "raw_duration": self.raw_duration,
            "rolling_avg": round(self.rolling_avg, 4) if self.rolling_avg is not None else None,
            "rolling_min": round(self.rolling_min, 4) if self.rolling_min is not None else None,
            "rolling_max": round(self.rolling_max, 4) if self.rolling_max is not None else None,
            "window_size": self.window_size,
        }


@dataclass
class RollingReport:
    points: List[RollingPoint]
    window: int

    def to_dict(self) -> dict:
        return {
            "window": self.window,
            "points": [p.to_dict() for p in self.points],
        }


def rolling_stats(results: List[TimingResult], window: int = 5) -> RollingReport:
    """Compute rolling avg/min/max over a sliding window of results."""
    if window < 1:
        raise ValueError("window must be >= 1")

    points: List[RollingPoint] = []
    for i, result in enumerate(results):
        start = max(0, i - window + 1)
        slice_ = results[start : i + 1]
        durations = [r.duration for r in slice_ if r.duration is not None]

        if durations:
            avg = sum(durations) / len(durations)
            mn = min(durations)
            mx = max(durations)
        else:
            avg = mn = mx = None

        points.append(
            RollingPoint(
                index=i,
                job_id=result.job_id,
                raw_duration=result.duration,
                rolling_avg=avg,
                rolling_min=mn,
                rolling_max=mx,
                window_size=len(slice_),
            )
        )

    return RollingReport(points=points, window=window)
