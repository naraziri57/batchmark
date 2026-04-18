"""Normalize TimingResult durations relative to a baseline or max value."""

from typing import List, Optional
from batchmark.timer import TimingResult


def normalize_by_max(results: List[TimingResult]) -> List[dict]:
    """Return results with duration normalized to [0.0, 1.0] by max duration."""
    durations = [r.duration for r in results if r.duration is not None]
    if not durations:
        return [{"job_id": r.job_id, "normalized": None, "raw": r.duration} for r in results]
    max_dur = max(durations)
    out = []
    for r in results:
        norm = (r.duration / max_dur) if r.duration is not None and max_dur > 0 else None
        out.append({"job_id": r.job_id, "normalized": round(norm, 6) if norm is not None else None, "raw": r.duration})
    return out


def normalize_by_baseline(results: List[TimingResult], baseline: float) -> List[dict]:
    """Return results with duration normalized relative to a fixed baseline value."""
    if baseline <= 0:
        raise ValueError("baseline must be a positive number")
    out = []
    for r in results:
        norm = (r.duration / baseline) if r.duration is not None else None
        out.append({"job_id": r.job_id, "normalized": round(norm, 6) if norm is not None else None, "raw": r.duration})
    return out


def normalize(results: List[TimingResult], baseline: Optional[float] = None) -> List[dict]:
    """Normalize results. Uses baseline if provided, otherwise normalizes by max."""
    if baseline is not None:
        return normalize_by_baseline(results, baseline)
    return normalize_by_max(results)
