"""Tests for batchmark.splitter."""
from __future__ import annotations

import pytest

from batchmark.timer import TimingResult
from batchmark.splitter import (
    Split,
    SplitReport,
    split_results,
    split_by_status,
    split_by_job_id,
)


def _r(job_id: str, duration: float | None = 1.0, success: bool = True) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success, error=None)


# ---------------------------------------------------------------------------
# split_results
# ---------------------------------------------------------------------------

def test_empty_returns_empty_report():
    report = split_results([], key_fn=lambda r: r.job_id)
    assert report.splits == []
    assert report.labels() == []


def test_single_result_one_split():
    report = split_results([_r("job-a")], key_fn=lambda r: r.job_id)
    assert len(report.splits) == 1
    assert report.splits[0].label == "job-a"
    assert len(report.splits[0].results) == 1


def test_multiple_keys_produce_multiple_splits():
    results = [_r("a"), _r("b"), _r("a"), _r("c")]
    report = split_results(results, key_fn=lambda r: r.job_id)
    assert set(report.labels()) == {"a", "b", "c"}
    assert len(report.get("a").results) == 2
    assert len(report.get("b").results) == 1


def test_sort_labels_true_returns_alphabetical():
    results = [_r("z"), _r("a"), _r("m")]
    report = split_results(results, key_fn=lambda r: r.job_id, sort_labels=True)
    assert report.labels() == ["a", "m", "z"]


def test_sort_labels_false_preserves_insertion_order():
    results = [_r("z"), _r("a"), _r("m")]
    report = split_results(results, key_fn=lambda r: r.job_id, sort_labels=False)
    assert report.labels() == ["z", "a", "m"]


def test_summary_attached_to_split():
    results = [_r("x", duration=2.0), _r("x", duration=4.0)]
    report = split_results(results, key_fn=lambda r: r.job_id)
    split = report.get("x")
    assert split is not None
    assert split.summary.avg_duration == pytest.approx(3.0)


def test_get_missing_label_returns_none():
    report = split_results([_r("a")], key_fn=lambda r: r.job_id)
    assert report.get("nonexistent") is None


def test_to_dict_structure():
    report = split_results([_r("a", duration=1.0)], key_fn=lambda r: r.job_id)
    d = report.to_dict()
    assert "splits" in d
    assert d["splits"][0]["label"] == "a"
    assert d["splits"][0]["count"] == 1
    assert "summary" in d["splits"][0]


# ---------------------------------------------------------------------------
# split_by_status
# ---------------------------------------------------------------------------

def test_split_by_status_groups_correctly():
    results = [_r("a", success=True), _r("b", success=False), _r("c", success=True)]
    report = split_by_status(results)
    assert set(report.labels()) == {"success", "failed"}
    assert len(report.get("success").results) == 2
    assert len(report.get("failed").results) == 1


def test_split_by_status_all_success():
    results = [_r("a"), _r("b")]
    report = split_by_status(results)
    assert report.labels() == ["success"]


# ---------------------------------------------------------------------------
# split_by_job_id
# ---------------------------------------------------------------------------

def test_split_by_job_id_convenience():
    results = [_r("job-1"), _r("job-2"), _r("job-1")]
    report = split_by_job_id(results)
    assert "job-1" in report.labels()
    assert "job-2" in report.labels()
    assert len(report.get("job-1").results) == 2
