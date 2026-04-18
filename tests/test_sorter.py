"""Tests for batchmark.sorter."""

import pytest
from batchmark.sorter import sort_results, top_n
from batchmark.timer import TimingResult


def _make_result(job_id: str, duration, status: str = "success") -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, status=status, start_time=0.0)


def test_sort_by_duration_ascending():
    results = [
        _make_result("c", 3.0),
        _make_result("a", 1.0),
        _make_result("b", 2.0),
    ]
    sorted_r = sort_results(results, key="duration")
    assert [r.job_id for r in sorted_r] == ["a", "b", "c"]


def test_sort_by_duration_descending():
    results = [
        _make_result("a", 1.0),
        _make_result("c", 3.0),
        _make_result("b", 2.0),
    ]
    sorted_r = sort_results(results, key="duration", reverse=True)
    assert [r.job_id for r in sorted_r] == ["c", "b", "a"]


def test_sort_by_job_id():
    results = [
        _make_result("banana", 1.0),
        _make_result("apple", 2.0),
        _make_result("cherry", 3.0),
    ]
    sorted_r = sort_results(results, key="job_id")
    assert [r.job_id for r in sorted_r] == ["apple", "banana", "cherry"]


def test_sort_none_duration_goes_last():
    results = [
        _make_result("a", None, status="failed"),
        _make_result("b", 1.0),
        _make_result("c", 2.0),
    ]
    sorted_r = sort_results(results, key="duration")
    assert sorted_r[-1].job_id == "a"


def test_sort_invalid_key_raises():
    results = [_make_result("a", 1.0)]
    with pytest.raises(ValueError, match="Invalid sort key"):
        sort_results(results, key="nonexistent")


def test_sort_empty_list():
    assert sort_results([], key="duration") == []


def test_top_n_longest():
    results = [_make_result(str(i), float(i)) for i in range(5)]
    top = top_n(results, n=3, key="duration", longest=True)
    assert [r.job_id for r in top] == ["4", "3", "2"]


def test_top_n_shortest():
    results = [_make_result(str(i), float(i)) for i in range(5)]
    top = top_n(results, n=2, key="duration", longest=False)
    assert [r.job_id for r in top] == ["0", "1"]


def test_top_n_zero():
    results = [_make_result("a", 1.0)]
    assert top_n(results, n=0) == []


def test_top_n_negative_raises():
    with pytest.raises(ValueError, match="non-negative"):
        top_n([], n=-1)


def test_top_n_larger_than_list():
    results = [_make_result("a", 1.0), _make_result("b", 2.0)]
    assert len(top_n(results, n=10)) == 2
