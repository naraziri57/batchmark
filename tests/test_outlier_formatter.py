"""Tests for outlier formatter."""
import json
import pytest
from batchmark.timer import TimingResult
from batchmark.outlier import detect_outliers
from batchmark.outlier_formatter import format_outlier, format_outlier_text, format_outlier_json


def _r(job_id: str, duration: float) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=True)


def test_text_empty():
    report = detect_outliers([])
    out = format_outlier_text(report)
    assert "No results" in out


def test_text_contains_job_id():
    report = detect_outliers([_r("myjob", 1.5), _r("other", 1.6)])
    out = format_outlier_text(report)
    assert "myjob" in out
    assert "other" in out


def test_text_flags_outlier():
    results = [_r("a", 1.0), _r("b", 1.0), _r("c", 1.0), _r("spike", 100.0)]
    report = detect_outliers(results, threshold=1.5)
    out = format_outlier_text(report)
    assert "[OUTLIER]" in out


def test_json_is_valid():
    report = detect_outliers([_r("a", 1.0), _r("b", 2.0)])
    out = format_outlier_json(report)
    data = json.loads(out)
    assert "mean" in data
    assert "results" in data


def test_format_dispatch_json():
    report = detect_outliers([_r("a", 1.0), _r("b", 1.0)])
    out = format_outlier(report, fmt="json")
    data = json.loads(out)
    assert isinstance(data, dict)


def test_format_dispatch_text_default():
    report = detect_outliers([_r("a", 1.0), _r("b", 1.0)])
    out = format_outlier(report)
    assert isinstance(out, str)
    assert "Outlier Detection" in out
