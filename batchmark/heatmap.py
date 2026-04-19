"""Generate a simple ASCII heatmap of job durations across runs."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import json


@dataclass
class HeatmapCell:
    job_id: str
    run_index: int
    duration: Optional[float]
    bucket: str  # "cold", "warm", "hot"

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "run_index": self.run_index,
            "duration": self.duration,
            "bucket": self.bucket,
        }


def _bucket(duration: Optional[float], low: float, high: float) -> str:
    if duration is None:
        return "none"
    if duration <= low:
        return "cold"
    if duration <= high:
        return "warm"
    return "hot"


def build_heatmap(runs: List[List], low_pct: float = 0.33, high_pct: float = 0.66) -> List[HeatmapCell]:
    """runs is a list of result lists (each inner list is one run)."""
    all_durations = [
        r.duration for run in runs for r in run if r.duration is not None
    ]
    if not all_durations:
        low = high = 0.0
    else:
        sorted_d = sorted(all_durations)
        n = len(sorted_d)
        low = sorted_d[int(n * low_pct)]
        high = sorted_d[int(n * high_pct)]

    cells: List[HeatmapCell] = []
    for run_idx, run in enumerate(runs):
        for result in run:
            cells.append(HeatmapCell(
                job_id=result.job_id,
                run_index=run_idx,
                duration=result.duration,
                bucket=_bucket(result.duration, low, high),
            ))
    return cells


_SYMBOLS = {"cold": ".", "warm": "o", "hot": "#", "none": "?"}


def format_heatmap_text(cells: List[HeatmapCell]) -> str:
    if not cells:
        return "(no data)"
    job_ids = sorted({c.job_id for c in cells})
    runs = sorted({c.run_index for c in cells})
    lookup: Dict[tuple, str] = {(c.job_id, c.run_index): _SYMBOLS[c.bucket] for c in cells}
    header = "job_id          " + " ".join(f"r{r}" for r in runs)
    lines = [header]
    for jid in job_ids:
        row = f"{jid:<16}" + "  ".join(lookup.get((jid, r), " ") for r in runs)
        lines.append(row)
    lines.append("legend: .=cold  o=warm  #=hot  ?=missing")
    return "\n".join(lines)


def format_heatmap_json(cells: List[HeatmapCell]) -> str:
    return json.dumps([c.to_dict() for c in cells], indent=2)


def format_heatmap(cells: List[HeatmapCell], fmt: str = "text") -> str:
    if fmt == "json":
        return format_heatmap_json(cells)
    return format_heatmap_text(cells)
