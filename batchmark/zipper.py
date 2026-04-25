"""Zip (interleave) two runs of TimingResults by job_id for side-by-side comparison."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence
from batchmark.timer import TimingResult


@dataclass
class ZippedPair:
    job_id: str
    left: Optional[TimingResult]
    right: Optional[TimingResult]

    @property
    def left_duration(self) -> Optional[float]:
        return self.left.duration if self.left else None

    @property
    def right_duration(self) -> Optional[float]:
        return self.right.duration if self.right else None

    @property
    def delta(self) -> Optional[float]:
        if self.left_duration is None or self.right_duration is None:
            return None
        return self.right_duration - self.left_duration

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "left_duration": round(self.left_duration, 4) if self.left_duration is not None else None,
            "right_duration": round(self.right_duration, 4) if self.right_duration is not None else None,
            "delta": round(self.delta, 4) if self.delta is not None else None,
            "left_success": self.left.success if self.left else None,
            "right_success": self.right.success if self.right else None,
        }


@dataclass
class ZipReport:
    pairs: List[ZippedPair] = field(default_factory=list)

    @property
    def only_in_left(self) -> List[ZippedPair]:
        return [p for p in self.pairs if p.right is None]

    @property
    def only_in_right(self) -> List[ZippedPair]:
        return [p for p in self.pairs if p.left is None]

    @property
    def matched(self) -> List[ZippedPair]:
        return [p for p in self.pairs if p.left is not None and p.right is not None]

    def to_dict(self) -> dict:
        return {
            "pairs": [p.to_dict() for p in self.pairs],
            "matched_count": len(self.matched),
            "only_in_left_count": len(self.only_in_left),
            "only_in_right_count": len(self.only_in_right),
        }


def zip_results(
    left: Sequence[TimingResult],
    right: Sequence[TimingResult],
) -> ZipReport:
    left_map: Dict[str, TimingResult] = {r.job_id: r for r in left}
    right_map: Dict[str, TimingResult] = {r.job_id: r for r in right}
    all_ids = sorted(set(left_map) | set(right_map))
    pairs = [
        ZippedPair(
            job_id=jid,
            left=left_map.get(jid),
            right=right_map.get(jid),
        )
        for jid in all_ids
    ]
    return ZipReport(pairs=pairs)
