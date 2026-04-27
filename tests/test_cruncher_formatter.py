"""tests for batchmark.cruncher_formatter"""
from __future__ import annotations

import json

import pytest

from batchmark.timer import TimingResult
from batchmark.cruncher import crunch, CrunchReport
from batchmark.cruncher_formatter import format_crunch_text, format_crunch_json, format_crunch


def _r(job_id: str, duration: float | None, success: bool = True) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success, error=None)


def _report(*results: TimingResult) -> CrunchReport:
    return crunch(list(results))


def test_text_empty_report():
    out = format_crunch_text(_report())
    assert out == "no data"


def test_text_contains_job_id():
    out = format_crunch_text(_report(_r("my-job", 1.0)))
    assert "my-job" in out


def test_text_shows_count():
    out = format_crunch_text(_report(_r("j", 1.0), _r("j", 2.0)))
    assert "2" in out


def test_text_shows_failure():
    out = format_crunch_text(_report(_r("j", 1.0, success=True), _r("j", 2.0, success=False)))
    assert "1" in out  # failure_count


def test_json_output_is_valid():
    out = format_crunch_json(_report(_r("j", 1.5)))
    data = json.loads(out)
    assert "jobs" in data
    assert data["jobs"][0]["job_id"] == "j"


def test_json_contains_percentiles():
    out = format_crunch_json(_report(_r("j", 1.0), _r("j", 2.0), _r("j", 3.0)))
    data = json.loads(out)
    assert "p50" in data["jobs"][0]
    assert "p95" in data["jobs"][0]


def test_format_defaults_to_text():
    report = _report(_r("j", 1.0))
    assert format_crunch(report) == format_crunch_text(report)


def test_format_json_mode():
    report = _report(_r("j", 1.0))
    out = format_crunch(report, fmt="json")
    json.loads(out)  # should not raise
