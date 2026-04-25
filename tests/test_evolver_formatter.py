"""Tests for batchmark.evolver_formatter."""
import json
from batchmark.timer import TimingResult
from batchmark.evolver import evolve
from batchmark.evolver_formatter import format_evolver, format_evolver_text, format_evolver_json


def _r(job_id: str, duration: float | None, success: bool = True) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success)


def test_text_empty():
    report = evolve({})
    out = format_evolver_text(report)
    assert "no evolution data" in out


def test_text_contains_job_id():
    report = evolve({"v1": [_r("job-a", 1.0)]})
    out = format_evolver_text(report)
    assert "job-a" in out


def test_text_contains_run_labels():
    report = evolve({"v1": [_r("job-a", 1.0)], "v2": [_r("job-a", 0.9)]})
    out = format_evolver_text(report)
    assert "v1" in out
    assert "v2" in out


def test_text_shows_net_change_negative():
    report = evolve({"v1": [_r("job-a", 1.0)], "v2": [_r("job-a", 0.5)]})
    out = format_evolver_text(report)
    assert "-" in out


def test_text_shows_net_change_positive():
    report = evolve({"v1": [_r("job-a", 0.5)], "v2": [_r("job-a", 1.0)]})
    out = format_evolver_text(report)
    assert "+" in out


def test_text_shows_na_for_missing():
    report = evolve({"v1": [_r("job-a", 1.0)], "v2": []})
    out = format_evolver_text(report)
    assert "n/a" in out


def test_json_output_is_valid():
    report = evolve({"v1": [_r("job-a", 1.0)], "v2": [_r("job-a", 0.8)]})
    out = format_evolver_json(report)
    parsed = json.loads(out)
    assert "run_labels" in parsed
    assert "jobs" in parsed


def test_format_dispatches_json():
    report = evolve({"v1": [_r("job-a", 1.0)]})
    out = format_evolver(report, fmt="json")
    parsed = json.loads(out)
    assert isinstance(parsed, dict)


def test_format_dispatches_text_default():
    report = evolve({"v1": [_r("job-a", 1.0)]})
    out = format_evolver(report)
    assert "job-a" in out
