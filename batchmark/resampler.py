"""Resampler: resample timing results onto a uniform time grid.

Useful for aligning runs that were recorded at irregular intervals so that
downstream trend/smoother modules receive evenly-spaced data points.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from batchmark.timer import TimingResult


@dataclass
class ResampledPoint:
    """A single point on the resampled grid."""

    index: int                  # position in the resampled sequence (0-based)
    job_id: str
    raw_duration: Optional[float]   # original duration of the nearest result
    resampled_duration: Optional[float]  # interpolated or nearest-neighbour value
    source_index: int           # index of the original result used

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "job_id": self.job_id,
            "raw_duration": self.raw_duration,
            "resampled_duration": self.resampled_duration,
            "source_index": self.source_index,
        }


@dataclass
class ResampleReport:
    """Full report produced by resampling a list of results."""

    job_id: str
    n_original: int
    n_resampled: int
    points: List[ResampledPoint] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "n_original": self.n_original,
            "n_resampled": self.n_resampled,
            "points": [p.to_dict() for p in self.points],
        }


def _nearest(values: List[float], target_idx: float) -> int:
    """Return the index in *values* whose position is closest to *target_idx*."""
    best = 0
    best_dist = abs(target_idx - 0)
    for i in range(1, len(values)):
        d = abs(target_idx - i)
        if d < best_dist:
            best_dist = d
            best = i
    return best


def _lerp(a: Optional[float], b: Optional[float], t: float) -> Optional[float]:
    """Linear interpolation between *a* and *b* at position *t* in [0, 1]."""
    if a is None or b is None:
        return a if b is None else b
    return a + (b - a) * t


def resample(
    results: List[TimingResult],
    n: int,
    *,
    method: str = "nearest",
) -> ResampleReport:
    """Resample *results* (filtered to a single job_id) onto a grid of *n* points.

    Parameters
    ----------
    results:
        Timing results, all assumed to share the same ``job_id``.
    n:
        Number of output points.  Must be >= 1.
    method:
        Resampling strategy.  ``"nearest"`` picks the closest original sample;
        ``"linear"`` linearly interpolates between the two surrounding samples.

    Returns
    -------
    ResampleReport
    """
    if not results:
        job_id = "unknown"
        return ResampleReport(job_id=job_id, n_original=0, n_resampled=0, points=[])

    job_id = results[0].job_id
    durations: List[Optional[float]] = [r.duration for r in results]
    orig_n = len(durations)

    if n < 1:
        raise ValueError("n must be >= 1")

    if method not in ("nearest", "linear"):
        raise ValueError(f"Unknown resampling method: {method!r}")

    points: List[ResampledPoint] = []

    for i in range(n):
        # Map output index i to a fractional position in the original sequence.
        if n == 1:
            frac = 0.0
        else:
            frac = i / (n - 1) * (orig_n - 1)

        if method == "nearest":
            src_idx = round(frac)
            src_idx = max(0, min(orig_n - 1, src_idx))
            resampled_val = durations[src_idx]
        else:  # linear
            lo = int(frac)
            hi = min(lo + 1, orig_n - 1)
            t = frac - lo
            src_idx = lo
            resampled_val = _lerp(durations[lo], durations[hi], t)

        points.append(
            ResampledPoint(
                index=i,
                job_id=job_id,
                raw_duration=durations[src_idx],
                resampled_duration=resampled_val,
                source_index=src_idx,
            )
        )

    return ResampleReport(
        job_id=job_id,
        n_original=orig_n,
        n_resampled=n,
        points=points,
    )
