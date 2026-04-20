"""Tests for batchmark.flattener_formatter."""

from __future__ import annotations

import json

from batchmark.flattener import FlatRecord
from batchmark.flattener_formatter import (
    format_flat_text,
    format_flat_json,
    format_flat_csv,
    format_flat,
)


def _rec(job_id: str, duration: float | None = 1.0, success: bool = True, tags=None) -> FlatRecord:
    return FlatRecord(job_id=job_id, duration=duration, success=success, tags=tags or {})


def test_text_empty():
    out = format_flat_text([])
    assert "No records" in out


def test_text_contains_job_id():
    out = format_flat_text([_rec("job-alpha")])
    assert "job-alpha" in out


def test_text_shows_ok_status():
    out = format_flat_text([_rec("j", success=True)])
    assert "OK" in out


def test_text_shows_fail_status():
    out = format_flat_text([_rec("j", success=False)])
    assert "FAIL" in out


def test_text_shows_tags():
    out = format_flat_text([_rec("j", tags={"env": "ci"})])
    assert "env:ci" in out


def test_text_none_duration_shows_na():
    out = format_flat_text([_rec("j", duration=None)])
    assert "N/A" in out


def test_json_is_valid():
    records = [_rec("job-a", 1.0), _rec("job-b", 2.0, success=False)]
    out = format_flat_json(records)
    parsed = json.loads(out)
    assert len(parsed) == 2
    assert parsed[0]["job_id"] == "job-a"


def test_csv_has_header():
    out = format_flat_csv([_rec("j", 0.5)])
    lines = out.strip().splitlines()
    assert "job_id" in lines[0]
    assert "duration" in lines[0]


def test_csv_empty_returns_empty_string():
    assert format_flat_csv([]) == ""


def test_format_dispatch_json():
    out = format_flat([_rec("j")], fmt="json")
    parsed = json.loads(out)
    assert parsed[0]["job_id"] == "j"


def test_format_dispatch_csv():
    out = format_flat([_rec("j")], fmt="csv")
    assert "job_id" in out


def test_format_dispatch_default_text():
    out = format_flat([_rec("j")])
    assert "j" in out
