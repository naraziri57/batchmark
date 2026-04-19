"""Tests for batchmark.trend module."""
import pytest
from batchmark.timer import TimingResult
from batchmark.trend import analyze_trend, TrendPoint, TrendReport


def _r(job_id: str, duration: float, success: bool = True) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success, error=None)


def test_empty_runs_returns_empty_report():
    report = analyze_trend([])
    assert report.points == []
    assert report.is_improving() is False
    assert report.slope() is None


def test_single_run_no_slope():
    run = [_r("a", 1.0), _r("b", 2.0)]
    report = analyze_trend([run])
    assert len(report.points) == 1
    assert report.slope() is None
    assert report.is_improving() is False


def test_two_runs_improving():
    run1 = [_r("a", 2.0), _r("b", 2.0)]
    run2 = [_r("a", 1.0), _r("b", 1.0)]
    report = analyze_trend([run1, run2])
    assert report.is_improving() is True
    assert report.slope() < 0


def test_two_runs_regressing():
    run1 = [_r("a", 1.0)]
    run2 = [_r("a", 3.0)]
    report = analyze_trend([run1, run2])
    assert report.is_improving() is False
    assert report.slope() > 0


def test_success_rate_calculation():
    run = [_r("a", 1.0, True), _r("b", 2.0, False), _r("c", 1.5, True)]
    report = analyze_trend([run])
    assert report.points[0].success_rate == pytest.approx(2 / 3)


def test_none_duration_excluded_from_avg():
    r1 = TimingResult(job_id="a", duration=None, success=False, error="err")
    r2 = _r("b", 4.0)
    report = analyze_trend([[r1, r2]])
    assert report.points[0].avg_duration == pytest.approx(4.0)


def test_to_dict_structure():
    run1 = [_r("a", 1.0)]
    run2 = [_r("a", 0.5)]
    report = analyze_trend([run1, run2])
    d = report.to_dict()
    assert "points" in d
    assert "is_improving" in d
    assert "slope" in d
    assert d["is_improving"] is True
    assert len(d["points"]) == 2


def test_empty_run_skipped():
    run1 = [_r("a", 1.0)]
    run2 = []
    run3 = [_r("a", 0.8)]
    report = analyze_trend([run1, run2, run3])
    assert len(report.points) == 2
    assert report.points[0].run_index == 0
    assert report.points[1].run_index == 2
