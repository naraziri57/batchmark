"""Sliding window aggregation over TimingResult sequences."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from batchmark.timer import TimingResult


@dataclass
class WindowStat:
    window_index: int
    start_index: int
    end_index: int  # exclusive
    count: int
    success_count: int
    failed_count: int
    avg_duration: Optional[float]

    def to_dict(self) -> dict:
        return {
            "window_index": self.window_index,
            "start_index": self.start_index,
            "end_index": self.end_index,
            "count": self.count,
            "success_count": self.success_count,
            "failed_count": self.failed_count,
            "avg_duration": self.avg_duration,
        }


@dataclass
class WindowReport:
    window_size: int
    step: int
    windows: List[WindowStat] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "window_size": self.window_size,
            "step": self.step,
            "windows": [w.to_dict() for w in self.windows],
        }


def _stat_for_window(
    results: List[TimingResult], start: int, end: int, index: int
) -> WindowStat:
    chunk = results[start:end]
    success = [r for r in chunk if r.success]
    failed = [r for r in chunk if not r.success]
    durations = [r.duration for r in chunk if r.duration is not None]
    avg = sum(durations) / len(durations) if durations else None
    return WindowStat(
        window_index=index,
        start_index=start,
        end_index=end,
        count=len(chunk),
        success_count=len(success),
        failed_count=len(failed),
        avg_duration=round(avg, 6) if avg is not None else None,
    )


def build_window_report(
    results: List[TimingResult],
    window_size: int = 5,
    step: int = 1,
) -> WindowReport:
    """Slide a window of *window_size* over *results* with stride *step*."""
    if window_size < 1:
        raise ValueError("window_size must be >= 1")
    if step < 1:
        raise ValueError("step must be >= 1")

    windows: List[WindowStat] = []
    n = len(results)
    idx = 0
    pos = 0
    while pos < n:
        end = min(pos + window_size, n)
        windows.append(_stat_for_window(results, pos, end, idx))
        idx += 1
        pos += step

    return WindowReport(window_size=window_size, step=step, windows=windows)
