"""Tests for batchmark.partitioner."""
from __future__ import annotations

import pytest
from batchmark.timer import TimingResult
from batchmark.partitioner import partition_results, Partition, PartitionReport


def _r(job_id: str, success: bool = True, duration: float = 1.0) -> TimingResult:
    return TimingResult(job_id=job_id, success=success, duration=duration)


def test_empty_returns_empty_report():
    report = partition_results([], key_fn=lambda r: r.job_id)
    assert isinstance(report, PartitionReport)
    assert report.partitions == []


def test_partition_by_status_two_groups():
    results = [_r("a", True), _r("b", False), _r("c", True)]
    report = partition_results(results, key_fn=lambda r: "ok" if r.success else "fail")
    labels = {p.label for p in report.partitions}
    assert labels == {"ok", "fail"}


def test_partition_counts_are_correct():
    results = [_r("a", True), _r("b", True), _r("c", False)]
    report = partition_results(results, key_fn=lambda r: "ok" if r.success else "fail")
    ok_part = report.get("ok")
    fail_part = report.get("fail")
    assert ok_part is not None and len(ok_part.results) == 2
    assert fail_part is not None and len(fail_part.results) == 1


def test_partition_summary_success_count():
    results = [_r("a", True, 2.0), _r("b", True, 4.0)]
    report = partition_results(results, key_fn=lambda r: "ok")
    p = report.get("ok")
    assert p is not None
    assert p.summary.success_count == 2
    assert p.summary.avg_duration == pytest.approx(3.0)


def test_labels_filters_partitions():
    results = [_r("a", True), _r("b", False)]
    report = partition_results(
        results,
        key_fn=lambda r: "ok" if r.success else "fail",
        labels=["ok"],
    )
    # 'fail' goes into 'other'
    assert report.get("ok") is not None
    other = report.get("other")
    assert other is not None
    assert len(other.results) == 1


def test_labels_ordering_preserved():
    results = [_r("x", True), _r("y", False)]
    report = partition_results(
        results,
        key_fn=lambda r: "ok" if r.success else "fail",
        labels=["fail", "ok"],
    )
    assert [p.label for p in report.partitions[:2]] == ["fail", "ok"]


def test_get_returns_none_for_missing_label():
    report = partition_results([], key_fn=lambda r: r.job_id)
    assert report.get("nonexistent") is None


def test_to_dict_structure():
    results = [_r("j1", True, 1.0)]
    report = partition_results(results, key_fn=lambda r: r.job_id)
    d = report.to_dict()
    assert "partitions" in d
    assert d["partitions"][0]["label"] == "j1"
    assert d["partitions"][0]["count"] == 1
