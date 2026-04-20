"""Partition results into named buckets based on a key function."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from batchmark.timer import TimingResult
from batchmark.summary import Summary, summarize


@dataclass
class Partition:
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
class PartitionReport:
    partitions: List[Partition] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"partitions": [p.to_dict() for p in self.partitions]}

    def get(self, label: str) -> Optional[Partition]:
        for p in self.partitions:
            if p.label == label:
                return p
        return None


def partition_results(
    results: List[TimingResult],
    key_fn: Callable[[TimingResult], str],
    labels: Optional[List[str]] = None,
) -> PartitionReport:
    """Group results into partitions using key_fn.

    If labels is provided, only those buckets are included (in order).
    Unknown keys are placed in an 'other' bucket unless labels is None.
    """
    buckets: Dict[str, List[TimingResult]] = {}
    for r in results:
        key = key_fn(r)
        buckets.setdefault(key, []).append(r)

    if labels is not None:
        ordered_keys = labels
        other = [r for r in results if key_fn(r) not in labels]
        if other:
            buckets.setdefault("other", []).extend(other)
            ordered_keys = labels + ["other"]
    else:
        ordered_keys = sorted(buckets.keys())

    partitions = []
    for label in ordered_keys:
        group = buckets.get(label, [])
        partitions.append(Partition(label=label, results=group, summary=summarize(group)))

    return PartitionReport(partitions=partitions)
