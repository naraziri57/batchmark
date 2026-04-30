"""Tests for batchmark.stamper."""
from __future__ import annotations

import pytest

from batchmark.timer import TimingResult
from batchmark.stamper import (
    StampedResult,
    StampReport,
    stamp_results,
)


def _r(job_id: str = "job-1", success: bool = True, duration: float = 1.0) -> TimingResult:
    return TimingResult(job_id=job_id, success=success, duration=duration)


def _fixed_clock(values):
    it = iter(values)
    return lambda: next(it)


def test_empty_results_returns_empty_report():
    report = stamp_results([])
    assert report.entries == []
    assert report.earliest() is None
    assert report.latest() is None
    assert report.span() is None


def test_single_result_stamped():
    r = _r()
    report = stamp_results([r], clock=lambda: 1000.0, label="run-1")
    assert len(report.entries) == 1
    entry = report.entries[0]
    assert entry.epoch == 1000.0
    assert entry.label == "run-1"
    assert entry.result is r


def test_multiple_results_ordered_by_clock():
    results = [_r("a"), _r("b"), _r("c")]
    clock = _fixed_clock([10.0, 20.0, 30.0])
    report = stamp_results(results, clock=clock)
    epochs = [e.epoch for e in report.entries]
    assert epochs == [10.0, 20.0, 30.0]


def test_earliest_and_latest():
    results = [_r("a"), _r("b"), _r("c")]
    clock = _fixed_clock([5.0, 1.0, 9.0])
    report = stamp_results(results, clock=clock)
    assert report.earliest().epoch == 1.0
    assert report.latest().epoch == 9.0


def test_span_calculated_correctly():
    results = [_r("a"), _r("b")]
    clock = _fixed_clock([100.0, 105.5])
    report = stamp_results(results, clock=clock)
    assert report.span() == pytest.approx(5.5)


def test_span_single_entry_is_none():
    report = stamp_results([_r()], clock=lambda: 42.0)
    assert report.span() is None


def test_offsets_applied_to_clock():
    results = [_r("a"), _r("b")]
    report = stamp_results(results, clock=lambda: 100.0, offsets=[0.0, 2.5])
    assert report.entries[0].epoch == pytest.approx(100.0)
    assert report.entries[1].epoch == pytest.approx(102.5)


def test_offsets_wrong_length_raises():
    with pytest.raises(ValueError, match="offsets length"):
        stamp_results([_r(), _r()], offsets=[1.0])


def test_to_dict_structure():
    r = _r("job-x", success=False, duration=3.14)
    entry = StampedResult(result=r, epoch=999.123456, label="test")
    d = entry.to_dict()
    assert d["job_id"] == "job-x"
    assert d["success"] is False
    assert d["duration"] == pytest.approx(3.14)
    assert d["epoch"] == pytest.approx(999.123456)
    assert d["label"] == "test"


def test_report_to_dict_contains_entries():
    results = [_r("a"), _r("b")]
    clock = _fixed_clock([1.0, 2.0])
    report = stamp_results(results, clock=clock)
    d = report.to_dict()
    assert "entries" in d
    assert len(d["entries"]) == 2
    assert d["entries"][0]["job_id"] == "a"
