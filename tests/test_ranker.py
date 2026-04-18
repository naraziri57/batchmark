"""Tests for batchmark.ranker."""

import pytest
from batchmark.timer import TimingResult
from batchmark.ranker import rank_results, RankedResult


def _r(job_id, duration, success=True):
    return TimingResult(job_id=job_id, duration=duration, success=success, error=None)


def test_empty_returns_empty():
    assert rank_results([]) == []


def test_single_result_rank_one():
    results = [_r("job_a", 1.0)]
    ranked = rank_results(results)
    assert len(ranked) == 1
    assert ranked[0].rank == 1
    assert ranked[0].result.job_id == "job_a"


def test_faster_job_ranks_higher():
    results = [_r("slow", 10.0), _r("fast", 1.0)]
    ranked = rank_results(results)
    assert ranked[0].result.job_id == "fast"
    assert ranked[1].result.job_id == "slow"


def test_success_bonus_applied():
    # failed job with same duration should rank lower
    results = [_r("ok", 5.0, success=True), _r("fail", 5.0, success=False)]
    ranked = rank_results(results)
    assert ranked[0].result.job_id == "ok"


def test_none_duration_scores_zero_duration():
    results = [_r("no_dur", None, success=True), _r("has_dur", 2.0, success=True)]
    ranked = rank_results(results)
    # has_dur should beat no_dur since it gets duration score
    job_ids = [r.result.job_id for r in ranked]
    assert job_ids[0] == "has_dur"


def test_breakdown_keys_present():
    results = [_r("j", 3.0)]
    ranked = rank_results(results)
    assert "duration_score" in ranked[0].breakdown
    assert "success_bonus" in ranked[0].breakdown


def test_to_dict_structure():
    results = [_r("j1", 2.0)]
    d = rank_results(results)[0].to_dict()
    assert d["rank"] == 1
    assert d["job_id"] == "j1"
    assert "score" in d
    assert "breakdown" in d


def test_ranks_are_sequential():
    results = [_r(f"job_{i}", float(i + 1)) for i in range(5)]
    ranked = rank_results(results)
    assert [r.rank for r in ranked] == [1, 2, 3, 4, 5]
