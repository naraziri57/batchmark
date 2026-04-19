import pytest
from batchmark.timer import TimingResult
from batchmark.differ import diff_results, DiffReport


def _r(job_id: str, duration: float | None = 1.0, success: bool = True) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success, error=None)


def test_empty_both_returns_empty_report():
    report = diff_results([], [])
    assert isinstance(report, DiffReport)
    assert report.entries == []


def test_added_job():
    report = diff_results([], [_r("job_a", 2.0)])
    assert len(report.entries) == 1
    assert report.entries[0].status == "added"
    assert report.entries[0].job_id == "job_a"
    assert report.entries[0].candidate_duration == 2.0


def test_removed_job():
    report = diff_results([_r("job_b", 1.5)], [])
    assert len(report.entries) == 1
    assert report.entries[0].status == "removed"
    assert report.entries[0].baseline_duration == 1.5


def test_unchanged_job():
    report = diff_results([_r("job_c", 1.0)], [_r("job_c", 1.0)])
    assert report.entries[0].status == "unchanged"
    assert report.entries[0].delta == 0.0


def test_changed_job():
    report = diff_results([_r("job_d", 1.0)], [_r("job_d", 2.5)])
    assert report.entries[0].status == "changed"
    assert abs(report.entries[0].delta - 1.5) < 1e-9


def test_mixed_diff():
    baseline = [_r("a", 1.0), _r("b", 2.0)]
    candidate = [_r("b", 2.0), _r("c", 3.0)]
    report = diff_results(baseline, candidate)
    statuses = {e.job_id: e.status for e in report.entries}
    assert statuses["a"] == "removed"
    assert statuses["b"] == "unchanged"
    assert statuses["c"] == "added"


def test_added_removed_changed_properties():
    baseline = [_r("x", 1.0)]
    candidate = [_r("x", 5.0), _r("y", 1.0)]
    report = diff_results(baseline, candidate)
    assert len(report.added) == 1
    assert len(report.changed) == 1
    assert len(report.removed) == 0


def test_to_dict_structure():
    report = diff_results([_r("j", 1.0)], [_r("j", 2.0)])
    d = report.to_dict()
    assert "entries" in d
    entry = d["entries"][0]
    assert "job_id" in entry
    assert "status" in entry
    assert "delta" in entry
