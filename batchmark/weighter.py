"""weighter.py — assign numeric weights to results based on configurable rules.

Weights can be used downstream by scorers, rankers, or aggregators to
prioritise certain jobs over others.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from batchmark.timer import TimingResult


@dataclass
class WeightedResult:
    """A TimingResult paired with a computed weight."""

    result: TimingResult
    weight: float
    reason: str  # human-readable explanation of why this weight was assigned

    def to_dict(self) -> dict:
        return {
            "job_id": self.result.job_id,
            "success": self.result.success,
            "duration": self.result.duration,
            "weight": round(self.weight, 6),
            "reason": self.reason,
        }


@dataclass
class WeightReport:
    """Collection of weighted results with convenience helpers."""

    items: List[WeightedResult] = field(default_factory=list)

    def total_weight(self) -> float:
        """Sum of all weights."""
        return sum(w.weight for w in self.items)

    def by_job_id(self, job_id: str) -> Optional[WeightedResult]:
        """Return the WeightedResult for a specific job, or None."""
        for item in self.items:
            if item.result.job_id == job_id:
                return item
        return None

    def to_dict(self) -> dict:
        return {
            "total_weight": round(self.total_weight(), 6),
            "items": [i.to_dict() for i in self.items],
        }


# A weighter is a callable that returns (weight, reason) for a result.
WeighterFn = Callable[[TimingResult], tuple[float, str]]


def weighter_from_map(weight_map: Dict[str, float], default: float = 1.0) -> WeighterFn:
    """Return a weighter that looks up job_id in *weight_map*.

    Jobs not present in the map receive *default*.
    """

    def _fn(result: TimingResult) -> tuple[float, str]:
        if result.job_id in weight_map:
            return weight_map[result.job_id], f"explicit weight for '{result.job_id}'"
        return default, "default weight"

    return _fn


def status_weighter(success_weight: float = 1.0, failure_weight: float = 0.5) -> WeighterFn:
    """Return a weighter that assigns different weights based on success/failure."""

    def _fn(result: TimingResult) -> tuple[float, str]:
        if result.success:
            return success_weight, "success weight"
        return failure_weight, "failure weight"

    return _fn


def duration_weighter(reference: float, scale: float = 1.0) -> WeighterFn:
    """Return a weighter that scores inversely proportional to duration.

    Jobs faster than *reference* get weight > *scale*; slower jobs get weight
    between 0 and *scale*.  Jobs with no duration receive weight 0.
    """

    def _fn(result: TimingResult) -> tuple[float, str]:
        if result.duration is None:
            return 0.0, "no duration — zero weight"
        ratio = reference / result.duration if result.duration > 0 else 0.0
        w = round(ratio * scale, 6)
        return w, f"duration-based weight (ref={reference}s)"

    return _fn


def weight_results(
    results: List[TimingResult],
    weighters: List[WeighterFn],
    combine: str = "product",
) -> WeightReport:
    """Apply one or more weighters to *results* and return a WeightReport.

    Parameters
    ----------
    results:
        Raw timing results to weight.
    weighters:
        List of weighter callables.  Each returns (weight, reason).
    combine:
        How to merge weights when multiple weighters are supplied.
        ``'product'`` multiplies all weights together (default).
        ``'sum'`` adds them.
        ``'min'`` takes the smallest.
        ``'max'`` takes the largest.
    """
    if combine not in {"product", "sum", "min", "max"}:
        raise ValueError(f"Unknown combine strategy: {combine!r}")

    items: List[WeightedResult] = []

    for result in results:
        if not weighters:
            items.append(WeightedResult(result=result, weight=1.0, reason="no weighters — default 1.0"))
            continue

        weights: List[float] = []
        reasons: List[str] = []
        for wfn in weighters:
            w, r = wfn(result)
            weights.append(w)
            reasons.append(r)

        if combine == "product":
            final = 1.0
            for w in weights:
                final *= w
        elif combine == "sum":
            final = sum(weights)
        elif combine == "min":
            final = min(weights)
        else:  # max
            final = max(weights)

        reason_str = f"{combine}({', '.join(reasons)})"
        items.append(WeightedResult(result=result, weight=round(final, 6), reason=reason_str))

    return WeightReport(items=items)
