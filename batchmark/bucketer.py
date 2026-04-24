"""Groups TimingResults into named duration buckets."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from batchmark.timer import TimingResult
from batchmark.summary import summarize, Summary


@dataclass
class Bucket:
    label: str
    low: Optional[float]   # inclusive, None = no lower bound
    high: Optional[float]  # exclusive, None = no upper bound
    results: List[TimingResult] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.results)

    @property
    def summary(self) -> Optional[Summary]:
        if not self.results:
            return None
        return summarize(self.results)

    def to_dict(self) -> dict:
        s = self.summary
        return {
            "label": self.label,
            "low": self.low,
            "high": self.high,
            "count": self.count,
            "summary": s.to_dict() if s else None,
        }


@dataclass
class BucketReport:
    buckets: List[Bucket]

    def get(self, label: str) -> Optional[Bucket]:
        for b in self.buckets:
            if b.label == label:
                return b
        return None

    def to_dict(self) -> dict:
        return {"buckets": [b.to_dict() for b in self.buckets]}


def _make_buckets(boundaries: List[float]) -> List[Bucket]:
    """Build bucket definitions from a sorted list of boundary values."""
    edges: List[tuple] = []
    sorted_b = sorted(set(boundaries))
    edges.append((None, sorted_b[0], f"<{sorted_b[0]}"))
    for i in range(len(sorted_b) - 1):
        lo, hi = sorted_b[i], sorted_b[i + 1]
        edges.append((lo, hi, f"{lo}-{hi}"))
    edges.append((sorted_b[-1], None, f">={sorted_b[-1]}"))
    return [Bucket(label=lbl, low=lo, high=hi) for lo, hi, lbl in edges]


def bucket_results(
    results: List[TimingResult],
    boundaries: List[float],
) -> BucketReport:
    """Assign each result to a duration bucket based on boundaries."""
    if not boundaries:
        b = Bucket(label="all", low=None, high=None, results=list(results))
        return BucketReport(buckets=[b])

    buckets = _make_buckets(boundaries)
    for r in results:
        dur = r.duration
        placed = False
        for b in buckets:
            lo_ok = b.low is None or (dur is not None and dur >= b.low)
            hi_ok = b.high is None or (dur is not None and dur < b.high)
            if dur is None:
                # put None-duration results in the first bucket
                if b.low is None:
                    b.results.append(r)
                    placed = True
                    break
            elif lo_ok and hi_ok:
                b.results.append(r)
                placed = True
                break
        if not placed:
            buckets[-1].results.append(r)
    return BucketReport(buckets=buckets)
