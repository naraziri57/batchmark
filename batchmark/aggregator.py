"""Aggregates multiple TimingResult lists into grouped statistics."""

from collections import defaultdict
from typing import Dict, List
from batchmark.timer import TimingResult
from batchmark.summary import Summary, summarize


def group_by_job_id(results: List[TimingResult]) -> Dict[str, List[TimingResult]]:
    """Group results by job_id."""
    groups: Dict[str, List[TimingResult]] = defaultdict(list)
    for r in results:
        groups[r.job_id].append(r)
    return dict(groups)


def aggregate(results: List[TimingResult]) -> Dict[str, Summary]:
    """Return a Summary per job_id."""
    groups = group_by_job_id(results)
    return {job_id: summarize(job_results) for job_id, job_results in groups.items()}


def aggregate_to_dict(results: List[TimingResult]) -> Dict[str, dict]:
    """Return serialisable dict of per-job summaries."""
    return {job_id: summary.to_dict() for job_id, summary in aggregate(results).items()}
