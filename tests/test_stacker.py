"""Tests for batchmark/stacker.py"""
import json
import pytest
from batchmark.timer import TimingResult
from batchmark.stacker import (
    StackedRun,
    StackReport,
    stack_runs,
    format_stack_text,
    format_stack_json,
    format_stack,
)


def _r(job_id: str, duration=None, success=True) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success)


def test_empty_stack_returns_empty_report():
    report = stack_runs([])
    assert report.runs == []
    assert report.labels() == []


def test_single_run_label():
    results = [_r("job1", 1.0), _r("job2", 2.0)]
    report = stack_runs([("run-a", results)])
    assert report.labels() == ["run-a"]


def test_avg_duration_calculated():
    results = [_r("j1", 2.0), _r("j2", 4.0)]
    report = stack_runs([("r1", results)])
    assert report.runs[0].avg_duration == pytest.approx(3.0)


def test_avg_duration_none_when_no_durations():
    results = [_r("j1", None), _r("j2", None)]
    report = stack_runs([("r1", results)])
    assert report.runs[0].avg_duration is None


def test_success_count():
    results = [_r("j1", 1.0, success=True), _r("j2", 2.0, success=False), _r("j3", 3.0, success=True)]
    report = stack_runs([("r1", results)])
    assert report.runs[0].success_count == 2


def test_by_label_found():
    results = [_r("j1", 1.0)]
    report = stack_runs([("alpha", results)])
    run = report.by_label("alpha")
    assert run is not None
    assert run.label == "alpha"


def test_by_label_missing_returns_none():
    report = stack_runs([])
    assert report.by_label("ghost") is None


def test_avg_durations_dict():
    r1 = [_r("j1", 1.0)]
    r2 = [_r("j2", 3.0)]
    report = stack_runs([("a", r1), ("b", r2)])
    avgs = report.avg_durations()
    assert avgs["a"] == pytest.approx(1.0)
    assert avgs["b"] == pytest.approx(3.0)


def test_to_dict_structure():
    results = [_r("j1", 2.0)]
    report = stack_runs([("run1", results)])
    d = report.to_dict()
    assert "runs" in d
    assert d["runs"][0]["label"] == "run1"
    assert d["runs"][0]["count"] == 1


def test_format_text_empty():
    report = stack_runs([])
    out = format_stack_text(report)
    assert "No stacked runs" in out


def test_format_text_contains_label():
    results = [_r("j1", 1.5)]
    report = stack_runs([("batch-1", results)])
    out = format_stack_text(report)
    assert "batch-1" in out
    assert "avg=" in out


def test_format_json_is_valid():
    results = [_r("j1", 1.0), _r("j2", 2.0, success=False)]
    report = stack_runs([("v1", results)])
    out = format_stack_json(report)
    parsed = json.loads(out)
    assert "runs" in parsed
    assert parsed["runs"][0]["label"] == "v1"


def test_format_dispatch_json():
    report = stack_runs([("x", [_r("j1", 1.0)])])
    out = format_stack(report, fmt="json")
    parsed = json.loads(out)
    assert "runs" in parsed


def test_format_dispatch_text_default():
    report = stack_runs([("x", [_r("j1", 1.0)])])
    out = format_stack(report)
    assert "Stacked Runs" in out
