"""Tests for batchmark.merger."""
from __future__ import annotations

import pytest

from batchmark.timer import TimingResult
from batchmark.merger import merge, MergeReport


def _r(job_id: str, success: bool = True, duration: float | None = 1.0) -> TimingResult:
    return TimingResult(
        job_id=job_id,
        success=success,
        duration=duration,
        error=None if success else "err",
    )


def test_empty_runs_returns_empty_report():
    report = merge([])
    assert report.total() == 0
    assert report.source_labels == []
    assert report.conflict_count() == 0


def test_single_run_no_conflicts():
    results = [_r("job_a"), _r("job_b")]
    report = merge([results])
    assert report.total() == 2
    assert report.conflict_count() == 0


def test_two_runs_no_overlap():
    run1 = [_r("job_a")]
    run2 = [_r("job_b")]
    report = merge([run1, run2], labels=["baseline", "candidate"])
    assert report.total() == 2
    assert report.source_labels == ["baseline", "candidate"]
    assert report.conflict_count() == 0


def test_keep_all_on_conflict():
    run1 = [_r("job_a", duration=1.0)]
    run2 = [_r("job_a", duration=2.0)]
    report = merge([run1, run2], on_conflict="keep_all")
    assert report.total() == 2
    assert report.conflict_count() == 1
    assert "job_a" in report.conflicts


def test_keep_first_on_conflict():
    run1 = [_r("job_a", duration=1.0)]
    run2 = [_r("job_a", duration=2.0)]
    report = merge([run1, run2], on_conflict="keep_first")
    assert report.total() == 1
    assert report.results[0].duration == 1.0
    assert report.conflict_count() == 1


def test_keep_last_on_conflict():
    run1 = [_r("job_a", duration=1.0)]
    run2 = [_r("job_a", duration=2.0)]
    report = merge([run1, run2], on_conflict="keep_last")
    assert report.total() == 1
    assert report.results[0].duration == 2.0


def test_default_labels_generated():
    report = merge([[_r("a")], [_r("b")]])
    assert report.source_labels == ["run_0", "run_1"]


def test_labels_length_mismatch_raises():
    with pytest.raises(ValueError, match="labels length"):
        merge([[_r("a")], [_r("b")]], labels=["only_one"])


def test_unknown_conflict_strategy_raises():
    with pytest.raises(ValueError, match="Unknown on_conflict"):
        merge([[_r("a")]], on_conflict="random")


def test_to_dict_structure():
    report = merge([[_r("job_x")]], labels=["run_0"])
    d = report.to_dict()
    assert d["total"] == 1
    assert d["source_labels"] == ["run_0"]
    assert d["conflict_count"] == 0
    assert d["conflicts"] == []
