"""Sorting utilities for TimingResult lists."""

from typing import List, Optional
from batchmark.timer import TimingResult

VALID_KEYS = ("duration", "job_id", "status", "start_time")


def sort_results(
    results: List[TimingResult],
    key: str = "duration",
    reverse: bool = False,
) -> List[TimingResult]:
    """Return a sorted copy of results by the given key.

    Args:
        results: List of TimingResult objects.
        key: Attribute to sort by. One of 'duration', 'job_id',
             'status', 'start_time'.
        reverse: If True, sort descending.

    Returns:
        New sorted list.

    Raises:
        ValueError: If key is not a valid sort key.
    """
    if key not in VALID_KEYS:
        raise ValueError(
            f"Invalid sort key '{key}'. Choose from: {', '.join(VALID_KEYS)}"
        )

    def _get(r: TimingResult):
        value = getattr(r, key)
        # Handle None durations (failed jobs with no end time)
        if value is None:
            return float("inf") if not reverse else float("-inf")
        return value

    return sorted(results, key=_get, reverse=reverse)


def top_n(
    results: List[TimingResult],
    n: int,
    key: str = "duration",
    longest: bool = True,
) -> List[TimingResult]:
    """Return the top N results by duration (or another key).

    Args:
        results: List of TimingResult objects.
        n: Number of results to return.
        key: Attribute to sort by.
        longest: If True return the N longest/largest; else shortest/smallest.

    Returns:
        List of up to N TimingResult objects.
    """
    if n < 0:
        raise ValueError("n must be a non-negative integer")
    sorted_results = sort_results(results, key=key, reverse=longest)
    return sorted_results[:n]
