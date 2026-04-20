"""Tests for batchmark.capper."""
from __future__ import annotations

import pytest

from batchmark.timer import TimingResult
from batchmark.capper import cap_results, CapReport, CappedResult


def _r(job_id: str, duration, success: bool = True) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success, error=None)


def test_empty_returns_empty_report():
    report = cap_results([], max_duration=5.0)
    assert report.total == 0
    assert report.capped_count == 0


def test_no_violations_when_all_under_cap():
    results = [_r("a", 1.0), _r("b", 2.5), _r("c", 4.9)]
    report = cap_results(results, max_duration=5.0)
    assert report.capped_count == 0
    assert report.total == 3
    for cr in report.results:
        assert not cr.capped


def test_duration_exactly_at_cap_not_flagged():
    results = [_r("a", 5.0)]
    report = cap_results(results, max_duration=5.0)
    assert report.capped_count == 0
    assert not report.results[0].capped


def test_duration_above_cap_is_clamped():
    results = [_r("slow", 10.0)]
    report = cap_results(results, max_duration=5.0)
    assert report.capped_count == 1
    cr = report.results[0]
    assert cr.capped
    assert cr.result.duration == 5.0
    assert cr.original_duration == 10.0


def test_multiple_results_mixed_capping():
    results = [_r("fast", 1.0), _r("slow", 20.0), _r("medium", 4.0)]
    report = cap_results(results, max_duration=5.0)
    assert report.capped_count == 1
    assert report.results[1].capped
    assert not report.results[0].capped
    assert not report.results[2].capped


def test_per_job_override_raises_own_cap():
    results = [_r("a", 8.0), _r("b", 8.0)]
    report = cap_results(results, max_duration=5.0, per_job={"a": 10.0})
    # job a has a higher cap so it should NOT be capped
    assert not report.results[0].capped
    # job b uses global cap of 5.0 and 8.0 > 5.0
    assert report.results[1].capped
    assert report.results[1].result.duration == 5.0


def test_per_job_override_lowers_cap():
    results = [_r("strict", 3.0)]
    report = cap_results(results, max_duration=10.0, per_job={"strict": 2.0})
    assert report.capped_count == 1
    assert report.results[0].result.duration == 2.0
    assert report.results[0].original_duration == 3.0


def test_none_duration_not_capped():
    results = [_r("failed", None, success=False)]
    report = cap_results(results, max_duration=5.0)
    assert report.capped_count == 0
    assert not report.results[0].capped


def test_to_dict_structure():
    results = [_r("x", 7.0)]
    report = cap_results(results, max_duration=5.0)
    d = report.to_dict()
    assert d["total"] == 1
    assert d["capped_count"] == 1
    entry = d["results"][0]
    assert entry["capped"] is True
    assert entry["original_duration"] == 7.0
    assert entry["duration"] == 5.0
