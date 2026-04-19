"""Detect consecutive success/failure streaks in job results."""
from dataclasses import dataclass, field
from typing import List, Dict
from batchmark.timer import TimingResult


@dataclass
class Streak:
    job_id: str
    status: str  # 'success' or 'failed'
    length: int

    def to_dict(self) -> dict:
        return {"job_id": self.job_id, "status": self.status, "length": self.length}


@dataclass
class StreakerReport:
    streaks: List[Streak] = field(default_factory=list)

    def longest(self) -> Streak | None:
        if not self.streaks:
            return None
        return max(self.streaks, key=lambda s: s.length)

    def to_dict(self) -> dict:
        return {
            "streaks": [s.to_dict() for s in self.streaks],
            "longest": self.longest().to_dict() if self.longest() else None,
        }


def detect_streaks(results: List[TimingResult]) -> StreakerReport:
    """Group consecutive results by job_id and detect status streaks."""
    if not results:
        return StreakerReport()

    # group by job_id preserving order
    groups: Dict[str, List[str]] = {}
    for r in results:
        groups.setdefault(r.job_id, []).append("success" if r.success else "failed")

    streaks: List[Streak] = []
    for job_id, statuses in groups.items():
        current = statuses[0]
        length = 1
        for s in statuses[1:]:
            if s == current:
                length += 1
            else:
                streaks.append(Streak(job_id=job_id, status=current, length=length))
                current = s
                length = 1
        streaks.append(Streak(job_id=job_id, status=current, length=length))

    return StreakerReport(streaks=streaks)
