"""High-level pipeline: filter -> sort -> aggregate -> format."""

from typing import List, Optional
from batchmark.timer import TimingResult
from batchmark.filter import filter_results
from batchmark.sorter import sort_results, top_n
from batchmark.aggregator import aggregate
from batchmark.formatter import format_aggregation


def run_pipeline(
    results: List[TimingResult],
    *,
    success_only: bool = False,
    failed_only: bool = False,
    sort_by: str = "duration",
    descending: bool = False,
    limit: Optional[int] = None,
    fmt: str = "text",
) -> str:
    """
    Filter, sort, optionally limit, aggregate and format a list of TimingResults.

    Returns formatted string output.
    """
    filtered = filter_results(results, success_only=success_only, failed_only=failed_only)
    sorted_results = sort_results(filtered, key=sort_by, descending=descending)
    if limit is not None:
        sorted_results = top_n(sorted_results, n=limit)
    agg = aggregate(sorted_results)
    return format_aggregation(agg, fmt=fmt)
