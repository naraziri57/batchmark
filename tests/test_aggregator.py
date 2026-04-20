"""Tests for batchmark.aggregator."""

import pytest
from batchmark.timer import TimingResult
from batchmark.aggregator import group_by_job_id, aggregate, aggregate_to_dict


def _make_result(job_id: str, duration: float, success: bool = True) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success, error=None)


def test_group_by_job_id_single_group():
    results = [_make_result("a", 1.0), _make_result("a", 2.0)]
    groups = group_by_job_id(results)
    assert list(groups.keys()) == ["a"]
    assert len(groups["a"]) == 2


def test_group_by_job_id_multiple_groups():
    results = [
        _make_result("a", 1.0),
        _make_result("b", 2.0),
        _make_result("a", 3.0),
    ]
    groups = group_by_job_id(results)
    assert set(groups.keys()) == {"a", "b"}
    assert len(groups["a"]) == 2
    assert len(groups["b"]) == 1


def test_group_by_job_id_empty():
    assert group_by_job_id([]) == {}


def test_aggregate_returns_summary_per_job():
    results = [
        _make_result("job1", 1.0),
        _make_result("job1", 3.0),
        _make_result("job2", 2.0),
    ]
    agg = aggregate(results)
    assert set(agg.keys()) == {"job1", "job2"}
    assert agg["job1"].total == 2
    assert agg["job2"].total == 1


def test_aggregate_avg_duration():
    results = [_make_result("x", 2.0), _make_result("x", 4.0)]
    agg = aggregate(results)
    assert agg["x"].avg_duration() == pytest.approx(3.0)


def test_aggregate_mixed_success_failure():
    results = [
        _make_result("j", 1.0, success=True),
        _make_result("j", 2.0, success=False),
    ]
    agg = aggregate(results)
    assert agg["j"].success_count == 1
    assert agg["j"].failure_count == 1


def test_aggregate_to_dict_structure():
    results = [_make_result("z", 5.0)]
    d = aggregate_to_dict(results)
    assert "z" in d
    assert "total" in d["z"]
    assert "success_count" in d["z"]
    assert "failure_count" in d["z"]


def test_aggregate_to_dict_values():
    """Check that aggregate_to_dict produces correct numeric values, not just keys."""
    results = [
        _make_result("k", 1.0, success=True),
        _make_result("k", 3.0, success=True),
        _make_result("k", 2.0, success=False),
    ]
    d = aggregate_to_dict(results)
    assert d["k"]["total"] == 3
    assert d["k"]["success_count"] == 2
    assert d["k"]["failure_count"] == 1


def test_aggregate_empty():
    assert aggregate([]) == {}
    assert aggregate_to_dict([]) == {}
