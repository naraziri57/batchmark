"""Filter TimingResults based on various criteria."""

from typing import List, Optional
from batchmark.timer import TimingResult


def filter_results(
    results: List[TimingResult],
    *,
    success_only: bool = False,
    failed_only: bool = False,
    min_duration: Optional[float] = None,
    max_duration: Optional[float] = None,
    job_name: Optional[str] = None,
) -> List[TimingResult]:
    """Return a filtered subset of timing results.

    Args:
        results: List of TimingResult to filter.
        success_only: If True, keep only successful jobs.
        failed_only: If True, keep only failed jobs.
        min_duration: Exclude results with duration below this value (seconds).
        max_duration: Exclude results with duration above this value (seconds).
        job_name: Keep only results whose job_name matches exactly.

    Returns:
        Filtered list of TimingResult.
    """
    if success_only and failed_only:
        raise ValueError("success_only and failed_only are mutually exclusive")

    filtered = list(results)

    if success_only:
        filtered = [r for r in filtered if r.success]
    elif failed_only:
        filtered = [r for r in filtered if not r.success]

    if min_duration is not None:
        filtered = [r for r in filtered if r.duration >= min_duration]

    if max_duration is not None:
        filtered = [r for r in filtered if r.duration <= max_duration]

    if job_name is not None:
        filtered = [r for r in filtered if r.job_name == job_name]

    return filtered
