"""trimmer.py — trim results by removing the top/bottom N% of durations."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from batchmark.timer import TimingResult


@dataclass
class TrimReport:
    kept: List[TimingResult]
    dropped_low: List[TimingResult]
    dropped_high: List[TimingResult]

    @property
    def dropped_count(self) -> int:
        return len(self.dropped_low) + len(self.dropped_high)

    @property
    def kept_count(self) -> int:
        return len(self.kept)

    def to_dict(self) -> dict:
        return {
            "kept_count": self.kept_count,
            "dropped_count": self.dropped_count,
            "dropped_low": self.dropped_low_count,
            "dropped_high": self.dropped_high_count,
        }

    @property
    def dropped_low_count(self) -> int:
        return len(self.dropped_low)

    @property
    def dropped_high_count(self) -> int:
        return len(self.dropped_high)


def trim_results(
    results: List[TimingResult],
    lower_pct: float = 0.0,
    upper_pct: float = 0.0,
) -> TrimReport:
    """Remove the bottom *lower_pct*% and top *upper_pct*% by duration.

    Results with no duration are always kept (they cannot be ranked).
    Percentages are expressed as values in [0, 100).
    """
    if lower_pct < 0 or upper_pct < 0:
        raise ValueError("Percentages must be non-negative")
    if lower_pct + upper_pct >= 100:
        raise ValueError("Combined trim percentage must be less than 100")

    with_duration = [r for r in results if r.duration_seconds is not None]
    without_duration = [r for r in results if r.duration_seconds is None]

    if not with_duration:
        return TrimReport(kept=list(results), dropped_low=[], dropped_high=[])

    sorted_results = sorted(with_duration, key=lambda r: r.duration_seconds)  # type: ignore[arg-type]
    n = len(sorted_results)

    low_cut = int(n * lower_pct / 100.0)
    high_cut = int(n * upper_pct / 100.0)
    high_start = n - high_cut if high_cut > 0 else n

    dropped_low = sorted_results[:low_cut]
    dropped_high = sorted_results[high_start:]
    kept = sorted_results[low_cut:high_start] + without_duration

    return TrimReport(kept=kept, dropped_low=dropped_low, dropped_high=dropped_high)
