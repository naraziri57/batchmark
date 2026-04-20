"""Correlator: find correlations between job duration and metadata tags/labels.

Given a list of AnnotatedResult or plain TimingResult objects, computes
Pearson correlation coefficients between numeric tag values and duration.
Also supports grouping by a categorical tag to compare mean durations.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

from batchmark.timer import TimingResult


@dataclass
class CorrelationEntry:
    """Pearson correlation between a numeric tag and duration."""

    tag_key: str
    correlation: float  # -1.0 to 1.0; NaN if not computable
    sample_size: int

    def to_dict(self) -> dict:
        corr = self.correlation if not math.isnan(self.correlation) else None
        return {
            "tag_key": self.tag_key,
            "correlation": corr,
            "sample_size": self.sample_size,
        }


@dataclass
class GroupStat:
    """Mean duration for a group defined by a categorical tag value."""

    tag_key: str
    tag_value: str
    count: int
    mean_duration: Optional[float]

    def to_dict(self) -> dict:
        return {
            "tag_key": self.tag_key,
            "tag_value": self.tag_value,
            "count": self.count,
            "mean_duration": round(self.mean_duration, 6) if self.mean_duration is not None else None,
        }


@dataclass
class CorrelationReport:
    """Full correlation analysis output."""

    numeric_correlations: List[CorrelationEntry] = field(default_factory=list)
    group_stats: List[GroupStat] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "numeric_correlations": [e.to_dict() for e in self.numeric_correlations],
            "group_stats": [g.to_dict() for g in self.group_stats],
        }


def _pearson(xs: List[float], ys: List[float]) -> float:
    """Compute Pearson r for two equal-length lists. Returns NaN on failure."""
    n = len(xs)
    if n < 2:
        return math.nan
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    den_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
    den_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))
    if den_x == 0 or den_y == 0:
        return math.nan
    return num / (den_x * den_y)


def correlate(
    results: Sequence,
    tag_keys: Optional[List[str]] = None,
) -> CorrelationReport:
    """Build a CorrelationReport from results.

    Works with plain TimingResult objects or AnnotatedResult wrappers
    (anything with a `.tags` dict attribute and a `.result` or direct
    `.duration` attribute).

    Args:
        results: Sequence of result objects.
        tag_keys: Optional list of tag keys to analyse. If None, all
                  discovered tag keys are used.

    Returns:
        CorrelationReport with numeric correlations and group stats.
    """
    if not results:
        return CorrelationReport()

    # Normalise: extract (duration, tags) pairs
    pairs: List[tuple] = []
    for r in results:
        # Support AnnotatedResult (has .result and .tags) or plain TimingResult
        if hasattr(r, "tags") and hasattr(r, "result"):
            duration = r.result.duration
            tags: Dict[str, str] = r.tags
        elif hasattr(r, "duration"):
            duration = r.duration
            tags = getattr(r, "tags", {})
        else:
            continue
        pairs.append((duration, tags))

    # Collect all tag keys if not specified
    all_keys: set = set()
    for _, tags in pairs:
        all_keys.update(tags.keys())
    keys_to_check = list(tag_keys) if tag_keys is not None else sorted(all_keys)

    numeric_correlations: List[CorrelationEntry] = []
    group_stats: List[GroupStat] = []

    for key in keys_to_check:
        numeric_xs: List[float] = []
        numeric_ys: List[float] = []
        groups: Dict[str, List[float]] = {}

        for duration, tags in pairs:
            if key not in tags:
                continue
            raw = tags[key]
            # Try numeric interpretation first
            try:
                val = float(raw)
                if duration is not None:
                    numeric_xs.append(val)
                    numeric_ys.append(duration)
            except (ValueError, TypeError):
                # Categorical grouping
                bucket = str(raw)
                if bucket not in groups:
                    groups[bucket] = []
                if duration is not None:
                    groups[bucket].append(duration)

        if numeric_xs:
            corr = _pearson(numeric_xs, numeric_ys)
            numeric_correlations.append(
                CorrelationEntry(
                    tag_key=key,
                    correlation=corr,
                    sample_size=len(numeric_xs),
                )
            )

        for tag_val, durations in sorted(groups.items()):
            mean_dur = sum(durations) / len(durations) if durations else None
            group_stats.append(
                GroupStat(
                    tag_key=key,
                    tag_value=tag_val,
                    count=len(durations),
                    mean_duration=mean_dur,
                )
            )

    return CorrelationReport(
        numeric_correlations=numeric_correlations,
        group_stats=group_stats,
    )
