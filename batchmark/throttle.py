"""Rate-limiting / concurrency throttle for batch job runs."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import List, Optional

from batchmark.timer import TimingResult


@dataclass
class ThrottleConfig:
    max_per_second: Optional[float] = None  # max jobs started per second
    max_concurrent: Optional[int] = None    # unused here, reserved
    min_gap_seconds: float = 0.0            # minimum gap between job starts

    def __post_init__(self) -> None:
        if self.max_per_second is not None and self.max_per_second <= 0:
            raise ValueError("max_per_second must be a positive number")
        if self.min_gap_seconds < 0:
            raise ValueError("min_gap_seconds must be non-negative")


@dataclass
class ThrottleReport:
    config: ThrottleConfig
    total_jobs: int
    total_wait_seconds: float
    waits: List[float] = field(default_factory=list)

    def avg_wait(self) -> float:
        if not self.waits:
            return 0.0
        return sum(self.waits) / len(self.waits)

    def to_dict(self) -> dict:
        return {
            "total_jobs": self.total_jobs,
            "total_wait_seconds": round(self.total_wait_seconds, 4),
            "avg_wait_seconds": round(self.avg_wait(), 4),
            "waits": [round(w, 4) for w in self.waits],
        }


def _required_gap(config: ThrottleConfig) -> float:
    gap = config.min_gap_seconds
    if config.max_per_second and config.max_per_second > 0:
        gap = max(gap, 1.0 / config.max_per_second)
    return gap


def apply_throttle(
    results: List[TimingResult],
    config: ThrottleConfig,
    *,
    _sleep=time.sleep,
) -> ThrottleReport:
    """Simulate throttle delays between job starts and return a report."""
    gap = _required_gap(config)
    waits: List[float] = []
    total_wait = 0.0
    last_start: Optional[float] = None

    for result in results:
        if last_start is not None and gap > 0:
            elapsed = time.monotonic() - last_start
            wait = max(0.0, gap - elapsed)
            if wait > 0:
                _sleep(wait)
                waits.append(wait)
                total_wait += wait
            else:
                waits.append(0.0)
        else:
            if last_start is not None:
                waits.append(0.0)
        last_start = time.monotonic()

    return ThrottleReport(
        config=config,
        total_jobs=len(results),
        total_wait_seconds=total_wait,
        waits=waits,
    )
