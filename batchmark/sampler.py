"""Random sampling of TimingResult lists."""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Optional

from batchmark.timer import TimingResult


@dataclass
class SampleReport:
    total: int
    sampled: int
    results: List[TimingResult]

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "sampled": self.sampled,
            "results": [r.to_dict() for r in self.results],
        }


def sample_results(
    results: List[TimingResult],
    n: Optional[int] = None,
    fraction: Optional[float] = None,
    seed: Optional[int] = None,
) -> SampleReport:
    """Return a random sample of results.

    Provide either *n* (absolute count) or *fraction* (0 < f <= 1).
    If both are given, *n* takes precedence.
    """
    if n is None and fraction is None:
        raise ValueError("Provide either n or fraction")
    if fraction is not None and not (0 < fraction <= 1.0):
        raise ValueError("fraction must be between 0 (exclusive) and 1 (inclusive)")

    total = len(results)
    if n is None:
        n = max(1, round(total * fraction))  # type: ignore[arg-type]
    n = min(n, total)

    rng = random.Random(seed)
    sampled = rng.sample(results, n) if n > 0 else []
    return SampleReport(total=total, sampled=len(sampled), results=sampled)


def stratified_sample(
    results: List[TimingResult],
    fraction: float,
    seed: Optional[int] = None,
) -> SampleReport:
    """Sample proportionally from success and failed groups."""
    if not (0 < fraction <= 1.0):
        raise ValueError("fraction must be between 0 (exclusive) and 1 (inclusive)")

    successes = [r for r in results if r.success]
    failures = [r for r in results if not r.success]

    rng = random.Random(seed)

    def _take(lst: List[TimingResult]) -> List[TimingResult]:
        k = max(1, round(len(lst) * fraction)) if lst else 0
        return rng.sample(lst, min(k, len(lst)))

    sampled = _take(successes) + _take(failures)
    return SampleReport(total=len(results), sampled=len(sampled), results=sampled)
