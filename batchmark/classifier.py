"""Classify TimingResults into named categories using predicate functions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from batchmark.timer import TimingResult


@dataclass
class ClassifiedResult:
    result: TimingResult
    category: str

    def to_dict(self) -> dict:
        d = self.result.to_dict()
        d["category"] = self.category
        return d


@dataclass
class ClassificationReport:
    classified: List[ClassifiedResult] = field(default_factory=list)
    default_category: str = "uncategorized"

    def by_category(self) -> Dict[str, List[ClassifiedResult]]:
        groups: Dict[str, List[ClassifiedResult]] = {}
        for cr in self.classified:
            groups.setdefault(cr.category, []).append(cr)
        return groups

    def category_counts(self) -> Dict[str, int]:
        return {cat: len(items) for cat, items in self.by_category().items()}

    def to_dict(self) -> dict:
        return {
            "classified": [cr.to_dict() for cr in self.classified],
            "category_counts": self.category_counts(),
        }


Classifier = Callable[[TimingResult], Optional[str]]


def classify_results(
    results: List[TimingResult],
    classifiers: List[tuple[str, Classifier]],
    default_category: str = "uncategorized",
) -> ClassificationReport:
    """Apply classifiers in order; first match wins. Falls back to default_category."""
    classified: List[ClassifiedResult] = []
    for result in results:
        category = default_category
        for name, fn in classifiers:
            if fn(result):
                category = name
                break
        classified.append(ClassifiedResult(result=result, category=category))
    return ClassificationReport(classified=classified, default_category=default_category)


def classifier_from_map(category_map: Dict[str, List[str]]) -> List[tuple[str, Classifier]]:
    """Build classifiers from a mapping of category -> list of job_id prefixes."""
    classifiers: List[tuple[str, Classifier]] = []
    for category, prefixes in category_map.items():
        def _make(cat_prefixes: List[str]) -> Classifier:
            def _fn(r: TimingResult) -> Optional[str]:
                return any(r.job_id.startswith(p) for p in cat_prefixes) or None
            return _fn
        classifiers.append((category, _make(prefixes)))
    return classifiers
