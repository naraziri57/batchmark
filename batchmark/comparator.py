"""Compare two sets of benchmark results and produce a diff report."""

from dataclasses import dataclass
from typing import Dict, List, Optional
from batchmark.timer import TimingResult
from batchmark.aggregator import aggregate
from batchmark.summary import Summary


@dataclass
class JobComparison:
    job_id: str
    baseline_avg: Optional[float]
    candidate_avg: Optional[float]
    delta: Optional[float]          # candidate - baseline
    pct_change: Optional[float]     # delta / baseline * 100

    @property
    def improved(self) -> Optional[bool]:
        if self.delta is None:
            return None
        return self.delta < 0


@dataclass
class ComparisonReport:
    comparisons: List[JobComparison]

    def to_dict(self) -> Dict:
        return {
            "comparisons": [
                {
                    "job_id": c.job_id,
                    "baseline_avg": c.baseline_avg,
                    "candidate_avg": c.candidate_avg,
                    "delta": c.delta,
                    "pct_change": c.pct_change,
                    "improved": c.improved,
                }
                for c in self.comparisons
            ]
        }


def compare(
    baseline: List[TimingResult],
    candidate: List[TimingResult],
) -> ComparisonReport:
    """Compare candidate results against a baseline by job_id."""
    base_map: Dict[str, Summary] = aggregate(baseline)
    cand_map: Dict[str, Summary] = aggregate(candidate)

    all_ids = sorted(set(base_map) | set(cand_map))
    comparisons: List[JobComparison] = []

    for job_id in all_ids:
        b_avg = base_map[job_id].avg_duration if job_id in base_map else None
        c_avg = cand_map[job_id].avg_duration if job_id in cand_map else None

        if b_avg is not None and c_avg is not None:
            delta = c_avg - b_avg
            pct = (delta / b_avg * 100) if b_avg != 0 else None
        else:
            delta = None
            pct = None

        comparisons.append(JobComparison(job_id, b_avg, c_avg, delta, pct))

    return ComparisonReport(comparisons)
