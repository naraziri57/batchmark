"""Tests for batchmark.scorer2."""
import pytest
from batchmark.timer import TimingResult
from batchmark.scorer2 import weighted_score, WeightedScoringReport


def _r(job_id, duration=None, success=True):
    return TimingResult(job_id=job_id, duration=duration, success=success)


def test_empty_returns_empty_report():
    report = weighted_score([])
    assert isinstance(report, WeightedScoringReport)
    assert report.scores == []
    assert report.overall() is None


def test_single_success_full_duration_score():
    # Only one result — it is the max, so dur_score = 0.0 (1 - 1.0)
    report = weighted_score([_r("job-a", duration=2.0)])
    assert len(report.scores) == 1
    s = report.scores[0]
    assert s.duration_score == pytest.approx(0.0)
    assert s.success_score == pytest.approx(1.0)


def test_faster_job_gets_higher_duration_score():
    results = [_r("slow", duration=10.0), _r("fast", duration=2.0)]
    report = weighted_score(results)
    by_id = {s.job_id: s for s in report.scores}
    assert by_id["fast"].duration_score > by_id["slow"].duration_score


def test_failed_job_zero_success_score():
    report = weighted_score([_r("job-x", duration=1.0, success=False)])
    assert report.scores[0].success_score == pytest.approx(0.0)


def test_weighted_total_uses_weights():
    results = [_r("a", duration=5.0), _r("b", duration=10.0)]
    report = weighted_score(results, duration_weight=0.7, success_weight=0.3)
    by_id = {s.job_id: s for s in report.scores}
    expected = 0.7 * by_id["a"].duration_score + 0.3 * by_id["a"].success_score
    assert by_id["a"].weighted_total == pytest.approx(expected)


def test_overall_is_mean_of_totals():
    results = [_r("a", duration=1.0), _r("b", duration=3.0)]
    report = weighted_score(results)
    expected = sum(s.weighted_total for s in report.scores) / 2
    assert report.overall() == pytest.approx(expected)


def test_none_duration_gives_zero_duration_score():
    report = weighted_score([_r("job-n", duration=None)])
    assert report.scores[0].duration_score == pytest.approx(0.0)


def test_baseline_adds_vs_baseline_tag():
    results = [_r("job-a", duration=1.0)]
    baseline = {"job-a": 2.0}
    report = weighted_score(results, baseline_durations=baseline)
    assert "vs_baseline" in report.scores[0].tags
    assert report.scores[0].tags["vs_baseline"] == pytest.approx(0.5)


def test_to_dict_structure():
    report = weighted_score([_r("j1", duration=1.0), _r("j2", duration=2.0)])
    d = report.to_dict()
    assert "scores" in d
    assert "overall" in d
    assert isinstance(d["scores"], list)
    assert d["scores"][0]["job_id"] in {"j1", "j2"}
