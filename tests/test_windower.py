"""Tests for batchmark.windower."""
import pytest
from batchmark.timer import TimingResult
from batchmark.windower import build_window_report, WindowReport


def _r(job_id: str, duration: float | None = 1.0, success: bool = True) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success, error=None)


def test_empty_returns_empty_report():
    report = build_window_report([], window_size=3, step=1)
    assert isinstance(report, WindowReport)
    assert report.windows == []


def test_single_result_one_window():
    results = [_r("j1", 2.0)]
    report = build_window_report(results, window_size=3, step=1)
    assert len(report.windows) == 1
    w = report.windows[0]
    assert w.count == 1
    assert w.success_count == 1
    assert w.failed_count == 0
    assert w.avg_duration == pytest.approx(2.0)


def test_window_size_equals_total():
    results = [_r(f"j{i}", float(i + 1)) for i in range(4)]
    report = build_window_report(results, window_size=4, step=1)
    assert len(report.windows) == 4
    assert report.windows[0].count == 4


def test_step_equals_window_no_overlap():
    results = [_r(f"j{i}", 1.0) for i in range(6)]
    report = build_window_report(results, window_size=3, step=3)
    assert len(report.windows) == 2
    assert report.windows[0].start_index == 0
    assert report.windows[1].start_index == 3


def test_avg_duration_computed_correctly():
    results = [_r("a", 2.0), _r("b", 4.0), _r("c", 6.0)]
    report = build_window_report(results, window_size=3, step=3)
    assert report.windows[0].avg_duration == pytest.approx(4.0)


def test_none_duration_excluded_from_avg():
    results = [_r("a", None), _r("b", 3.0), _r("c", None)]
    report = build_window_report(results, window_size=3, step=3)
    assert report.windows[0].avg_duration == pytest.approx(3.0)


def test_all_none_duration_avg_is_none():
    results = [_r("a", None), _r("b", None)]
    report = build_window_report(results, window_size=2, step=2)
    assert report.windows[0].avg_duration is None


def test_failed_jobs_counted():
    results = [_r("a", 1.0, success=True), _r("b", 2.0, success=False), _r("c", 3.0, success=False)]
    report = build_window_report(results, window_size=3, step=3)
    w = report.windows[0]
    assert w.success_count == 1
    assert w.failed_count == 2


def test_invalid_window_size_raises():
    with pytest.raises(ValueError, match="window_size"):
        build_window_report([], window_size=0)


def test_invalid_step_raises():
    with pytest.raises(ValueError, match="step"):
        build_window_report([], window_size=2, step=0)


def test_to_dict_structure():
    results = [_r("x", 1.0)]
    report = build_window_report(results, window_size=1, step=1)
    d = report.to_dict()
    assert d["window_size"] == 1
    assert d["step"] == 1
    assert isinstance(d["windows"], list)
    assert "avg_duration" in d["windows"][0]
