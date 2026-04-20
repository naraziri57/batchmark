"""Assign human-readable labels to results based on configurable rules."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from batchmark.timer import TimingResult


@dataclass
class LabeledResult:
    result: TimingResult
    labels: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = self.result.to_dict()
        d["labels"] = dict(self.labels)
        return d


LabelerFn = Callable[[TimingResult], Optional[str]]


def label_results(
    results: List[TimingResult],
    labelers: Dict[str, LabelerFn],
) -> List[LabeledResult]:
    """Apply each labeler function to every result, collecting non-None values."""
    labeled: List[LabeledResult] = []
    for r in results:
        labels: Dict[str, str] = {}
        for key, fn in labelers.items():
            value = fn(r)
            if value is not None:
                labels[key] = value
        labeled.append(LabeledResult(result=r, labels=labels))
    return labeled


def labeler_from_map(key: str, mapping: Dict[str, str]) -> LabelerFn:
    """Return a labeler that maps job_id to a fixed label string."""
    def _fn(r: TimingResult) -> Optional[str]:
        return mapping.get(r.job_id)
    return _fn


def status_labeler(r: TimingResult) -> Optional[str]:
    """Label results by their success/failure status."""
    return "ok" if r.success else "fail"


def duration_tier_labeler(
    fast_threshold: float = 0.5,
    slow_threshold: float = 2.0,
) -> LabelerFn:
    """Return a labeler that assigns 'fast', 'medium', or 'slow' based on duration."""
    def _fn(r: TimingResult) -> Optional[str]:
        if r.duration is None:
            return None
        if r.duration < fast_threshold:
            return "fast"
        if r.duration <= slow_threshold:
            return "medium"
        return "slow"
    return _fn
