"""Flatten nested aggregation or annotated results into a list of plain dicts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from batchmark.timer import TimingResult


@dataclass
class FlatRecord:
    job_id: str
    duration: Optional[float]
    success: bool
    tags: Dict[str, str] = field(default_factory=dict)
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "duration": self.duration,
            "success": self.success,
            **{f"tag_{k}": v for k, v in self.tags.items()},
            **self.extra,
        }


def flatten_results(
    results: List[TimingResult],
    extra_fields: Optional[Dict[str, Any]] = None,
) -> List[FlatRecord]:
    """Convert TimingResult objects into FlatRecord instances."""
    out: List[FlatRecord] = []
    for r in results:
        rec = FlatRecord(
            job_id=r.job_id,
            duration=r.duration,
            success=r.success,
            extra=dict(extra_fields) if extra_fields else {},
        )
        out.append(rec)
    return out


def flatten_annotated(
    annotated_results: List[Any],
) -> List[FlatRecord]:
    """Convert AnnotatedResult objects into FlatRecord instances."""
    out: List[FlatRecord] = []
    for ar in annotated_results:
        r: TimingResult = ar.result
        rec = FlatRecord(
            job_id=r.job_id,
            duration=r.duration,
            success=r.success,
            tags=dict(ar.tags),
        )
        out.append(rec)
    return out


def records_to_dicts(records: List[FlatRecord]) -> List[Dict[str, Any]]:
    """Serialize a list of FlatRecord to plain dicts."""
    return [r.to_dict() for r in records]
