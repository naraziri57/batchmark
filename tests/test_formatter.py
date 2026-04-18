"""Tests for batchmark.formatter."""

import json
from batchmark.timer import TimingResult
from batchmark.aggregator import aggregate
from batchmark.formatter import format_aggregation_text, format_aggregation_json, format_aggregation


def _make_result(job_id: str, duration: float, success: bool = True) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success, error=None)


def test_format_text_empty():
    out = format_aggregation_text({})
    assert "No results" in out


def test_format_text_single_job():
    agg = aggregate([_make_result("job1", 2.0), _make_result("job1", 4.0)])
    out = format_aggregation_text(agg)
    assert "job1" in out
    assert "total=2" in out
    assert "ok=2" in out
    assert "fail=0" in out
    assert "avg=3.0000s" in out


def test_format_text_multiple_jobs_sorted():
    agg = aggregate([
        _make_result("beta", 1.0),
        _make_result("alpha", 2.0),
    ])
    out = format_aggregation_text(agg)
    assert out.index("alpha") < out.index("beta")


def test_format_json_structure():
    agg = aggregate([_make_result("j", 3.0)])
    out = format_aggregation_json(agg)
    data = json.loads(out)
    assert "j" in data
    assert data["j"]["total"] == 1


def test_format_aggregation_dispatch_text():
    agg = aggregate([_make_result("x", 1.0)])
    out = format_aggregation(agg, fmt="text")
    assert "x" in out
    assert not out.startswith("{")


def test_format_aggregation_dispatch_json():
    agg = aggregate([_make_result("x", 1.0)])
    out = format_aggregation(agg, fmt="json")
    data = json.loads(out)
    assert "x" in data


def test_format_aggregation_default_is_text():
    agg = aggregate([_make_result("y", 1.5)])
    out = format_aggregation(agg)
    assert "y" in out
