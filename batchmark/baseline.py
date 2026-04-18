"""Baseline management: save and load benchmark results as a named baseline."""

import json
import os
from typing import Optional

from batchmark.timer import TimingResult

DEFAULT_BASELINE_DIR = ".batchmark_baselines"


def save_baseline(name: str, results: list[TimingResult], directory: str = DEFAULT_BASELINE_DIR) -> str:
    """Serialize results to JSON and save under the given baseline name."""
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, f"{name}.json")
    data = [r.to_dict() for r in results]
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return path


def load_baseline(name: str, directory: str = DEFAULT_BASELINE_DIR) -> list[TimingResult]:
    """Load a previously saved baseline by name."""
    path = os.path.join(directory, f"{name}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Baseline '{name}' not found at {path}")
    with open(path, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Baseline '{name}' contains invalid JSON: {e}") from e
    if not isinstance(data, list):
        raise ValueError(f"Baseline '{name}' has unexpected format: expected a list")
    return [_from_dict(d) for d in data]


def list_baselines(directory: str = DEFAULT_BASELINE_DIR) -> list[str]:
    """Return names of all saved baselines."""
    if not os.path.isdir(directory):
        return []
    return [
        os.path.splitext(fname)[0]
        for fname in os.listdir(directory)
        if fname.endswith(".json")
    ]


def _from_dict(d: dict) -> TimingResult:
    return TimingResult(
        job_id=d["job_id"],
        duration=d.get("duration"),
        success=d["success"],
        error=d.get("error"),
    )
