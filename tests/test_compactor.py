"""Tests for batchmark.compactor and batchmark.compactor_formatter."""
from __future__ import annotations

import json

import pytest

from batchmark.timer import TimingResult
from batchmark.compactor import compact_results, CompactedResult, CompactReport
from batchmark.compactor_formatter import format_compact, format_compact_text, format_compact_json


def _r(job_id: str, duration, success: bool = True) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success)


# ---------------------------------------------------------------------------
# compact_results
# ---------------------------------------------------------------------------

def test_empty_returns_empty_report():
    report = compact_results([])
    assert report.total == 0
    assert report.results == []


def test_single_result_passthrough():
    report = compact_results([_r("job1", 1.0)], strategy="best")
    assert report.total == 1
    assert report.results[0].job_id == "job1"
    assert report.results[0].duration == pytest.approx(1.0)
    assert report.results[0].source_count == 1


def test_best_strategy_picks_minimum():
    results = [_r("job1", 3.0), _r("job1", 1.0), _r("job1", 2.0)]
    report = compact_results(results, strategy="best")
    assert report.results[0].duration == pytest.approx(1.0)


def test_worst_strategy_picks_maximum():
    results = [_r("job1", 3.0), _r("job1", 1.0), _r("job1", 2.0)]
    report = compact_results(results, strategy="worst")
    assert report.results[0].duration == pytest.approx(3.0)


def test_mean_strategy_averages():
    results = [_r("job1", 1.0), _r("job1", 3.0)]
    report = compact_results(results, strategy="mean")
    assert report.results[0].duration == pytest.approx(2.0)


def test_first_strategy_keeps_first():
    results = [_r("job1", 5.0), _r("job1", 1.0)]
    report = compact_results(results, strategy="first")
    assert report.results[0].duration == pytest.approx(5.0)


def test_last_strategy_keeps_last():
    results = [_r("job1", 5.0), _r("job1", 1.0)]
    report = compact_results(results, strategy="last")
    assert report.results[0].duration == pytest.approx(1.0)


def test_multiple_jobs_kept_separate():
    results = [_r("a", 1.0), _r("b", 2.0), _r("a", 0.5)]
    report = compact_results(results, strategy="best")
    job_ids = {r.job_id for r in report.results}
    assert job_ids == {"a", "b"}


def test_any_success_true_when_mixed():
    results = [_r("job1", 1.0, success=False), _r("job1", 2.0, success=True)]
    report = compact_results(results, strategy="best")
    assert report.results[0].success is True


def test_none_duration_handled():
    results = [_r("job1", None, success=False), _r("job1", None, success=False)]
    report = compact_results(results, strategy="best")
    assert report.results[0].duration is None


def test_to_dict_structure():
    results = [_r("job1", 1.5)]
    d = compact_results(results, strategy="best").to_dict()
    assert "strategy" in d
    assert "total" in d
    assert "results" in d
    assert d["results"][0]["job_id"] == "job1"


# ---------------------------------------------------------------------------
# formatter
# ---------------------------------------------------------------------------

def test_text_empty():
    report = compact_results([])
    out = format_compact_text(report)
    assert "No compacted" in out


def test_text_contains_job_id():
    report = compact_results([_r("myjob", 0.42)])
    out = format_compact_text(report)
    assert "myjob" in out


def test_text_shows_strategy():
    report = compact_results([_r("j", 1.0)], strategy="worst")
    out = format_compact_text(report)
    assert "worst" in out


def test_json_output_is_valid():
    report = compact_results([_r("j", 1.0)])
    out = format_compact_json(report)
    data = json.loads(out)
    assert data["total"] == 1


def test_format_dispatch_defaults_to_text():
    report = compact_results([_r("j", 1.0)])
    assert format_compact(report, "text") == format_compact_text(report)
