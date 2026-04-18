"""Tests for batchmark.filter module."""

import pytest
from batchmark.timer import TimingResult
from batchmark.filter import filter_results


def _make_result(job_name="job", duration=1.0, success=True) -> TimingResult:
    return TimingResult(job_name=job_name, duration=duration, success=success)


def test_no_filters_returns_all():
    results = [_make_result(), _make_result("job2"), _make_result("job3", success=False)]
    assert filter_results(results) == results


def test_success_only():
    results = [
        _make_result("a", success=True),
        _make_result("b", success=False),
        _make_result("c", success=True),
    ]
    out = filter_results(results, success_only=True)
    assert len(out) == 2
    assert all(r.success for r in out)


def test_failed_only():
    results = [
        _make_result("a", success=True),
        _make_result("b", success=False),
    ]
    out = filter_results(results, failed_only=True)
    assert len(out) == 1
    assert not out[0].success


def test_success_and_failed_raises():
    with pytest.raises(ValueError, match="mutually exclusive"):
        filter_results([], success_only=True, failed_only=True)


def test_min_duration():
    results = [_make_result(duration=0.5), _make_result(duration=1.5), _make_result(duration=2.0)]
    out = filter_results(results, min_duration=1.0)
    assert len(out) == 2
    assert all(r.duration >= 1.0 for r in out)


def test_max_duration():
    results = [_make_result(duration=0.5), _make_result(duration=1.5), _make_result(duration=3.0)]
    out = filter_results(results, max_duration=2.0)
    assert len(out) == 2


def test_duration_range():
    results = [_make_result(duration=d) for d in [0.1, 1.0, 2.0, 5.0]]
    out = filter_results(results, min_duration=0.5, max_duration=3.0)
    assert len(out) == 2


def test_job_name_filter():
    results = [
        _make_result("alpha"),
        _make_result("beta"),
        _make_result("alpha"),
    ]
    out = filter_results(results, job_name="alpha")
    assert len(out) == 2
    assert all(r.job_name == "alpha" for r in out)


def test_combined_filters():
    results = [
        _make_result("alpha", duration=1.0, success=True),
        _make_result("alpha", duration=0.1, success=True),
        _make_result("alpha", duration=1.5, success=False),
    ]
    out = filter_results(results, job_name="alpha", success_only=True, min_duration=0.5)
    assert len(out) == 1
    assert out[0].duration == 1.0


def test_empty_input():
    assert filter_results([]) == []
