"""Tests for batchmark.shrinker."""
import pytest
from batchmark.timer import TimingResult
from batchmark.shrinker import shrink_results, ShrinkReport


def _r(job_id: str, duration: float = 1.0, success: bool = True) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success, error=None)


def test_empty_returns_empty_report():
    report = shrink_results([], max_per_job=2)
    assert report.kept_count == 0
    assert report.dropped_count == 0
    assert report.per_job_dropped == {}


def test_none_max_keeps_all():
    results = [_r("a"), _r("a"), _r("a")]
    report = shrink_results(results, max_per_job=None)
    assert report.kept_count == 3
    assert report.dropped_count == 0


def test_no_overflow_keeps_all():
    results = [_r("a", 1.0), _r("b", 2.0)]
    report = shrink_results(results, max_per_job=5)
    assert report.kept_count == 2
    assert report.dropped_count == 0


def test_latest_keeps_last_n():
    results = [_r("a", 1.0), _r("a", 2.0), _r("a", 3.0)]
    report = shrink_results(results, max_per_job=2, keep="latest")
    assert report.kept_count == 2
    assert report.dropped_count == 1
    kept_durations = sorted(r.duration for r in report.kept)
    assert kept_durations == [2.0, 3.0]


def test_earliest_keeps_first_n():
    results = [_r("a", 1.0), _r("a", 2.0), _r("a", 3.0)]
    report = shrink_results(results, max_per_job=2, keep="earliest")
    assert report.kept_count == 2
    kept_durations = sorted(r.duration for r in report.kept)
    assert kept_durations == [1.0, 2.0]


def test_per_job_dropped_populated():
    results = [_r("x", 1.0), _r("x", 2.0), _r("x", 3.0), _r("y", 9.0)]
    report = shrink_results(results, max_per_job=1)
    assert report.per_job_dropped.get("x") == 2
    assert "y" not in report.per_job_dropped


def test_multiple_jobs_shrunk_independently():
    results = [_r("a", 1.0), _r("a", 2.0), _r("b", 5.0), _r("b", 6.0), _r("b", 7.0)]
    report = shrink_results(results, max_per_job=1, keep="latest")
    assert report.kept_count == 2
    assert report.dropped_count == 3
    assert report.per_job_dropped["a"] == 1
    assert report.per_job_dropped["b"] == 2


def test_to_dict_structure():
    results = [_r("a"), _r("a"), _r("a")]
    report = shrink_results(results, max_per_job=2)
    d = report.to_dict()
    assert d["total"] == 3
    assert d["kept"] == 2
    assert d["dropped"] == 1
    assert "per_job_dropped" in d


def test_invalid_keep_raises():
    with pytest.raises(ValueError, match="keep must be"):
        shrink_results([_r("a")], max_per_job=1, keep="random")


def test_max_per_job_zero_drops_all():
    results = [_r("a"), _r("b")]
    report = shrink_results(results, max_per_job=0)
    assert report.kept_count == 0
    assert report.dropped_count == 2
