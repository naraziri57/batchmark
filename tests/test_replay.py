"""Tests for batchmark.replay and replay_cli."""

from __future__ import annotations

import json
import pytest
from pathlib import Path

from batchmark.timer import TimingResult
from batchmark.replay import load_replay, save_replay, filter_replay


def _r(job_id="job1", duration=1.0, success=True, error=None):
    return TimingResult(job_id=job_id, duration=duration, success=success, error=error, metadata={})


def test_save_and_load_roundtrip(tmp_path):
    results = [_r("a", 1.5), _r("b", 2.0, success=False, error="oops")]
    p = tmp_path / "replay.json"
    save_replay(results, p)
    loaded = load_replay(p)
    assert len(loaded) == 2
    assert loaded[0].job_id == "a"
    assert loaded[1].success is False
    assert loaded[1].error == "oops"


def test_load_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_replay(tmp_path / "nope.json")


def test_load_invalid_format_raises(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text(json.dumps({"not": "a list"}))
    with pytest.raises(ValueError):
        load_replay(p)


def test_filter_by_job_id():
    results = [_r("x"), _r("y"), _r("x")]
    out = filter_replay(results, job_id="x")
    assert len(out) == 2
    assert all(r.job_id == "x" for r in out)


def test_filter_success_only():
    results = [_r(success=True), _r(success=False), _r(success=True)]
    out = filter_replay(results, success_only=True)
    assert len(out) == 2
    assert all(r.success for r in out)


def test_filter_no_filters_returns_all():
    results = [_r("a"), _r("b")]
    assert filter_replay(results) == results


def test_save_creates_parent_dirs(tmp_path):
    p = tmp_path / "nested" / "dir" / "replay.json"
    save_replay([_r()], p)
    assert p.exists()
    data = json.loads(p.read_text())
    assert isinstance(data, list)
    assert data[0]["job_id"] == "job1"
