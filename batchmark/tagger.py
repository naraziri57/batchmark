"""Tag results with arbitrary key-value labels for grouping and filtering."""
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from batchmark.timer import TimingResult


@dataclass
class TaggedResult:
    result: TimingResult
    tags: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        base = {
            "job_id": self.result.job_id,
            "duration": self.result.duration,
            "success": self.result.success,
            "tags": self.tags,
        }
        if self.result.error:
            base["error"] = self.result.error
        return base


Tagger = Callable[[TimingResult], Dict[str, Any]]


def tag_results(
    results: List[TimingResult],
    taggers: List[Tagger],
) -> List[TaggedResult]:
    """Apply each tagger to every result, merging all returned tags."""
    tagged = []
    for r in results:
        merged: Dict[str, Any] = {}
        for tagger in taggers:
            merged.update(tagger(r))
        tagged.append(TaggedResult(result=r, tags=merged))
    return tagged


def tagger_from_map(tag_key: str, mapping: Dict[str, Any]) -> Tagger:
    """Return a tagger that sets tag_key to mapping[job_id] or None."""
    def _tagger(r: TimingResult) -> Dict[str, Any]:
        return {tag_key: mapping.get(r.job_id)}
    return _tagger


def tagger_static(tags: Dict[str, Any]) -> Tagger:
    """Return a tagger that applies the same static tags to every result."""
    def _tagger(r: TimingResult) -> Dict[str, Any]:
        return dict(tags)
    return _tagger


def filter_by_tag(
    tagged: List[TaggedResult],
    tag_key: str,
    tag_value: Any,
) -> List[TaggedResult]:
    """Return only results whose tag matches the given value."""
    return [t for t in tagged if t.tags.get(tag_key) == tag_value]
