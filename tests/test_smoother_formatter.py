"""Tests for batchmark.smoother_formatter."""
from __future__ import annotations

import json

from batchmark.timer import TimingResult
from batchmark.smoother import smooth_results
from batchmark.smoother_formatter import format_smoother, format_smoother_text, format_smoother_json


def _r(job_id: str, duration: float | None) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=True)


def test_text_empty():
    out = format_smoother_text([])
    assert "No smoothed" in out


def test_text_contains_job_id():
    reports = smooth_results([_r("myjob", 1.0)], window=1)
    out = format_smoother_text(reports)
    assert "myjob" in out


def test_text_shows_window():
    reports = smooth_results([_r("j", 2.0)], window=5)
    out = format_smoother_text(reports)
    assert "window=5" in out


def test_text_shows_raw_and_smoothed():
    reports = smooth_results([_r("j", 1.0), _r("j", 3.0)], window=2)
    out = format_smoother_text(reports)
    assert "1.0000" in out
    assert "2.0000" in out  # smoothed for second point


def test_json_output_is_valid():
    reports = smooth_results([_r("j", 1.0), _r("j", 2.0)], window=2)
    out = format_smoother_json(reports)
    data = json.loads(out)
    assert isinstance(data, list)
    assert data[0]["job_id"] == "j"


def test_format_dispatch_json():
    reports = smooth_results([_r("j", 1.0)], window=1)
    out = format_smoother(reports, fmt="json")
    json.loads(out)  # should not raise


def test_format_dispatch_text():
    reports = smooth_results([_r("j", 1.0)], window=1)
    out = format_smoother(reports, fmt="text")
    assert "j" in out
