"""stamper.py — attach epoch-based time stamps to timing results."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Callable
import time

from batchmark.timer import TimingResult


@dataclass
class StampedResult:
    result: TimingResult
    epoch: float  # unix timestamp in seconds
    label: str = ""

    def to_dict(self) -> dict:
        d = {
            "job_id": self.result.job_id,
            "success": self.result.success,
            "duration": self.result.duration,
            "epoch": round(self.epoch, 6),
            "label": self.label,
        }
        return d


@dataclass
class StampReport:
    entries: List[StampedResult] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"entries": [e.to_dict() for e in self.entries]}

    def earliest(self) -> Optional[StampedResult]:
        if not self.entries:
            return None
        return min(self.entries, key=lambda e: e.epoch)

    def latest(self) -> Optional[StampedResult]:
        if not self.entries:
            return None
        return max(self.entries, key=lambda e: e.epoch)

    def span(self) -> Optional[float]:
        """Total time span from earliest to latest stamp in seconds."""
        if len(self.entries) < 2:
            return None
        return self.latest().epoch - self.earliest().epoch


def stamp_results(
    results: List[TimingResult],
    clock: Callable[[], float] = time.time,
    label: str = "",
    offsets: Optional[List[float]] = None,
) -> StampReport:
    """Attach timestamps to a list of results.

    If *offsets* is provided it must have the same length as *results*;
    each value is added to the current clock reading to produce the epoch.
    Otherwise the clock is called once per result in order.
    """
    if offsets is not None and len(offsets) != len(results):
        raise ValueError(
            f"offsets length ({len(offsets)}) must match results length ({len(results)})"
        )

    entries: List[StampedResult] = []
    for i, result in enumerate(results):
        if offsets is not None:
            epoch = clock() + offsets[i]
        else:
            epoch = clock()
        entries.append(StampedResult(result=result, epoch=epoch, label=label))

    return StampReport(entries=entries)
