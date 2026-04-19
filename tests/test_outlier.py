"""Tests for outlier detection logic."""
import pytest
from batchmark.timer import TimingResult
from batchmark.outlier import detect_outliers, OutlierReport


def _r(job_id: str, duration: float, success: bool = True) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success)


def test_empty_returns_empty_report():
    report = detect_outliers([])
    assert report.results == []
    assert report.mean is None
    assert report.outliers == []


def test_single_result_no_stdev():
    report = detect_outliers([_r("job1", 1.0)])
    assert len(report.results) == 1
    assert report.stdev is None
    assert report.results[0].is_outlier is False


def test_no_outliers_when_uniform():
    results = [_r(f"job{i}", 1.0) for i in range(5)]
    report = detect_outliers(results)
    assert len(report.outliers) == 0


def test_detects_obvious_outlier():
    results = [
        _r("a", 1.0),
        _r("b", 1.1),
        _r("c", 1.05),
        _r("d", 1.02),
        _r("e", 50.0),  # obvious outlier
    ]
    report = detect_outliers(results, threshold=2.0)
    outlier_ids = [o.result.job_id for o in report.outliers]
    assert "e" in outlier_ids
    assert "a" not in outlier_ids


def test_threshold_respected():
    results = [_r("a", 1.0), _r("b", 3.0), _r("c", 1.0)]
    loose = detect_outliers(results, threshold=10.0)
    strict = detect_outliers(results, threshold=0.1)
    assert len(loose.outliers) == 0
    assert len(strict.outliers) > 0


def test_none_duration_gets_zero_z():
    r = TimingResult(job_id="x", duration=None, success=False)
    results = [_r("a", 1.0), _r("b", 1.0), r]
    report = detect_outliers(results)
    none_entry = next(e for e in report.results if e.result.job_id == "x")
    assert none_entry.z_score == 0.0
    assert none_entry.is_outlier is False


def test_to_dict_structure():
    results = [_r("a", 1.0), _r("b", 2.0)]
    report = detect_outliers(results)
    d = report.to_dict()
    assert "mean" in d
    assert "stdev" in d
    assert "outlier_count" in d
    assert isinstance(d["results"], list)
    assert "z_score" in d["results"][0]
