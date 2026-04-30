"""binner.py — group results into fixed-width time bins and compute per-bin stats."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from batchmark.timer import TimingResult
from batchmark.summary import summarize


@dataclass
class Bin:
    label: str          # e.g. "0.0–0.5s"
    low: float
    high: float
    results: List[TimingResult] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.results)

    @property
    def success_count(self) -> int:
        return sum(1 for r in self.results if r.success)

    @property
    def avg_duration(self) -> Optional[float]:
        durations = [r.duration for r in self.results if r.duration is not None]
        return sum(durations) / len(durations) if durations else None

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "low": self.low,
            "high": self.high,
            "count": self.count,
            "success_count": self.success_count,
            "avg_duration": round(self.avg_duration, 4) if self.avg_duration is not None else None,
        }


@dataclass
class BinReport:
    bins: List[Bin]
    bin_width: float

    @property
    def total(self) -> int:
        return sum(b.count for b in self.bins)

    def to_dict(self) -> dict:
        return {
            "bin_width": self.bin_width,
            "total": self.total,
            "bins": [b.to_dict() for b in self.bins],
        }


def bin_results(
    results: List[TimingResult],
    bin_width: float = 0.5,
    max_duration: Optional[float] = None,
) -> BinReport:
    """Distribute results into fixed-width duration bins."""
    if not results or bin_width <= 0:
        return BinReport(bins=[], bin_width=bin_width)

    durations = [r.duration for r in results if r.duration is not None]
    if not durations:
        return BinReport(bins=[], bin_width=bin_width)

    upper = max_duration if max_duration is not None else max(durations)
    num_bins = max(1, int((upper / bin_width)) + 1)

    bins: List[Bin] = []
    for i in range(num_bins):
        low = i * bin_width
        high = low + bin_width
        label = f"{low:.2f}–{high:.2f}s"
        bins.append(Bin(label=label, low=low, high=high))

    for r in results:
        if r.duration is None:
            continue
        idx = min(int(r.duration / bin_width), num_bins - 1)
        bins[idx].results.append(r)

    return BinReport(bins=bins, bin_width=bin_width)
