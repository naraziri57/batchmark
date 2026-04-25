"""Pivot timing results by a key field, producing a matrix of job_id vs pivot value."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional
from batchmark.timer import TimingResult


@dataclass
class PivotCell:
    job_id: str
    pivot_value: str
    count: int
    avg_duration: Optional[float]
    success_count: int

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "pivot_value": self.pivot_value,
            "count": self.count,
            "avg_duration": round(self.avg_duration, 4) if self.avg_duration is not None else None,
            "success_count": self.success_count,
        }


@dataclass
class PivotReport:
    pivot_key: str
    pivot_values: List[str]
    job_ids: List[str]
    cells: Dict[str, Dict[str, PivotCell]] = field(default_factory=dict)

    def get(self, job_id: str, pivot_value: str) -> Optional[PivotCell]:
        return self.cells.get(job_id, {}).get(pivot_value)

    def to_dict(self) -> dict:
        return {
            "pivot_key": self.pivot_key,
            "pivot_values": self.pivot_values,
            "job_ids": self.job_ids,
            "cells": {
                jid: {pv: cell.to_dict() for pv, cell in pv_map.items()}
                for jid, pv_map in self.cells.items()
            },
        }


def pivot_results(
    results: List[TimingResult],
    key_fn: Callable[[TimingResult], Optional[str]],
    pivot_key: str = "pivot",
) -> PivotReport:
    """Group results by (job_id, pivot_value) and compute per-cell stats."""
    raw: Dict[str, Dict[str, List[TimingResult]]] = {}
    for r in results:
        pv = key_fn(r)
        if pv is None:
            continue
        raw.setdefault(r.job_id, {}).setdefault(pv, []).append(r)

    all_pivot_values: List[str] = sorted({pv for pv_map in raw.values() for pv in pv_map})
    all_job_ids: List[str] = sorted(raw.keys())

    cells: Dict[str, Dict[str, PivotCell]] = {}
    for job_id, pv_map in raw.items():
        cells[job_id] = {}
        for pv, group in pv_map.items():
            durations = [r.duration for r in group if r.duration is not None]
            avg = sum(durations) / len(durations) if durations else None
            cells[job_id][pv] = PivotCell(
                job_id=job_id,
                pivot_value=pv,
                count=len(group),
                avg_duration=avg,
                success_count=sum(1 for r in group if r.success),
            )

    return PivotReport(
        pivot_key=pivot_key,
        pivot_values=all_pivot_values,
        job_ids=all_job_ids,
        cells=cells,
    )
