"""Tests for batchmark.pivotter_formatter."""
from __future__ import annotations
import json
from batchmark.timer import TimingResult
from batchmark.pivotter import pivot_results
from batchmark.pivotter_formatter import format_pivot, format_pivot_text, format_pivot_json


def _r(job_id: str, env: str, duration: float = 1.0, success: bool = True) -> TimingResult:
    r = TimingResult(job_id=job_id, success=success)
    r.duration = duration
    r.env = env
    return r


def _key(x):
    return getattr(x, "env", None)


def test_text_empty():
    from batchmark.pivotter import PivotReport
    report = PivotReport(pivot_key="env", pivot_values=[], job_ids=[], cells={})
    out = format_pivot_text(report)
    assert "No pivot data" in out


def test_text_contains_job_id():
    r = _r("job-a", "prod", duration=1.0)
    report = pivot_results([r], key_fn=_key, pivot_key="env")
    out = format_pivot_text(report)
    assert "job-a" in out


def test_text_contains_pivot_value():
    r = _r("job-a", "staging", duration=2.5)
    report = pivot_results([r], key_fn=_key, pivot_key="env")
    out = format_pivot_text(report)
    assert "staging" in out


def test_text_shows_avg_duration():
    r = _r("job-b", "dev", duration=3.0)
    report = pivot_results([r], key_fn=_key, pivot_key="env")
    out = format_pivot_text(report)
    assert "3.000s" in out


def test_text_missing_cell_shows_dash():
    r1 = _r("job-a", "prod", duration=1.0)
    r2 = _r("job-b", "dev", duration=2.0)
    report = pivot_results([r1, r2], key_fn=_key, pivot_key="env")
    out = format_pivot_text(report)
    assert "—" in out


def test_json_output_is_valid():
    r = _r("job-c", "qa", duration=0.5)
    report = pivot_results([r], key_fn=_key, pivot_key="env")
    out = format_pivot_json(report)
    parsed = json.loads(out)
    assert parsed["pivot_key"] == "env"
    assert "job-c" in parsed["job_ids"]


def test_format_dispatch_json():
    r = _r("job-d", "prod", duration=1.0)
    report = pivot_results([r], key_fn=_key, pivot_key="env")
    out = format_pivot(report, fmt="json")
    parsed = json.loads(out)
    assert "cells" in parsed


def test_format_dispatch_text_default():
    r = _r("job-e", "prod", duration=1.0)
    report = pivot_results([r], key_fn=_key, pivot_key="env")
    out = format_pivot(report)
    assert "job-e" in out
