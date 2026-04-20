"""Snapshotter: capture and compare point-in-time result sets."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from batchmark.timer import TimingResult


@dataclass
class Snapshot:
    label: str
    timestamp: str
    results: List[TimingResult]

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "timestamp": self.timestamp,
            "results": [
                {
                    "job_id": r.job_id,
                    "duration": r.duration,
                    "success": r.success,
                    "error": r.error,
                }
                for r in self.results
            ],
        }


def _result_from_dict(d: dict) -> TimingResult:
    return TimingResult(
        job_id=d["job_id"],
        duration=d.get("duration"),
        success=d.get("success", True),
        error=d.get("error"),
    )


def save_snapshot(snapshot: Snapshot, directory: str) -> str:
    os.makedirs(directory, exist_ok=True)
    filename = f"{snapshot.label}.json"
    path = os.path.join(directory, filename)
    with open(path, "w") as fh:
        json.dump(snapshot.to_dict(), fh, indent=2)
    return path


def load_snapshot(label: str, directory: str) -> Snapshot:
    path = os.path.join(directory, f"{label}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Snapshot not found: {path}")
    with open(path) as fh:
        data = json.load(fh)
    results = [_result_from_dict(r) for r in data["results"]]
    return Snapshot(label=data["label"], timestamp=data["timestamp"], results=results)


def list_snapshots(directory: str) -> List[str]:
    if not os.path.isdir(directory):
        return []
    return sorted(
        f[:-5] for f in os.listdir(directory) if f.endswith(".json")
    )


def make_snapshot(label: str, results: List[TimingResult]) -> Snapshot:
    ts = datetime.now(timezone.utc).isoformat()
    return Snapshot(label=label, timestamp=ts, results=results)
