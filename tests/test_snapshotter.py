"""Tests for snapshotter module."""
import os
import pytest

from batchmark.timer import TimingResult
from batchmark.snapshotter import (
    Snapshot,
    make_snapshot,
    save_snapshot,
    load_snapshot,
    list_snapshots,
)


def _r(job_id: str, duration: float = 1.0, success: bool = True) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success, error=None)


def test_make_snapshot_sets_label_and_timestamp():
    snap = make_snapshot("run1", [_r("job-a")])
    assert snap.label == "run1"
    assert "T" in snap.timestamp  # ISO format
    assert len(snap.results) == 1


def test_snapshot_to_dict_structure():
    snap = make_snapshot("run1", [_r("job-a", 2.5)])
    d = snap.to_dict()
    assert d["label"] == "run1"
    assert isinstance(d["results"], list)
    assert d["results"][0]["job_id"] == "job-a"
    assert d["results"][0]["duration"] == 2.5


def test_save_and_load_roundtrip(tmp_path):
    snap = make_snapshot("mysnap", [_r("job-1", 1.5), _r("job-2", 2.0, False)])
    save_snapshot(snap, str(tmp_path))
    loaded = load_snapshot("mysnap", str(tmp_path))
    assert loaded.label == "mysnap"
    assert len(loaded.results) == 2
    assert loaded.results[1].success is False


def test_load_preserves_failure(tmp_path):
    snap = make_snapshot("fail-snap", [_r("bad-job", 0.5, False)])
    save_snapshot(snap, str(tmp_path))
    loaded = load_snapshot("fail-snap", str(tmp_path))
    assert loaded.results[0].success is False


def test_load_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_snapshot("nonexistent", str(tmp_path))


def test_list_snapshots_empty(tmp_path):
    assert list_snapshots(str(tmp_path)) == []


def test_list_snapshots_returns_labels(tmp_path):
    save_snapshot(make_snapshot("alpha", [_r("j1")]), str(tmp_path))
    save_snapshot(make_snapshot("beta", [_r("j2")]), str(tmp_path))
    labels = list_snapshots(str(tmp_path))
    assert labels == ["alpha", "beta"]


def test_list_snapshots_missing_dir():
    assert list_snapshots("/tmp/batchmark_nonexistent_dir_xyz") == []
