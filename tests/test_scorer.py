"""Tests for batchmark.scorer."""

import pytest
from batchmark.timer import TimingResult
from batchmark.scorer import score_results, ScoringReport, JobScore


def _r(job_id: str, duration: float = None, success: bool = True) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success, error=None)


def test_empty_results_returns_empty_report():
    report = score_results([], {})
    assert isinstance(report, ScoringReport)
    assert report.scores == []
    assert report.overall == 0.0


def test_no_baseline_gives_full_score():
    results = [_r("job1", duration=2.0)]
    report = score_results(results, {})
    assert len(report.scores) == 1
    s = report.scores[0]
    assert s.score == 1.0
    assert "no baseline available" in s.notes


def test_failed_job_applies_penalty():
    results = [_r("job1", duration=1.0, success=False)]
    report = score_results(results, {"job1": 1.0}, failure_penalty=0.5)
    s = report.scores[0]
    assert s.score == 0.5
    assert s.penalty == 0.5
    assert "job failed" in s.notes


def test_improvement_gives_high_score():
    results = [_r("job1", duration=0.5)]
    report = score_results(results, {"job1": 1.0})
    s = report.scores[0]
    assert s.score == 1.0
    assert any("improvement" in n for n in s.notes)


def test_regression_reduces_score():
    results = [_r("job1", duration=2.0)]
    report = score_results(results, {"job1": 1.0}, regression_weight=1.0)
    s = report.scores[0]
    assert s.score == 0.0
    assert s.penalty == 1.0
    assert any("regression" in n for n in s.notes)


def test_partial_regression():
    results = [_r("job1", duration=1.5)]
    report = score_results(results, {"job1": 1.0}, regression_weight=1.0)
    s = report.scores[0]
    assert 0.0 < s.score < 1.0


def test_overall_is_average():
    results = [_r("a", duration=1.0), _r("b", duration=2.0)]
    baselines = {"a": 1.0, "b": 1.0}
    report = score_results(results, baselines, regression_weight=1.0)
    scores = [s.score for s in report.scores]
    assert report.overall == round(sum(scores) / len(scores), 4)


def test_to_dict_structure():
    results = [_r("job1", duration=1.0)]
    report = score_results(results, {"job1": 1.0})
    d = report.to_dict()
    assert "overall" in d
    assert "jobs" in d
    assert d["jobs"][0]["job_id"] == "job1"


def test_no_duration_gives_neutral_score():
    results = [_r("job1", duration=None)]
    report = score_results(results, {"job1": 1.0})
    s = report.scores[0]
    assert s.score == 0.5
    assert "no duration recorded" in s.notes
