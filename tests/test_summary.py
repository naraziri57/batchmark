"""Tests for batchmark.summary module."""

import pytest

from batchmark.timer import TimingResult
from batchmark.summary import summarize, Summary


def _make_result(duration: float, success: bool = True) -> TimingResult:
    return TimingResult(
        job_id="job",
        start_time=0.0,
        end_time=duration,
        duration=duration,
        success=success,
        error=None if success else "err",
    )


def test_empty_summarize():
    s = summarize([])
    assert s.total == 0
    assert s.succeeded == 0
    assert s.failed == 0
    assert s.avg_duration == 0.0
    assert s.median_duration == 0.0
    d = s.to_dict()
    assert d["min_duration_s"] is None
    assert d["max_duration_s"] is None


def test_all_success():
    results = [_make_result(d) for d in [1.0, 2.0, 3.0]]
    s = summarize(results)
    assert s.total == 3
    assert s.succeeded == 3
    assert s.failed == 0
    assert s.min_duration == 1.0
    assert s.max_duration == 3.0
    assert s.avg_duration == pytest.approx(2.0)
    assert s.median_duration == pytest.approx(2.0)


def test_mixed_success_failure():
    results = [
        _make_result(1.0, success=True),
        _make_result(5.0, success=False),
        _make_result(3.0, success=True),
    ]
    s = summarize(results)
    assert s.total == 3
    assert s.succeeded == 2
    assert s.failed == 1
    assert s.max_duration == 5.0


def test_even_count_median():
    results = [_make_result(d) for d in [1.0, 2.0, 3.0, 4.0]]
    s = summarize(results)
    assert s.median_duration == pytest.approx(2.5)


def test_to_dict_keys():
    results = [_make_result(2.5)]
    d = summarize(results).to_dict()
    expected_keys = {
        "total", "succeeded", "failed",
        "total_duration_s", "min_duration_s", "max_duration_s",
        "avg_duration_s", "median_duration_s",
    }
    assert expected_keys == set(d.keys())
    assert d["total_duration_s"] == pytest.approx(2.5)


def test_all_failed():
    """Summary should still compute durations correctly when all jobs fail."""
    results = [_make_result(d, success=False) for d in [2.0, 4.0]]
    s = summarize(results)
    assert s.total == 2
    assert s.succeeded == 0
    assert s.failed == 2
    assert s.min_duration == pytest.approx(2.0)
    assert s.max_duration == pytest.approx(4.0)
    assert s.avg_duration == pytest.approx(3.0)
