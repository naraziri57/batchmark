"""Tests for batchmark.pruner."""
from __future__ import annotations
import pytest
from batchmark.timer import TimingResult
from batchmark.pruner import prune_results, PruneReport


def _r(job_id: str, duration, success: bool = True) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success, error=None)


def test_empty_returns_empty_report():
    report = prune_results([])
    assert report.kept == []
    assert report.dropped == []
    assert report.kept_count == 0
    assert report.dropped_count == 0


def test_no_thresholds_keeps_all():
    results = [_r("a", 1.0), _r("b", 2.0), _r("c", 0.1)]
    report = prune_results(results)
    assert report.kept_count == 3
    assert report.dropped_count == 0


def test_min_duration_drops_slow_below_threshold():
    results = [_r("fast", 0.05), _r("ok", 1.0), _r("also_fast", 0.01)]
    report = prune_results(results, min_duration=0.1)
    assert report.kept_count == 1
    assert report.dropped_count == 2
    dropped_ids = {r.job_id for r in report.dropped}
    assert dropped_ids == {"fast", "also_fast"}


def test_min_duration_keeps_none_duration():
    """Results with None duration should not be dropped by min_duration."""
    results = [_r("no_time", None), _r("slow", 0.001)]
    report = prune_results(results, min_duration=0.5)
    kept_ids = {r.job_id for r in report.kept}
    assert "no_time" in kept_ids
    assert "slow" not in kept_ids


def test_min_score_drops_low_scoring_jobs():
    scores = {"a": 90.0, "b": 40.0, "c": 75.0}
    results = [_r("a", 1.0), _r("b", 1.0), _r("c", 1.0)]
    report = prune_results(results, min_score=60.0, scores=scores)
    assert report.kept_count == 2
    assert report.dropped_count == 1
    assert report.dropped[0].job_id == "b"


def test_min_score_keeps_missing_from_scores():
    """Jobs not present in scores dict are kept regardless."""
    scores = {"a": 10.0}
    results = [_r("a", 1.0), _r("unknown", 1.0)]
    report = prune_results(results, min_score=50.0, scores=scores)
    kept_ids = {r.job_id for r in report.kept}
    assert "unknown" in kept_ids
    assert "a" not in kept_ids


def test_combined_duration_and_score():
    scores = {"a": 80.0, "b": 20.0, "c": 90.0}
    results = [_r("a", 0.01), _r("b", 1.0), _r("c", 1.0)]
    report = prune_results(results, min_duration=0.1, min_score=50.0, scores=scores)
    kept_ids = {r.job_id for r in report.kept}
    assert kept_ids == {"c"}
    assert report.dropped_count == 2


def test_to_dict_structure():
    results = [_r("x", 0.5), _r("y", 0.01)]
    report = prune_results(results, min_duration=0.1)
    d = report.to_dict()
    assert "kept_count" in d
    assert "dropped_count" in d
    assert "min_duration" in d
    assert "min_score" in d
    assert "dropped_job_ids" in d
    assert d["dropped_job_ids"] == ["y"]


def test_report_min_values_stored():
    report = prune_results([], min_duration=2.5, min_score=70.0)
    assert report.min_duration == 2.5
    assert report.min_score == 70.0
