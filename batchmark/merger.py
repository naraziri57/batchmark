"""Merge multiple lists of TimingResults into a unified result set."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from batchmark.timer import TimingResult


@dataclass
class MergeReport:
    results: List[TimingResult]
    source_labels: List[str]
    conflicts: List[str] = field(default_factory=list)

    def total(self) -> int:
        return len(self.results)

    def conflict_count(self) -> int:
        return len(self.conflicts)

    def to_dict(self) -> dict:
        return {
            "total": self.total(),
            "source_labels": self.source_labels,
            "conflict_count": self.conflict_count(),
            "conflicts": self.conflicts,
        }


def merge(
    runs: List[List[TimingResult]],
    labels: Optional[List[str]] = None,
    on_conflict: str = "keep_all",
) -> MergeReport:
    """Merge multiple runs into one result list.

    Args:
        runs: List of result lists to merge.
        labels: Optional names for each run. Defaults to 'run_0', 'run_1', ...
        on_conflict: Strategy when same job_id appears multiple times.
            'keep_all'  – keep every occurrence (default)
            'keep_first' – keep only the first seen
            'keep_last'  – keep only the most recently seen
    """
    if labels is None:
        labels = [f"run_{i}" for i in range(len(runs))]

    if len(labels) != len(runs):
        raise ValueError("labels length must match runs length")

    if on_conflict not in {"keep_all", "keep_first", "keep_last"}:
        raise ValueError(f"Unknown on_conflict strategy: {on_conflict!r}")

    seen: dict[str, TimingResult] = {}
    merged: List[TimingResult] = []
    conflicts: List[str] = []

    for run in runs:
        for result in run:
            jid = result.job_id
            if jid in seen:
                if jid not in conflicts:
                    conflicts.append(jid)
                if on_conflict == "keep_all":
                    merged.append(result)
                elif on_conflict == "keep_last":
                    # replace previous occurrence in merged list
                    merged = [r for r in merged if r.job_id != jid]
                    merged.append(result)
                    seen[jid] = result
                # keep_first: do nothing
            else:
                seen[jid] = result
                merged.append(result)

    return MergeReport(results=merged, source_labels=labels, conflicts=conflicts)
