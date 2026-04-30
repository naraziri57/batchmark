from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional
from batchmark.timer import TimingResult
from batchmark.summary import Summary, summarize


@dataclass
class Group:
    label: str
    results: List[TimingResult]

    @property
    def count(self) -> int:
        return len(self.results)

    @property
    def success_count(self) -> int:
        return sum(1 for r in self.results if r.success)

    @property
    def failure_count(self) -> int:
        return self.count - self.success_count

    @property
    def summary(self) -> Summary:
        return summarize(self.results)

    def to_dict(self) -> dict:
        s = self.summary
        return {
            "label": self.label,
            "count": self.count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "avg_duration": s.avg_duration,
            "median_duration": s.median_duration,
        }


@dataclass
class GroupReport:
    groups: List[Group] = field(default_factory=list)

    def get(self, label: str) -> Optional[Group]:
        for g in self.groups:
            if g.label == label:
                return g
        return None

    @property
    def labels(self) -> List[str]:
        return [g.label for g in self.groups]

    def to_dict(self) -> dict:
        return {"groups": [g.to_dict() for g in self.groups]}


KeyFn = Callable[[TimingResult], str]


def group_results(
    results: List[TimingResult],
    key_fn: KeyFn,
    sort_labels: bool = True,
) -> GroupReport:
    buckets: Dict[str, List[TimingResult]] = {}
    for r in results:
        label = key_fn(r)
        buckets.setdefault(label, []).append(r)
    labels = sorted(buckets) if sort_labels else list(buckets)
    groups = [Group(label=lbl, results=buckets[lbl]) for lbl in labels]
    return GroupReport(groups=groups)


def group_by_status(results: List[TimingResult]) -> GroupReport:
    return group_results(results, lambda r: "success" if r.success else "failure")


def group_by_prefix(results: List[TimingResult], sep: str = "_") -> GroupReport:
    def _key(r: TimingResult) -> str:
        parts = r.job_id.split(sep, 1)
        return parts[0] if len(parts) > 1 else r.job_id

    return group_results(results, _key)
