"""Detect outlier results based on duration statistics."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from batchmark.timer import TimingResult
import statistics


@dataclass
class OutlierResult:
    result: TimingResult
    z_score: float
    is_outlier: bool

    def to_dict(self) -> dict:
        return {
            "job_id": self.result.job_id,
            "duration": self.result.duration,
            "z_score": round(self.z_score, 4),
            "is_outlier": self.is_outlier,
        }


@dataclass
class OutlierReport:
    results: List[OutlierResult] = field(default_factory=list)
    mean: Optional[float] = None
    stdev: Optional[float] = None

    @property
    def outliers(self) -> List[OutlierResult]:
        return [r for r in self.results if r.is_outlier]

    def to_dict(self) -> dict:
        return {
            "mean": round(self.mean, 4) if self.mean is not None else None,
            "stdev": round(self.stdev, 4) if self.stdev is not None else None,
            "results": [r.to_dict() for r in self.results],
            "outlier_count": len(self.outliers),
        }


def detect_outliers(
    results: List[TimingResult],
    threshold: float = 2.0,
) -> OutlierReport:
    """Flag results whose duration z-score exceeds threshold."""
    durations = [r.duration for r in results if r.duration is not None]
    if len(durations) < 2:
        scored = [
            OutlierResult(result=r, z_score=0.0, is_outlier=False)
            for r in results
        ]
        mean = durations[0] if durations else None
        return OutlierReport(results=scored, mean=mean, stdev=None)

    mean = statistics.mean(durations)
    stdev = statistics.stdev(durations)

    scored = []
    for r in results:
        if r.duration is None or stdev == 0.0:
            z = 0.0
        else:
            z = abs(r.duration - mean) / stdev
        scored.append(OutlierResult(result=r, z_score=z, is_outlier=z > threshold))

    return OutlierReport(results=scored, mean=mean, stdev=stdev)
