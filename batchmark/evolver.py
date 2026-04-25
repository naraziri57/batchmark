"""evolver.py — track how job durations evolve across multiple labeled runs."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from batchmark.timer import TimingResult


@dataclass
class EvolvedJob:
    job_id: str
    runs: List[str]          # ordered run labels
    durations: List[Optional[float]]  # parallel to runs; None if job absent/failed

    def first_seen(self) -> Optional[str]:
        for label, dur in zip(self.runs, self.durations):
            if dur is not None:
                return label
        return None

    def last_seen(self) -> Optional[str]:
        for label, dur in zip(reversed(self.runs), reversed(self.durations)):
            if dur is not None:
                return label
        return None

    def net_change(self) -> Optional[float]:
        """last duration minus first duration; None if fewer than two data points."""
        valid = [d for d in self.durations if d is not None]
        if len(valid) < 2:
            return None
        return valid[-1] - valid[0]

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "runs": self.runs,
            "durations": self.durations,
            "net_change": self.net_change(),
        }


@dataclass
class EvolverReport:
    run_labels: List[str]
    jobs: List[EvolvedJob] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "run_labels": self.run_labels,
            "jobs": [j.to_dict() for j in self.jobs],
        }


def evolve(
    runs: Dict[str, List[TimingResult]]
) -> EvolverReport:
    """Build an EvolverReport from an ordered dict of {label: results}."""
    labels = list(runs.keys())
    job_index: Dict[str, List[Optional[float]]] = {}

    for label in labels:
        seen: Dict[str, Optional[float]] = {}
        for r in runs[label]:
            seen[r.job_id] = r.duration if r.success else None
        for jid in job_index:
            job_index[jid].append(seen.get(jid))
        for jid, dur in seen.items():
            if jid not in job_index:
                job_index[jid] = [None] * (labels.index(label)) + [dur]

    # pad any jobs that ended before the last run
    for jid, durs in job_index.items():
        while len(durs) < len(labels):
            durs.append(None)

    jobs = [
        EvolvedJob(job_id=jid, runs=labels, durations=durs)
        for jid, durs in sorted(job_index.items())
    ]
    return EvolverReport(run_labels=labels, jobs=jobs)
