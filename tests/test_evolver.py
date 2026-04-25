"""Tests for batchmark.evolver."""
import pytest
from batchmark.timer import TimingResult
from batchmark.evolver import evolve, EvolvedJob, EvolverReport


def _r(job_id: str, duration: float | None, success: bool = True) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success)


def test_empty_runs_returns_empty_report():
    report = evolve({})
    assert report.run_labels == []
    assert report.jobs == []


def test_single_run_single_job():
    report = evolve({"v1": [_r("job-a", 1.0)]})
    assert report.run_labels == ["v1"]
    assert len(report.jobs) == 1
    assert report.jobs[0].job_id == "job-a"
    assert report.jobs[0].durations == [1.0]


def test_two_runs_same_job_tracks_both():
    report = evolve({
        "v1": [_r("job-a", 1.0)],
        "v2": [_r("job-a", 0.8)],
    })
    job = report.jobs[0]
    assert job.durations == [1.0, 0.8]
    assert job.net_change() == pytest.approx(-0.2)


def test_failed_job_records_none_duration():
    report = evolve({"v1": [_r("job-a", None, success=False)]})
    assert report.jobs[0].durations == [None]


def test_job_absent_in_later_run_padded_with_none():
    report = evolve({
        "v1": [_r("job-a", 1.0)],
        "v2": [],
    })
    assert report.jobs[0].durations == [1.0, None]


def test_new_job_in_second_run_padded_at_start():
    report = evolve({
        "v1": [],
        "v2": [_r("job-b", 2.0)],
    })
    assert report.jobs[0].job_id == "job-b"
    assert report.jobs[0].durations == [None, 2.0]


def test_net_change_none_when_only_one_data_point():
    report = evolve({
        "v1": [_r("job-a", 1.0)],
        "v2": [],
    })
    assert report.jobs[0].net_change() is None


def test_to_dict_structure():
    report = evolve({"v1": [_r("job-a", 1.5)], "v2": [_r("job-a", 1.2)]})
    d = report.to_dict()
    assert "run_labels" in d
    assert "jobs" in d
    assert d["jobs"][0]["net_change"] == pytest.approx(-0.3)


def test_jobs_sorted_alphabetically():
    report = evolve({"v1": [_r("job-z", 1.0), _r("job-a", 2.0)]})
    ids = [j.job_id for j in report.jobs]
    assert ids == sorted(ids)
