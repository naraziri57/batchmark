"""Tests for batchmark.zipper_formatter."""
import json
from batchmark.timer import TimingResult
from batchmark.zipper import zip_results
from batchmark.zipper_formatter import format_zip, format_zip_text, format_zip_json


def _r(job_id: str, duration: float | None = 1.0, success: bool = True) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success)


def test_text_empty():
    report = zip_results([], [])
    out = format_zip_text(report)
    assert "No pairs" in out


def test_text_contains_job_id():
    report = zip_results([_r("job-a", 1.0)], [_r("job-a", 0.8)])
    out = format_zip_text(report)
    assert "job-a" in out


def test_text_shows_delta_down_arrow():
    report = zip_results([_r("job-a", 2.0)], [_r("job-a", 1.0)])
    out = format_zip_text(report)
    assert "▼" in out


def test_text_shows_delta_up_arrow():
    report = zip_results([_r("job-a", 1.0)], [_r("job-a", 2.0)])
    out = format_zip_text(report)
    assert "▲" in out


def test_text_shows_summary_line():
    report = zip_results([_r("job-a"), _r("job-b")], [_r("job-a")])
    out = format_zip_text(report)
    assert "Matched: 1" in out
    assert "Left only: 1" in out


def test_json_output_is_valid():
    report = zip_results([_r("job-a", 1.5)], [_r("job-a", 1.2)])
    out = format_zip_json(report)
    data = json.loads(out)
    assert "pairs" in data
    assert data["matched_count"] == 1


def test_format_zip_defaults_to_text():
    report = zip_results([_r("j", 1.0)], [_r("j", 0.9)])
    assert format_zip(report) == format_zip_text(report)


def test_format_zip_json_mode():
    report = zip_results([_r("j", 1.0)], [_r("j", 0.9)])
    out = format_zip(report, fmt="json")
    json.loads(out)  # should not raise
