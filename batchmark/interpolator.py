"""Interpolator: fill in missing durations using neighbouring values.

When a batch run has None durations (e.g. the job was skipped or its
timing was lost), it can be useful to estimate the missing values so
downstream analysis still works.  This module supports three strategies:

  linear   – linearly interpolate between the nearest known neighbours
  forward  – carry the last known value forward
  backward – carry the next known value backward

Results whose duration is not None are left untouched.  A flag
``interpolated`` on the returned record lets callers distinguish
original from filled-in values.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Literal

from batchmark.timer import TimingResult

Strategy = Literal["linear", "forward", "backward"]


@dataclass
class InterpolatedResult:
    """A timing result, possibly with an estimated duration."""

    result: TimingResult
    interpolated: bool = False
    estimated_duration: Optional[float] = None

    @property
    def effective_duration(self) -> Optional[float]:
        """Return the estimated duration if interpolated, else the original."""
        if self.interpolated:
            return self.estimated_duration
        return self.result.duration

    def to_dict(self) -> dict:
        d = {
            "job_id": self.result.job_id,
            "duration": self.effective_duration,
            "success": self.result.success,
            "interpolated": self.interpolated,
        }
        if self.result.error:
            d["error"] = self.result.error
        return d


@dataclass
class InterpolateReport:
    """Container for all interpolated results and summary statistics."""

    results: List[InterpolatedResult] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def interpolated_count(self) -> int:
        return sum(1 for r in self.results if r.interpolated)

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "interpolated_count": self.interpolated_count,
            "results": [r.to_dict() for r in self.results],
        }


def interpolate(
    results: List[TimingResult],
    strategy: Strategy = "linear",
) -> InterpolateReport:
    """Interpolate missing durations in *results* using *strategy*.

    Parameters
    ----------
    results:
        Ordered list of timing results (ordering matters for linear /
        forward / backward strategies).
    strategy:
        One of ``"linear"``, ``"forward"``, or ``"backward"``.

    Returns
    -------
    InterpolateReport
        Report containing one :class:`InterpolatedResult` per input result.
    """
    if not results:
        return InterpolateReport()

    if strategy == "forward":
        filled = _forward_fill(results)
    elif strategy == "backward":
        filled = _backward_fill(results)
    else:
        filled = _linear_fill(results)

    items = []
    for original, estimated in zip(results, filled):
        if original.duration is None and estimated is not None:
            items.append(
                InterpolatedResult(
                    result=original,
                    interpolated=True,
                    estimated_duration=estimated,
                )
            )
        else:
            items.append(InterpolatedResult(result=original, interpolated=False))

    return InterpolateReport(results=items)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _forward_fill(results: List[TimingResult]) -> List[Optional[float]]:
    """Carry the last known duration forward."""
    out: List[Optional[float]] = []
    last: Optional[float] = None
    for r in results:
        if r.duration is not None:
            last = r.duration
        out.append(last)
    return out


def _backward_fill(results: List[TimingResult]) -> List[Optional[float]]:
    """Carry the next known duration backward."""
    out: List[Optional[float]] = [None] * len(results)
    nxt: Optional[float] = None
    for i in range(len(results) - 1, -1, -1):
        if results[i].duration is not None:
            nxt = results[i].duration
        out[i] = nxt
    return out


def _linear_fill(results: List[TimingResult]) -> List[Optional[float]]:
    """Linearly interpolate between neighbouring known durations."""
    n = len(results)
    out: List[Optional[float]] = [r.duration for r in results]

    # Find runs of None values and interpolate within each run.
    i = 0
    while i < n:
        if out[i] is None:
            # Find the start of this gap.
            start = i - 1  # index of last known value before the gap (-1 if none)
            while i < n and out[i] is None:
                i += 1
            end = i  # index of first known value after the gap (n if none)

            left = out[start] if start >= 0 else None
            right = out[end] if end < n else None

            for j in range(start + 1, end):
                if left is not None and right is not None:
                    # Interpolate proportionally.
                    span = end - start
                    t = (j - start) / span
                    out[j] = left + t * (right - left)
                elif left is not None:
                    out[j] = left
                elif right is not None:
                    out[j] = right
                # else: leave as None (no neighbours at all)
        else:
            i += 1

    return out
