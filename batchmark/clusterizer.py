"""Group timing results into clusters based on duration proximity."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from batchmark.timer import TimingResult


@dataclass
class Cluster:
    label: str
    min_duration: Optional[float]
    max_duration: Optional[float]
    results: List[TimingResult] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.results)

    @property
    def success_count(self) -> int:
        return sum(1 for r in self.results if r.success)

    @property
    def avg_duration(self) -> Optional[float]:
        durations = [r.duration for r in self.results if r.duration is not None]
        return sum(durations) / len(durations) if durations else None

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "min_duration": self.min_duration,
            "max_duration": self.max_duration,
            "count": self.count,
            "success_count": self.success_count,
            "avg_duration": round(self.avg_duration, 4) if self.avg_duration is not None else None,
        }


@dataclass
class ClusterReport:
    clusters: List[Cluster] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"clusters": [c.to_dict() for c in self.clusters]}


def clusterize(
    results: List[TimingResult],
    boundaries: List[float],
) -> ClusterReport:
    """Partition results into duration-based clusters defined by boundary values.

    Args:
        results: List of timing results to cluster.
        boundaries: Sorted list of upper-bound values for each cluster bucket.
                    Results exceeding all boundaries go into a final 'high' bucket.

    Returns:
        ClusterReport containing one Cluster per bucket.
    """
    if not boundaries:
        cluster = Cluster(label="all", min_duration=None, max_duration=None, results=list(results))
        return ClusterReport(clusters=[cluster])

    sorted_bounds = sorted(boundaries)
    clusters: List[Cluster] = []

    prev = None
    for bound in sorted_bounds:
        label = f"<{bound}s"
        clusters.append(Cluster(label=label, min_duration=prev, max_duration=bound))
        prev = bound

    clusters.append(Cluster(label=f">={sorted_bounds[-1]}s", min_duration=sorted_bounds[-1], max_duration=None))

    for result in results:
        d = result.duration
        placed = False
        for cluster in clusters[:-1]:
            if d is None or d < cluster.max_duration:  # type: ignore[operator]
                cluster.results.append(result)
                placed = True
                break
        if not placed:
            clusters[-1].results.append(result)

    return ClusterReport(clusters=clusters)
