"""Tests for batchmark.roller and batchmark.roller_formatter."""
import json
import pytest

from batchmark.timer import TimingResult
from batchmark.roller import rolling_stats, RollingReport
from batchmark.roller_formatter import format_roller, format_roller_text, format_roller_json


def _r(job_id: str, duration):
    return TimingResult(job_id=job_id, duration=duration, success=True, error=None)


def test_empty_returns_empty_report():
    report = rolling_stats([], window=3)
    assert report.points == []
    assert report.window == 3


def test_single_result_rolling_equals_raw():
    r = _r("job-1", 1.0)
    report = rolling_stats([r], window=3)
    assert len(report.points) == 1
    p = report.points[0]
    assert p.rolling_avg == pytest.approx(1.0)
    assert p.rolling_min == pytest.approx(1.0)
    assert p.rolling_max == pytest.approx(1.0)
    assert p.window_size == 1


def test_window_averages_correctly():
    results = [_r(f"job-{i}", float(i + 1)) for i in range(5)]
    report = rolling_stats(results, window=3)
    # index 2: window covers indices 0,1,2 -> durations 1,2,3
    p = report.points[2]
    assert p.rolling_avg == pytest.approx(2.0)
    assert p.rolling_min == pytest.approx(1.0)
    assert p.rolling_max == pytest.approx(3.0)
    assert p.window_size == 3


def test_window_slides_correctly():
    results = [_r(f"job-{i}", float(i + 1)) for i in range(5)]
    report = rolling_stats(results, window=3)
    # index 4: window covers indices 2,3,4 -> durations 3,4,5
    p = report.points[4]
    assert p.rolling_avg == pytest.approx(4.0)
    assert p.rolling_min == pytest.approx(3.0)
    assert p.rolling_max == pytest.approx(5.0)


def test_none_duration_excluded_from_stats():
    results = [_r("a", 2.0), _r("b", None), _r("c", 4.0)]
    report = rolling_stats(results, window=3)
    p = report.points[2]
    # only 2.0 and 4.0 contribute
    assert p.rolling_avg == pytest.approx(3.0)
    assert p.rolling_min == pytest.approx(2.0)
    assert p.rolling_max == pytest.approx(4.0)


def test_all_none_durations_gives_none_stats():
    results = [_r("a", None), _r("b", None)]
    report = rolling_stats(results, window=2)
    for p in report.points:
        assert p.rolling_avg is None
        assert p.rolling_min is None
        assert p.rolling_max is None


def test_invalid_window_raises():
    with pytest.raises(ValueError):
        rolling_stats([_r("x", 1.0)], window=0)


def test_to_dict_structure():
    results = [_r("job-1", 1.5)]
    report = rolling_stats(results, window=1)
    d = report.to_dict()
    assert "window" in d
    assert "points" in d
    assert d["points"][0]["job_id"] == "job-1"


def test_format_text_empty():
    report = rolling_stats([], window=3)
    out = format_roller_text(report)
    assert "No data" in out


def test_format_text_contains_job_id():
    results = [_r("job-42", 0.5)]
    report = rolling_stats(results, window=1)
    out = format_roller_text(report)
    assert "job-42" in out


def test_format_json_is_valid():
    results = [_r("job-1", 1.0), _r("job-2", 2.0)]
    report = rolling_stats(results, window=2)
    out = format_roller_json(report)
    data = json.loads(out)
    assert data["window"] == 2
    assert len(data["points"]) == 2


def test_format_dispatch():
    results = [_r("j", 1.0)]
    report = rolling_stats(results, window=1)
    assert format_roller(report, fmt="text") == format_roller_text(report)
    assert format_roller(report, fmt="json") == format_roller_json(report)
