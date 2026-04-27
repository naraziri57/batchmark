"""tests for batchmark.cruncher"""
from __future__ import annotations

import pytest

from batchmark.timer import TimingResult
from batchmark.cruncher import crunch, CrunchReport, _percentile


def _r(job_id: str, duration: float | None, success: bool = True) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success, error=None)


def test_empty_returns_empty_report():
    report = crunch([])
    assert isinstance(report, CrunchReport)
    assert report.jobs == []


def test_single_result_basic_counts():
    report = crunch([_r("job-a", 1.0)])
    assert len(report.jobs) == 1
    j = report.jobs[0]
    assert j.job_id == "job-a"
    assert j.count == 1
    assert j.success_count == 1
    assert j.failure_count == 0


def test_min_max_mean_single():
    report = crunch([_r("job-a", 2.5)])
    j = report.jobs[0]
    assert j.min_duration == 2.5
    assert j.max_duration == 2.5
    assert j.mean_duration == 2.5


def test_stdev_requires_two_samples():
    report = crunch([_r("j", 1.0)])
    assert report.jobs[0].stdev_duration is None

    report2 = crunch([_r("j", 1.0), _r("j", 3.0)])
    assert report2.jobs[0].stdev_duration is not None


def test_failure_counted_correctly():
    results = [_r("j", 1.0, success=True), _r("j", 2.0, success=False), _r("j", 3.0, success=False)]
    report = crunch(results)
    j = report.jobs[0]
    assert j.success_count == 1
    assert j.failure_count == 2


def test_none_duration_excluded_from_stats():
    results = [_r("j", None, success=False), _r("j", 4.0)]
    report = crunch(results)
    j = report.jobs[0]
    assert j.count == 2
    assert j.min_duration == 4.0
    assert j.max_duration == 4.0


def test_multiple_jobs_grouped_separately():
    results = [_r("a", 1.0), _r("b", 2.0), _r("a", 3.0)]
    report = crunch(results)
    assert len(report.jobs) == 2
    a = report.get("a")
    assert a is not None
    assert a.count == 2


def test_p50_and_p95_calculated():
    durations = [1.0, 2.0, 3.0, 4.0, 5.0]
    results = [_r("j", d) for d in durations]
    report = crunch(results)
    j = report.jobs[0]
    assert j.p50 == 3.0
    assert j.p95 is not None and j.p95 >= 4.0


def test_percentile_empty_returns_none():
    assert _percentile([], 50) is None


def test_to_dict_structure():
    report = crunch([_r("x", 1.0)])
    d = report.to_dict()
    assert "jobs" in d
    assert d["jobs"][0]["job_id"] == "x"
    assert "mean_duration" in d["jobs"][0]
    assert "p95" in d["jobs"][0]


def test_get_returns_none_for_missing_job():
    report = crunch([_r("a", 1.0)])
    assert report.get("missing") is None
