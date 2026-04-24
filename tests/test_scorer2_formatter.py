"""Tests for batchmark.scorer2_formatter."""
import json
from batchmark.timer import TimingResult
from batchmark.scorer2 import weighted_score
from batchmark.scorer2_formatter import (
    format_weighted_score_text,
    format_weighted_score_json,
    format_weighted_score,
)


def _r(job_id, duration=None, success=True):
    return TimingResult(job_id=job_id, duration=duration, success=success)


def test_text_empty():
    report = weighted_score([])
    out = format_weighted_score_text(report)
    assert "No weighted scores" in out


def test_text_contains_job_id():
    report = weighted_score([_r("my-job", duration=1.5)])
    out = format_weighted_score_text(report)
    assert "my-job" in out


def test_text_contains_overall():
    report = weighted_score([_r("a", duration=1.0), _r("b", duration=2.0)])
    out = format_weighted_score_text(report)
    assert "Overall average" in out


def test_json_output_is_valid():
    report = weighted_score([_r("j1", duration=3.0), _r("j2", duration=1.0)])
    out = format_weighted_score_json(report)
    parsed = json.loads(out)
    assert "scores" in parsed
    assert "overall" in parsed


def test_format_dispatch_text():
    report = weighted_score([_r("x", duration=1.0)])
    out = format_weighted_score(report, fmt="text")
    assert "Weighted Scoring" in out


def test_format_dispatch_json():
    report = weighted_score([_r("x", duration=1.0)])
    out = format_weighted_score(report, fmt="json")
    parsed = json.loads(out)
    assert isinstance(parsed, dict)
