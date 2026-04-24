"""Tests for batchmark.trimmer."""
from __future__ import annotations
import pytest
from batchmark.timer import TimingResult
from batchmark.trimmer import trim_results, TrimReport


def _r(job_id: str, duration: float | None, success: bool = True) -> TimingResult:
    return TimingResult(job_id=job_id, duration_seconds=duration, success=success)


def test_empty_returns_empty_report():
    report = trim_results([])
    assert report.kept_count == 0
    assert report.dropped_count == 0


def test_no_trim_keeps_all():
    results = [_r("a", 1.0), _r("b", 2.0), _r("c", 3.0)]
    report = trim_results(results, lower_pct=0, upper_pct=0)
    assert report.kept_count == 3
    assert report.dropped_count == 0


def test_trim_top_10_percent():
    results = [_r(str(i), float(i)) for i in range(10)]
    report = trim_results(results, upper_pct=10)
    assert report.dropped_high_count == 1
    assert report.dropped_high[0].job_id == "9"
    assert report.kept_count == 9


def test_trim_bottom_10_percent():
    results = [_r(str(i), float(i)) for i in range(10)]
    report = trim_results(results, lower_pct=10)
    assert report.dropped_low_count == 1
    assert report.dropped_low[0].job_id == "0"
    assert report.kept_count == 9


def test_trim_both_ends():
    results = [_r(str(i), float(i)) for i in range(10)]
    report = trim_results(results, lower_pct=10, upper_pct=10)
    assert report.dropped_low_count == 1
    assert report.dropped_high_count == 1
    assert report.kept_count == 8


def test_none_duration_always_kept():
    results = [_r("a", None), _r("b", 5.0), _r("c", 10.0)]
    report = trim_results(results, upper_pct=50)
    kept_ids = {r.job_id for r in report.kept}
    assert "a" in kept_ids


def test_all_none_duration_returns_all_kept():
    results = [_r("a", None), _r("b", None)]
    report = trim_results(results, lower_pct=20, upper_pct=20)
    assert report.kept_count == 2
    assert report.dropped_count == 0


def test_negative_pct_raises():
    with pytest.raises(ValueError, match="non-negative"):
        trim_results([_r("a", 1.0)], lower_pct=-5)


def test_combined_pct_100_raises():
    with pytest.raises(ValueError, match="less than 100"):
        trim_results([_r("a", 1.0)], lower_pct=50, upper_pct=50)


def test_to_dict_structure():
    results = [_r(str(i), float(i)) for i in range(10)]
    report = trim_results(results, lower_pct=10, upper_pct=10)
    d = report.to_dict()
    assert "kept_count" in d
    assert "dropped_count" in d
    assert "dropped_low" in d
    assert "dropped_high" in d
    assert d["dropped_count"] == d["dropped_low"] + d["dropped_high"]
