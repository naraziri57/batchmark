"""Diff two snapshots and report what changed between them."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from batchmark.snapshotter import Snapshot
from batchmark.timer import TimingResult


@dataclass
class SnapshotDiffEntry:
    job_id: str
    before_duration: Optional[float]
    after_duration: Optional[float]
    before_success: bool
    after_success: bool

    @property
    def delta(self) -> Optional[float]:
        if self.before_duration is None or self.after_duration is None:
            return None
        return self.after_duration - self.before_duration

    @property
    def status_changed(self) -> bool:
        return self.before_success != self.after_success

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "before_duration": self.before_duration,
            "after_duration": self.after_duration,
            "delta": self.delta,
            "before_success": self.before_success,
            "after_success": self.after_success,
            "status_changed": self.status_changed,
        }


@dataclass
class SnapshotDiffReport:
    before_label: str
    after_label: str
    entries: List[SnapshotDiffEntry]

    def changed(self) -> List[SnapshotDiffEntry]:
        return [e for e in self.entries if e.delta != 0 or e.status_changed]

    def to_dict(self) -> dict:
        return {
            "before_label": self.before_label,
            "after_label": self.after_label,
            "entries": [e.to_dict() for e in self.entries],
        }


def diff_snapshots(before: Snapshot, after: Snapshot) -> SnapshotDiffReport:
    before_map: Dict[str, TimingResult] = {r.job_id: r for r in before.results}
    after_map: Dict[str, TimingResult] = {r.job_id: r for r in after.results}
    all_ids = sorted(set(before_map) | set(after_map))
    entries = []
    for job_id in all_ids:
        b = before_map.get(job_id)
        a = after_map.get(job_id)
        entries.append(
            SnapshotDiffEntry(
                job_id=job_id,
                before_duration=b.duration if b else None,
                after_duration=a.duration if a else None,
                before_success=b.success if b else False,
                after_success=a.success if a else False,
            )
        )
    return SnapshotDiffReport(
        before_label=before.label,
        after_label=after.label,
        entries=entries,
    )
