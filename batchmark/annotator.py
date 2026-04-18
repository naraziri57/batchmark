"""Annotate TimingResults with custom tags or labels."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional
from batchmark.timer import TimingResult


@dataclass
class AnnotatedResult:
    result: TimingResult
    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = self.result.to_dict()
        d["tags"] = self.tags
        return d


AnnotatorFn = Callable[[TimingResult], Dict[str, str]]


def annotate(
    results: List[TimingResult],
    annotators: List[AnnotatorFn],
) -> List[AnnotatedResult]:
    """Apply one or more annotator functions to each result.

    Each annotator receives a TimingResult and returns a dict of tag key/value
    pairs. Tags from multiple annotators are merged; later annotators win on
    key conflicts.
    """
    annotated: List[AnnotatedResult] = []
    for r in results:
        merged: Dict[str, str] = {}
        for fn in annotators:
            merged.update(fn(r))
        annotated.append(AnnotatedResult(result=r, tags=merged))
    return annotated


def tag_by_status(result: TimingResult) -> Dict[str, str]:
    """Built-in annotator: adds a 'status' tag."""
    return {"status": "success" if result.success else "failed"}


def tag_by_duration_bucket(
    thresholds: Optional[Dict[str, float]] = None,
) -> AnnotatorFn:
    """Factory: returns an annotator that buckets duration into slow/medium/fast.

    thresholds keys: 'fast' and 'medium' (upper bounds in seconds).
    Anything above 'medium' is 'slow'.
    """
    if thresholds is None:
        thresholds = {"fast": 1.0, "medium": 5.0}

    def _annotate(result: TimingResult) -> Dict[str, str]:
        if result.duration is None:
            return {"bucket": "unknown"}
        if result.duration <= thresholds["fast"]:
            return {"bucket": "fast"}
        if result.duration <= thresholds["medium"]:
            return {"bucket": "medium"}
        return {"bucket": "slow"}

    return _annotate
