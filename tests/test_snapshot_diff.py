"""Tests for snapshot_diff and snapshot_formatter modules."""
import json
import pytest

from batchmark.timer import TimingResult
from batchmark.snapshotter import make_snapshot
from batchmark.snapshot_diff import diff_snapshots, SnapshotDiffEntry
from batchmark.snapshot_formatter import format_snapshot_diff


def _r(job_id: str, duration: float = 1.0, success: bool = True) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success, error=None)


def test_diff_empty_snapshots():
    before = make_snapshot("b", [])
    after = make_snapshot("a", [])
    report = diff_snapshots(before, after)
    assert report.entries == []
    assert report.changed() == []


def test_diff_no_change():
    before = make_snapshot("b", [_r("job-1", 1.0)])
    after = make_snapshot("a", [_r("job-1", 1.0)])
    report = diff_snapshots(before, after)
    assert len(report.entries) == 1
    assert report.entries[0].delta == pytest.approx(0.0)
    assert report.changed() == []


def test_diff_improvement():
    before = make_snapshot("b", [_r("job-1", 2.0)])
    after = make_snapshot("a", [_r("job-1", 1.0)])
    report = diff_snapshots(before, after)
    assert report.entries[0].delta == pytest.approx(-1.0)


def test_diff_regression():
    before = make_snapshot("b", [_r("job-1", 1.0)])
    after = make_snapshot("a", [_r("job-1", 3.0)])
    report = diff_snapshots(before, after)
    assert report.entries[0].delta == pytest.approx(2.0)


def test_diff_status_changed():
    before = make_snapshot("b", [_r("job-1", 1.0, True)])
    after = make_snapshot("a", [_r("job-1", 1.0, False)])
    report = diff_snapshots(before, after)
    assert report.entries[0].status_changed is True
    assert len(report.changed()) == 1


def test_diff_missing_in_after():
    before = make_snapshot("b", [_r("job-1"), _r("job-2")])
    after = make_snapshot("a", [_r("job-1")])
    report = diff_snapshots(before, after)
    ids = [e.job_id for e in report.entries]
    assert "job-2" in ids
    missing = next(e for e in report.entries if e.job_id == "job-2")
    assert missing.after_duration is None


def test_format_text_empty():
    before = make_snapshot("b", [])
    after = make_snapshot("a", [])
    report = diff_snapshots(before, after)
    out = format_snapshot_diff(report, fmt="text")
    assert "No jobs" in out


def test_format_text_contains_job_id():
    before = make_snapshot("b", [_r("my-job", 1.0)])
    after = make_snapshot("a", [_r("my-job", 0.5)])
    report = diff_snapshots(before, after)
    out = format_snapshot_diff(report, fmt="text")
    assert "my-job" in out


def test_format_json_is_valid():
    before = make_snapshot("b", [_r("j1", 1.0)])
    after = make_snapshot("a", [_r("j1", 2.0)])
    report = diff_snapshots(before, after)
    out = format_snapshot_diff(report, fmt="json")
    data = json.loads(out)
    assert data["before_label"] == "b"
    assert len(data["entries"]) == 1
