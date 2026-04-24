"""Tests for batchmark.bucketer."""
from __future__ import annotations
import pytest
from batchmark.timer import TimingResult
from batchmark.bucketer import bucket_results, BucketReport


def _r(job_id: str, duration=None, success: bool = True) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success)


def test_empty_results_returns_buckets_with_zero_count():
    report = bucket_results([], [1.0, 5.0])
    assert isinstance(report, BucketReport)
    for b in report.buckets:
        assert b.count == 0


def test_no_boundaries_single_bucket_contains_all():
    results = [_r("a", 2.0), _r("b", 8.0)]
    report = bucket_results(results, [])
    assert len(report.buckets) == 1
    assert report.buckets[0].label == "all"
    assert report.buckets[0].count == 2


def test_single_boundary_creates_two_buckets():
    results = [_r("a", 0.5), _r("b", 3.0)]
    report = bucket_results(results, [1.0])
    assert len(report.buckets) == 2
    labels = [b.label for b in report.buckets]
    assert "<1.0" in labels
    assert ">=1.0" in labels


def test_results_distributed_correctly():
    results = [_r("a", 0.5), _r("b", 1.5), _r("c", 6.0)]
    report = bucket_results(results, [1.0, 5.0])
    low = report.get("<1.0")
    mid = report.get("1.0-5.0")
    high = report.get(">=5.0")
    assert low is not None and low.count == 1
    assert mid is not None and mid.count == 1
    assert high is not None and high.count == 1


def test_none_duration_goes_to_first_bucket():
    results = [_r("x", None), _r("y", 2.0)]
    report = bucket_results(results, [1.0])
    first = report.buckets[0]
    assert any(r.job_id == "x" for r in first.results)


def test_boundary_is_inclusive_lower():
    results = [_r("a", 1.0), _r("b", 0.9)]
    report = bucket_results(results, [1.0])
    ge_bucket = report.get(">=1.0")
    lt_bucket = report.get("<1.0")
    assert ge_bucket is not None and any(r.job_id == "a" for r in ge_bucket.results)
    assert lt_bucket is not None and any(r.job_id == "b" for r in lt_bucket.results)


def test_to_dict_structure():
    results = [_r("a", 2.0, success=True), _r("b", 0.5, success=False)]
    report = bucket_results(results, [1.0])
    d = report.to_dict()
    assert "buckets" in d
    for entry in d["buckets"]:
        assert "label" in entry
        assert "count" in entry


def test_summary_reflects_success_failure():
    results = [_r("ok", 2.0, success=True), _r("fail", 3.0, success=False)]
    report = bucket_results(results, [1.0])
    ge = report.get(">=1.0")
    assert ge is not None
    s = ge.summary
    assert s is not None
    assert s.success_count == 1
    assert s.failure_count == 1


def test_get_returns_none_for_unknown_label():
    report = bucket_results([], [1.0])
    assert report.get("nonexistent") is None
