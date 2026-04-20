"""splitter.py — split a list of TimingResults into named subsets by a key function."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from batchmark.timer import TimingResult
from batchmark.summary import Summary, summarize


@dataclass
class Split:
    label: str
    results: List[TimingResult]
    summary: Summary

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "count": len(self.results),
            "summary": self.summary.to_dict(),
        }


@dataclass
class SplitReport:
    splits: List[Split] = field(default_factory=list)

    def get(self, label: str) -> Optional[Split]:
        for s in self.splits:
            if s.label == label:
                return s
        return None

    def labels(self) -> List[str]:
        return [s.label for s in self.splits]

    def to_dict(self) -> dict:
        return {"splits": [s.to_dict() for s in self.splits]}


def split_results(
    results: List[TimingResult],
    key_fn: Callable[[TimingResult], str],
    *,
    sort_labels: bool = True,
) -> SplitReport:
    """Partition *results* into named groups determined by *key_fn*.

    Args:
        results:      flat list of TimingResult objects.
        key_fn:       function that returns a string label for each result.
        sort_labels:  if True (default) the splits are returned in
                      alphabetical label order.

    Returns:
        SplitReport containing one Split per distinct label.
    """
    buckets: Dict[str, List[TimingResult]] = {}
    for r in results:
        label = key_fn(r)
        buckets.setdefault(label, []).append(r)

    labels = sorted(buckets) if sort_labels else list(buckets)
    splits = [
        Split(label=lbl, results=buckets[lbl], summary=summarize(buckets[lbl]))
        for lbl in labels
    ]
    return SplitReport(splits=splits)


def split_by_status(results: List[TimingResult]) -> SplitReport:
    """Convenience wrapper: split into 'success' and 'failed' groups."""
    return split_results(results, key_fn=lambda r: "success" if r.success else "failed")


def split_by_job_id(results: List[TimingResult]) -> SplitReport:
    """Convenience wrapper: one split per distinct job_id."""
    return split_results(results, key_fn=lambda r: r.job_id)
