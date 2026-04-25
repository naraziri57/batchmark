"""Assign severity levels to timing results based on configurable thresholds."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from batchmark.timer import TimingResult

LEVELS = ("ok", "warn", "critical")


@dataclass
class LeveledResult:
    result: TimingResult
    level: str  # "ok" | "warn" | "critical"
    reason: str

    def to_dict(self) -> dict:
        d = {
            "job_id": self.result.job_id,
            "duration": self.result.duration,
            "success": self.result.success,
            "level": self.level,
            "reason": self.reason,
        }
        return d


@dataclass
class LevelReport:
    items: List[LeveledResult] = field(default_factory=list)

    def by_level(self, level: str) -> List[LeveledResult]:
        return [i for i in self.items if i.level == level]

    @property
    def critical_count(self) -> int:
        return len(self.by_level("critical"))

    @property
    def warn_count(self) -> int:
        return len(self.by_level("warn"))

    def to_dict(self) -> dict:
        return {
            "total": len(self.items),
            "critical": self.critical_count,
            "warn": self.warn_count,
            "ok": len(self.by_level("ok")),
            "items": [i.to_dict() for i in self.items],
        }


def level_results(
    results: List[TimingResult],
    warn_above: Optional[float] = None,
    critical_above: Optional[float] = None,
    failure_level: str = "critical",
    per_job: Optional[Dict[str, Dict[str, float]]] = None,
) -> LevelReport:
    """Assign a severity level to each result.

    Args:
        results: list of TimingResult objects.
        warn_above: global warn threshold in seconds.
        critical_above: global critical threshold in seconds.
        failure_level: level to assign to failed jobs (default 'critical').
        per_job: optional dict mapping job_id -> {warn_above, critical_above}.
    """
    per_job = per_job or {}
    items: List[LeveledResult] = []

    for r in results:
        overrides = per_job.get(r.job_id, {})
        w = overrides.get("warn_above", warn_above)
        c = overrides.get("critical_above", critical_above)

        if not r.success:
            items.append(LeveledResult(r, failure_level, "job failed"))
            continue

        dur = r.duration
        if dur is None:
            items.append(LeveledResult(r, "ok", "no duration"))
            continue

        if c is not None and dur > c:
            items.append(LeveledResult(r, "critical", f"duration {dur:.3f}s > critical {c}s"))
        elif w is not None and dur > w:
            items.append(LeveledResult(r, "warn", f"duration {dur:.3f}s > warn {w}s"))
        else:
            items.append(LeveledResult(r, "ok", "within thresholds"))

    return LevelReport(items=items)
