"""Tests for batchmark.classifier_formatter."""
from __future__ import annotations

import json
import csv
import io

from batchmark.classifier import classify_results
from batchmark.classifier_formatter import (
    format_classifier,
    format_classifier_csv,
    format_classifier_json,
    format_classifier_text,
)
from batchmark.timer import TimingResult


def _r(job_id: str, success: bool = True, duration: float | None = 1.0) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success)


def _report(results=None, classifiers=None):
    results = results or []
    classifiers = classifiers or []
    return classify_results(results, classifiers)


def test_text_empty():
    out = format_classifier_text(_report())
    assert "No classified" in out


def test_text_contains_job_id():
    r = _report([_r("job-alpha")], [])
    out = format_classifier_text(r)
    assert "job-alpha" in out


def test_text_shows_category():
    classifiers = [("fast", lambda r: True)]
    r = _report([_r("job-1")], classifiers)
    out = format_classifier_text(r)
    assert "fast" in out


def test_text_shows_ok_status():
    r = _report([_r("job-ok", success=True)], [])
    out = format_classifier_text(r)
    assert "OK" in out


def test_text_shows_fail_status():
    r = _report([_r("job-fail", success=False)], [])
    out = format_classifier_text(r)
    assert "FAIL" in out


def test_json_output_is_valid():
    r = _report([_r("job-j")], [])
    out = format_classifier_json(r)
    data = json.loads(out)
    assert "classified" in data
    assert "category_counts" in data


def test_csv_has_header_and_row():
    r = _report([_r("job-c")], [])
    out = format_classifier_csv(r)
    reader = csv.DictReader(io.StringIO(out))
    rows = list(reader)
    assert len(rows) == 1
    assert rows[0]["job_id"] == "job-c"
    assert "category" in rows[0]


def test_format_dispatcher_json():
    r = _report([_r("job-d")], [])
    out = format_classifier(r, fmt="json")
    assert out.startswith("{")


def test_format_dispatcher_csv():
    r = _report([_r("job-e")], [])
    out = format_classifier(r, fmt="csv")
    assert "job_id" in out
