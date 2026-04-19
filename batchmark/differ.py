"""Diff two sets of TimingResults by job_id, highlighting new/removed/changed jobs."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from batchmark.timer import TimingResult


@dataclass
class DiffEntry:
    job_id: str
    status: str  # 'added', 'removed', 'changed', 'unchanged'
    baseline_duration: Optional[float] = None
    candidate_duration: Optional[float] = None
    delta: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "status": self.status,
            "baseline_duration": self.baseline_duration,
            "candidate_duration": self.candidate_duration,
            "delta": round(self.delta, 4) if self.delta is not None else None,
        }


@dataclass
class DiffReport:
    entries: List[DiffEntry] = field(default_factory=list)

    @property
    def added(self) -> List[DiffEntry]:
        return [e for e in self.entries if e.status == "added"]

    @property
    def removed(self) -> List[DiffEntry]:
        return [e for e in self.entries if e.status == "removed"]

    @property
    def changed(self) -> List[DiffEntry]:
        return [e for e in self.entries if e.status == "changed"]

    def to_dict(self) -> dict:
        return {"entries": [e.to_dict() for e in self.entries]}


def diff_results(
    baseline: List[TimingResult],
    candidate: List[TimingResult],
    epsilon: float = 0.001,
) -> DiffReport:
    base_map: Dict[str, TimingResult] = {r.job_id: r for r in baseline}
    cand_map: Dict[str, TimingResult] = {r.job_id: r for r in candidate}
    all_ids = sorted(set(base_map) | set(cand_map))
    entries: List[DiffEntry] = []
    for job_id in all_ids:
        b = base_map.get(job_id)
        c = cand_map.get(job_id)
        if b is None:
            entries.append(DiffEntry(job_id, "added", None, c.duration, None))
        elif c is None:
            entries.append(DiffEntry(job_id, "removed", b.duration, None, None))
        else:
            delta = (c.duration - b.duration) if (c.duration is not None and b.duration is not None) else None
            status = "unchanged"
            if delta is not None and abs(delta) > epsilon:
                status = "changed"
            entries.append(DiffEntry(job_id, status, b.duration, c.duration, delta))
    return DiffReport(entries=entries)
