"""Tests for batchmark.merger_formatter."""
from __future__ import annotations

import json

from batchmark.timer import TimingResult
from batchmark.merger import merge
from batchmark.merger_formatter import format_merge, format_merge_text, format_merge_json


def _r(job_id: str, success: bool = True, duration: float | None = 1.0) -> TimingResult:
    return TimingResult(
        job_id=job_id,
        success=success,
        duration=duration,
        error=None if success else "err",
    )


def _report(runs=None, labels=None, on_conflict="keep_all"):
    runs = runs or [[_r("job_a")]]
    return merge(runs, labels=labels, on_conflict=on_conflict)


def test_text_empty():
    report = merge([])
    text = format_merge_text(report)
    assert "Merge Report" in text
    assert "Total    : 0" in text


def test_text_contains_source_labels():
    report = merge([[_r("a")], [_r("b")]], labels=["alpha", "beta"])
    text = format_merge_text(report)
    assert "alpha" in text
    assert "beta" in text


def test_text_shows_conflicts():
    run1 = [_r("job_x")]
    run2 = [_r("job_x")]
    report = merge([run1, run2], on_conflict="keep_all")
    text = format_merge_text(report)
    assert "job_x" in text
    assert "Conflicts: 1" in text


def test_json_is_valid():
    report = _report()
    raw = format_merge_json(report)
    data = json.loads(raw)
    assert "total" in data
    assert "results" in data
    assert isinstance(data["results"], list)


def test_json_results_have_expected_keys():
    report = _report([[_r("job_a", success=False, duration=3.5)]])
    data = json.loads(format_merge_json(report))
    result = data["results"][0]
    assert result["job_id"] == "job_a"
    assert result["success"] is False
    assert result["duration"] == 3.5


def test_format_dispatch_text():
    report = _report()
    assert format_merge(report, fmt="text") == format_merge_text(report)


def test_format_dispatch_json():
    report = _report()
    assert format_merge(report, fmt="json") == format_merge_json(report)
