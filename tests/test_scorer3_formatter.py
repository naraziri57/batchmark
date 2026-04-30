"""Tests for batchmark.scorer3_formatter."""
import json
from batchmark.timer import TimingResult
from batchmark.scorer3 import score_composite
from batchmark.scorer3_formatter import format_composite, format_composite_text, format_composite_json


def _r(job_id, duration=None, success=True):
    return TimingResult(job_id=job_id, duration=duration, success=success)


def test_text_empty():
    report = score_composite([])
    out = format_composite_text(report)
    assert "No composite" in out


def test_text_contains_job_id():
    report = score_composite([_r("myjob", duration=1.0)])
    out = format_composite_text(report)
    assert "myjob" in out


def test_text_contains_overall():
    report = score_composite([_r("j", duration=1.0)])
    out = format_composite_text(report)
    assert "overall" in out.lower()


def test_json_output_is_valid():
    report = score_composite([_r("j", duration=2.0)])
    out = format_composite_json(report)
    data = json.loads(out)
    assert "scores" in data
    assert "overall" in data


def test_json_score_fields_present():
    report = score_composite([_r("j", duration=1.0)])
    data = json.loads(format_composite_json(report))
    score = data["scores"][0]
    for key in ("job_id", "duration_score", "success_score", "consistency_score", "composite"):
        assert key in score


def test_format_dispatches_text():
    report = score_composite([_r("j", duration=1.0)])
    assert format_composite(report, fmt="text") == format_composite_text(report)


def test_format_dispatches_json():
    report = score_composite([_r("j", duration=1.0)])
    assert format_composite(report, fmt="json") == format_composite_json(report)
