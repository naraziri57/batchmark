"""Trend analysis across multiple benchmark runs."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from batchmark.timer import TimingResult


@dataclass
class TrendPoint:
    run_index: int
    avg_duration: float
    success_rate: float
    total_jobs: int

    def to_dict(self) -> dict:
        return {
            "run_index": self.run_index,
            "avg_duration": round(self.avg_duration, 4),
            "success_rate": round(self.success_rate, 4),
            "total_jobs": self.total_jobs,
        }


@dataclass
class TrendReport:
    points: List[TrendPoint] = field(default_factory=list)

    def is_improving(self) -> bool:
        """Return True if avg_duration is decreasing over runs."""
        durations = [p.avg_duration for p in self.points]
        if len(durations) < 2:
            return False
        return durations[-1] < durations[0]

    def slope(self) -> Optional[float]:
        """Simple linear slope of avg_duration across run indices."""
        if len(self.points) < 2:
            return None
        n = len(self.points)
        xs = [p.run_index for p in self.points]
        ys = [p.avg_duration for p in self.points]
        x_mean = sum(xs) / n
        y_mean = sum(ys) / n
        num = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
        den = sum((x - x_mean) ** 2 for x in xs)
        return num / den if den != 0 else 0.0

    def to_dict(self) -> dict:
        return {
            "points": [p.to_dict() for p in self.points],
            "is_improving": self.is_improving(),
            "slope": round(self.slope(), 6) if self.slope() is not None else None,
        }


def analyze_trend(runs: List[List[TimingResult]]) -> TrendReport:
    """Build a TrendReport from a list of runs (each run is a list of TimingResults)."""
    points = []
    for idx, results in enumerate(runs):
        if not results:
            continue
        durations = [r.duration for r in results if r.duration is not None]
        avg = sum(durations) / len(durations) if durations else 0.0
        successes = sum(1 for r in results if r.success)
        rate = successes / len(results) if results else 0.0
        points.append(TrendPoint(
            run_index=idx,
            avg_duration=avg,
            success_rate=rate,
            total_jobs=len(results),
        ))
    return TrendReport(points=points)
