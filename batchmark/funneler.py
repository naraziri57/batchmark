"""funneler.py — filter results through a sequence of named stages."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, List, Optional
from batchmark.timer import TimingResult


@dataclass
class FunnelStage:
    name: str
    predicate: Callable[[TimingResult], bool]


@dataclass
class FunnelStep:
    stage: str
    passed: int
    dropped: int

    def to_dict(self) -> dict:
        return {"stage": self.stage, "passed": self.passed, "dropped": self.dropped}


@dataclass
class FunnelReport:
    steps: List[FunnelStep] = field(default_factory=list)
    final_results: List[TimingResult] = field(default_factory=list)

    @property
    def total_dropped(self) -> int:
        return sum(s.dropped for s in self.steps)

    def to_dict(self) -> dict:
        return {
            "steps": [s.to_dict() for s in self.steps],
            "total_dropped": self.total_dropped,
            "final_count": len(self.final_results),
        }


def funnel_results(
    results: List[TimingResult],
    stages: List[FunnelStage],
) -> FunnelReport:
    """Pass results through each stage in order, recording drop counts."""
    report = FunnelReport()
    current = list(results)
    for stage in stages:
        passed = [r for r in current if stage.predicate(r)]
        dropped = len(current) - len(passed)
        report.steps.append(FunnelStep(stage=stage.name, passed=len(passed), dropped=dropped))
        current = passed
    report.final_results = current
    return report
