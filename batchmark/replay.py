"""Replay recorded job results from a JSON file for re-analysis."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from batchmark.timer import TimingResult


def _result_from_dict(d: dict) -> TimingResult:
    return TimingResult(
        job_id=d["job_id"],
        duration=d.get("duration"),
        success=d.get("success", True),
        error=d.get("error"),
        metadata=d.get("metadata", {}),
    )


def load_replay(path: str | Path) -> List[TimingResult]:
    """Load a list of TimingResult from a JSON replay file."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Replay file not found: {path}")
    try:
        data = json.loads(p.read_text())
    except json.JSONDecodeError as e:
        raise ValueError(f"Replay file contains invalid JSON: {e}") from e
    if not isinstance(data, list):
        raise ValueError("Replay file must contain a JSON array of results")
    return [_result_from_dict(item) for item in data]


def save_replay(results: List[TimingResult], path: str | Path) -> None:
    """Save a list of TimingResult to a JSON replay file."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = [
        {
            "job_id": r.job_id,
            "duration": r.duration,
            "success": r.success,
            "error": r.error,
            "metadata": r.metadata,
        }
        for r in results
    ]
    p.write_text(json.dumps(payload, indent=2))


def filter_replay(
    results: List[TimingResult],
    job_id: Optional[str] = None,
    success_only: bool = False,
) -> List[TimingResult]:
    """Optionally filter replayed results by job_id or success status."""
    out = results
    if job_id is not None:
        out = [r for r in out if r.job_id == job_id]
    if success_only:
        out = [r for r in out if r.success]
    return out
