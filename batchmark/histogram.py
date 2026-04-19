"""Duration histogram bucketing for batch job results."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict
import json

from batchmark.timer import TimingResult


@dataclass
class HistogramBucket:
    label: str
    low: float
    high: float
    count: int = 0
    job_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "range": [self.low, self.high],
            "count": self.count,
            "job_ids": self.job_ids,
        }


def build_histogram(
    results: List[TimingResult],
    num_buckets: int = 5,
) -> List[HistogramBucket]:
    durations = [(r.job_id, r.duration) for r in results if r.duration is not None]
    if not durations:
        return []

    values = [d for _, d in durations]
    lo, hi = min(values), max(values)
    if lo == hi:
        hi = lo + 1.0

    step = (hi - lo) / num_buckets
    buckets: List[HistogramBucket] = []
    for i in range(num_buckets):
        b_lo = lo + i * step
        b_hi = lo + (i + 1) * step
        buckets.append(HistogramBucket(label=f"{b_lo:.2f}-{b_hi:.2f}", low=b_lo, high=b_hi))

    for job_id, dur in durations:
        idx = min(int((dur - lo) / step), num_buckets - 1)
        buckets[idx].count += 1
        buckets[idx].job_ids.append(job_id)

    return buckets


def format_histogram_text(buckets: List[HistogramBucket]) -> str:
    if not buckets:
        return "No data for histogram."
    lines = ["Duration Histogram:", "-" * 40]
    max_count = max(b.count for b in buckets) or 1
    for b in buckets:
        bar = "#" * int(b.count / max_count * 20)
        lines.append(f"  {b.label:>20s} | {bar:<20s} {b.count}")
    return "\n".join(lines)


def format_histogram_json(buckets: List[HistogramBucket]) -> str:
    return json.dumps([b.to_dict() for b in buckets], indent=2)


def format_histogram(buckets: List[HistogramBucket], fmt: str = "text") -> str:
    if fmt == "json":
        return format_histogram_json(buckets)
    return format_histogram_text(buckets)
