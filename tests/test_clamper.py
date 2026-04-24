"""Tests for batchmark/clamper.py"""
import pytest
from batchmark.timer import TimingResult
from batchmark.clamper import clamp_results, ClampReport


def _r(job_id: str, duration, success: bool = True) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success, error=None)


def test_empty_returns_empty_report():
    report = clamp_results([])
    assert report.total == 0
    assert report.clamped_count == 0


def test_no_clamp_bounds_leaves_durations_unchanged():
    results = [_r("a", 1.0), _r("b", 5.0)]
    report = clamp_results(results)
    assert report.clamped_count == 0
    assert report.entries[0].result.duration == 1.0
    assert report.entries[1].result.duration == 5.0


def test_max_clamps_high_duration():
    results = [_r("a", 10.0), _r("b", 2.0)]
    report = clamp_results(results, max_duration=5.0)
    assert report.entries[0].result.duration == 5.0
    assert report.entries[0].clamped is True
    assert report.entries[0].original_duration == 10.0
    assert report.entries[1].result.duration == 2.0
    assert report.entries[1].clamped is False


def test_min_clamps_low_duration():
    results = [_r("a", 0.1), _r("b", 3.0)]
    report = clamp_results(results, min_duration=1.0)
    assert report.entries[0].result.duration == 1.0
    assert report.entries[0].clamped is True
    assert report.entries[1].result.duration == 3.0
    assert report.entries[1].clamped is False


def test_both_bounds_clamp_both_ends():
    results = [_r("low", 0.5), _r("mid", 3.0), _r("high", 9.0)]
    report = clamp_results(results, min_duration=1.0, max_duration=7.0)
    durations = [e.result.duration for e in report.entries]
    assert durations == [1.0, 3.0, 7.0]
    assert report.clamped_count == 2


def test_none_duration_not_clamped():
    results = [_r("a", None, success=False)]
    report = clamp_results(results, min_duration=1.0, max_duration=5.0)
    assert report.entries[0].result.duration is None
    assert report.entries[0].clamped is False
    assert report.entries[0].original_duration is None


def test_duration_exactly_at_bound_not_flagged():
    results = [_r("a", 5.0)]
    report = clamp_results(results, min_duration=1.0, max_duration=5.0)
    assert report.entries[0].clamped is False
    assert report.entries[0].result.duration == 5.0


def test_invalid_bounds_raises():
    with pytest.raises(ValueError):
        clamp_results([_r("a", 1.0)], min_duration=10.0, max_duration=5.0)


def test_to_dict_structure():
    results = [_r("a", 8.0)]
    report = clamp_results(results, max_duration=5.0)
    d = report.to_dict()
    assert d["total"] == 1
    assert d["clamped_count"] == 1
    assert len(d["entries"]) == 1
    entry = d["entries"][0]
    assert entry["clamped"] is True
    assert entry["original_duration"] == 8.0
    assert entry["duration"] == 5.0


def test_success_flag_preserved():
    results = [_r("a", 1.0, success=False)]
    report = clamp_results(results, min_duration=2.0)
    assert report.entries[0].result.success is False
