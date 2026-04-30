"""Tests for batchmark.scorer3."""
import pytest
from batchmark.timer import TimingResult
from batchmark.scorer3 import score_composite, CompositeReport


def _r(job_id, duration=None, success=True):
    return TimingResult(job_id=job_id, duration=duration, success=success)


def test_empty_returns_empty_report():
    report = score_composite([])
    assert isinstance(report, CompositeReport)
    assert report.scores == []
    assert report.overall() is None


def test_single_success_full_success_score():
    report = score_composite([_r("job1", duration=1.0)])
    assert len(report.scores) == 1
    s = report.scores[0]
    assert s.success_score == 100.0


def test_failed_job_zero_success_score():
    report = score_composite([_r("job1", duration=1.0, success=False)])
    assert report.scores[0].success_score == 0.0


def test_faster_job_ranks_higher_duration_score():
    results = [_r("fast", duration=1.0), _r("slow", duration=5.0)]
    report = score_composite(results)
    scores = {s.job_id: s for s in report.scores}
    assert scores["fast"].duration_score > scores["slow"].duration_score


def test_consistent_job_gets_high_consistency_score():
    results = [_r("job1", duration=1.0), _r("job1", duration=1.0), _r("job1", duration=1.0)]
    report = score_composite(results)
    assert report.scores[0].consistency_score == 100.0


def test_inconsistent_job_gets_lower_consistency_score():
    results = [_r("job1", duration=1.0), _r("job1", duration=10.0)]
    report = score_composite(results)
    assert report.scores[0].consistency_score < 100.0


def test_composite_is_weighted_average():
    results = [_r("j", duration=0.0, success=True)]
    report = score_composite(results, weights={"duration": 1.0, "success": 0.0, "consistency": 0.0})
    # duration 0 vs max 0 => score 0 (max_dur == 0 edge case)
    assert report.scores[0].composite == 0.0


def test_overall_averages_all_composites():
    results = [_r("a", duration=1.0), _r("b", duration=2.0)]
    report = score_composite(results)
    expected = sum(s.composite for s in report.scores) / 2
    assert abs(report.overall() - round(expected, 2)) < 0.01


def test_to_dict_structure():
    results = [_r("x", duration=1.0)]
    d = score_composite(results).to_dict()
    assert "overall" in d
    assert "scores" in d
    assert d["scores"][0]["job_id"] == "x"


def test_none_duration_treated_as_zero_score():
    results = [_r("j", duration=None, success=True)]
    report = score_composite(results)
    assert report.scores[0].duration_score == 0.0
