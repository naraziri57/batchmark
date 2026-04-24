"""Tests for batchmark.bucketer_formatter."""
from __future__ import annotations
import json
import pytest
from batchmark.timer import TimingResult
from batchmark.bucketer import bucket_results
from batchmark.bucketer_formatter import format_bucket_text, format_bucket_json, format_bucket


def _r(job_id: str, duration=None, success: bool = True) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success)


def test_text_empty_report():
    report = bucket_results([], [1.0])
    out = format_bucket_text(report)
    assert "Duration Buckets" in out
    assert "count=0" in out


def test_text_shows_bucket_label():
    results = [_r("a", 0.5)]
    report = bucket_results(results, [1.0])
    out = format_bucket_text(report)
    assert "<1.0" in out


def test_text_shows_avg_duration():
    results = [_r("a", 2.0), _r("b", 4.0)]
    report = bucket_results(results, [1.0])
    out = format_bucket_text(report)
    assert "avg=" in out


def test_json_output_is_valid():
    results = [_r("a", 0.5), _r("b", 3.0)]
    report = bucket_results(results, [1.0])
    out = format_bucket_json(report)
    parsed = json.loads(out)
    assert "buckets" in parsed
    assert isinstance(parsed["buckets"], list)


def test_json_contains_count():
    results = [_r("x", 2.0)]
    report = bucket_results(results, [1.0])
    parsed = json.loads(format_bucket_json(report))
    counts = [b["count"] for b in parsed["buckets"]]
    assert sum(counts) == 1


def test_format_dispatch_text():
    report = bucket_results([_r("a", 1.5)], [1.0])
    out = format_bucket(report, "text")
    assert "Duration Buckets" in out


def test_format_dispatch_json():
    report = bucket_results([_r("a", 1.5)], [1.0])
    out = format_bucket(report, "json")
    parsed = json.loads(out)
    assert "buckets" in parsed
