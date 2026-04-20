"""stacker.py — stack multiple runs of results into a unified time-series view."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from batchmark.timer import TimingResult


@dataclass
class StackedRun:
    label: str
    results: List[TimingResult]

    @property
    def job_ids(self) -> List[str]:
        return [r.job_id for r in self.results]

    @property
    def success_count(self) -> int:
        return sum(1 for r in self.results if r.success)

    @property
    def avg_duration(self) -> Optional[float]:
        durations = [r.duration for r in self.results if r.duration is not None]
        if not durations:
            return None
        return sum(durations) / len(durations)

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "count": len(self.results),
            "success_count": self.success_count,
            "avg_duration": round(self.avg_duration, 4) if self.avg_duration is not None else None,
        }


@dataclass
class StackReport:
    runs: List[StackedRun] = field(default_factory=list)

    def labels(self) -> List[str]:
        return [r.label for r in self.runs]

    def by_label(self, label: str) -> Optional[StackedRun]:
        for run in self.runs:
            if run.label == label:
                return run
        return None

    def avg_durations(self) -> Dict[str, Optional[float]]:
        return {run.label: run.avg_duration for run in self.runs}

    def to_dict(self) -> dict:
        return {"runs": [r.to_dict() for r in self.runs]}


def stack_runs(labeled_batches: List[tuple]) -> StackReport:
    """Build a StackReport from a list of (label, results) tuples."""
    runs = []
    for label, results in labeled_batches:
        runs.append(StackedRun(label=label, results=list(results)))
    return StackReport(runs=runs)


def format_stack_text(report: StackReport) -> str:
    if not report.runs:
        return "No stacked runs."
    lines = ["Stacked Runs:"]
    for run in report.runs:
        avg = f"{run.avg_duration:.4f}s" if run.avg_duration is not None else "N/A"
        lines.append(
            f"  [{run.label}] count={len(run.results)} success={run.success_count} avg={avg}"
        )
    return "\n".join(lines)


def format_stack_json(report: StackReport) -> str:
    import json
    return json.dumps(report.to_dict(), indent=2)


def format_stack(report: StackReport, fmt: str = "text") -> str:
    if fmt == "json":
        return format_stack_json(report)
    return format_stack_text(report)
