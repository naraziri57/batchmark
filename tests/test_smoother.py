"""Tests for batchmark.smoother."""
from __future__ import annotations

import pytest

from batchmark.timer import TimingResult
from batchmark.smoother import smooth_results, SmoothedPoint, SmoothedReport


def _r(job_id: str, duration: float | None, success: bool = True) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success)


def test_empty_returns_empty():
    assert smooth_results([]) == []


def test_single_result_smoothed_equals_raw():
    results = [_r("job1", 2.0)]
    reports = smooth_results(results, window=3)
    assert len(reports) == 1
    assert reports[0].job_id == "job1"
    assert len(reports[0].points) == 1
    p = reports[0].points[0]
    assert p.raw_duration == 2.0
    assert p.smoothed_duration == pytest.approx(2.0)


def test_window_averages_correctly():
    results = [_r("j", 1.0), _r("j", 3.0), _r("j", 5.0)]
    reports = smooth_results(results, window=3)
    points = reports[0].points
    assert points[0].smoothed_duration == pytest.approx(1.0)
    assert points[1].smoothed_duration == pytest.approx(2.0)
    assert points[2].smoothed_duration == pytest.approx(3.0)


def test_window_of_one_equals_raw():
    results = [_r("j", 1.0), _r("j", 4.0), _r("j", 9.0)]
    reports = smooth_results(results, window=1)
    for p in reports[0].points:
        assert p.smoothed_duration == pytest.approx(p.raw_duration)


def test_none_duration_excluded_from_average():
    results = [_r("j", 2.0), _r("j", None), _r("j", 4.0)]
    reports = smooth_results(results, window=3)
    points = reports[0].points
    # index 1: only index 0 has a value -> avg = 2.0
    assert points[1].smoothed_duration == pytest.approx(2.0)
    # index 2: values at 0 and 2 -> avg = 3.0
    assert points[2].smoothed_duration == pytest.approx(3.0)


def test_all_none_duration_gives_none_smoothed():
    results = [_r("j", None), _r("j", None)]
    reports = smooth_results(results, window=2)
    for p in reports[0].points:
        assert p.smoothed_duration is None


def test_multiple_jobs_produce_separate_reports():
    results = [_r("a", 1.0), _r("b", 2.0), _r("a", 3.0)]
    reports = smooth_results(results, window=2)
    job_ids = [r.job_id for r in reports]
    assert "a" in job_ids
    assert "b" in job_ids


def test_invalid_window_raises():
    with pytest.raises(ValueError):
        smooth_results([_r("j", 1.0)], window=0)


def test_to_dict_keys():
    results = [_r("j", 1.5)]
    report = smooth_results(results, window=1)[0]
    d = report.to_dict()
    assert "job_id" in d
    assert "window" in d
    assert "points" in d
    assert "raw_duration" in d["points"][0]
    assert "smoothed_duration" in d["points"][0]
