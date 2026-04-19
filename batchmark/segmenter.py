"""Segment results into time-based windows."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from batchmark.timer import TimingResult


@dataclass
class Segment:
    label: str
    start: float
    end: float
    results: List[TimingResult] = field(default_factory=list)

    def count(self) -> int:
        return len(self.results)

    def success_count(self) -> int:
        return sum(1 for r in self.results if r.success)

    def avg_duration(self) -> Optional[float]:
        durations = [r.duration for r in self.results if r.duration is not None]
        if not durations:
            return None
        return sum(durations) / len(durations)

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "start": self.start,
            "end": self.end,
            "count": self.count(),
            "success_count": self.success_count(),
            "avg_duration": self.avg_duration(),
        }


def segment_by_window(
    results: List[TimingResult],
    window_size: float,
    origin: Optional[float] = None,
) -> List[Segment]:
    """Split results into fixed-width time windows based on start_time."""
    timed = [r for r in results if r.start_time is not None]
    if not timed:
        return []

    base = origin if origin is not None else min(r.start_time for r in timed)
    max_t = max(r.start_time for r in timed)

    segments: List[Segment] = []
    t = base
    idx = 0
    while t <= max_t:
        end = t + window_size
        label = f"{t:.2f}-{end:.2f}"
        seg = Segment(label=label, start=t, end=end)
        for r in timed:
            if t <= r.start_time < end:
                seg.results.append(r)
        segments.append(seg)
        t = end
        idx += 1
    return segments
