"""Scale job durations by a factor or to a target range."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from batchmark.timer import TimingResult


@dataclass
class ScaledResult:
    result: TimingResult
    original_duration: Optional[float]
    scaled_duration: Optional[float]
    scale_factor: float

    def to_dict(self) -> dict:
        return {
            "job_id": self.result.job_id,
            "success": self.result.success,
            "original_duration": round(self.original_duration, 4) if self.original_duration is not None else None,
            "scaled_duration": round(self.scaled_duration, 4) if self.scaled_duration is not None else None,
            "scale_factor": round(self.scale_factor, 6),
        }


@dataclass
class ScaleReport:
    scaled: List[ScaledResult] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.scaled)

    @property
    def affected(self) -> int:
        return sum(1 for s in self.scaled if s.original_duration != s.scaled_duration)

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "affected": self.affected,
            "scaled": [s.to_dict() for s in self.scaled],
        }


def scale_results(
    results: List[TimingResult],
    factor: Optional[float] = None,
    target_min: Optional[float] = None,
    target_max: Optional[float] = None,
) -> ScaleReport:
    """Scale durations by a fixed factor, or linearly map into [target_min, target_max]."""
    if factor is not None and (target_min is not None or target_max is not None):
        raise ValueError("Specify either factor or target range, not both.")

    durations = [r.duration for r in results if r.duration is not None]
    src_min = min(durations) if durations else None
    src_max = max(durations) if durations else None
    src_range = (src_max - src_min) if (src_min is not None and src_max != src_min) else None

    scaled_list: List[ScaledResult] = []
    for r in results:
        orig = r.duration
        if orig is None:
            scaled_list.append(ScaledResult(r, None, None, factor if factor is not None else 1.0))
            continue

        if factor is not None:
            new_dur = orig * factor
            used_factor = factor
        elif target_min is not None and target_max is not None and src_range is not None:
            new_dur = target_min + (orig - src_min) / src_range * (target_max - target_min)
            used_factor = new_dur / orig if orig != 0 else 1.0
        elif target_min is not None and target_max is not None:
            # all durations are equal — map to midpoint
            new_dur = (target_min + target_max) / 2.0
            used_factor = new_dur / orig if orig != 0 else 1.0
        else:
            new_dur = orig
            used_factor = 1.0

        scaled_list.append(ScaledResult(r, orig, new_dur, used_factor))

    return ScaleReport(scaled=scaled_list)
