"""Tests for batchmark.pivotter."""
from __future__ import annotations
import pytest
from batchmark.timer import TimingResult
from batchmark.pivotter import pivot_results, PivotReport


def _r(job_id: str, success: bool = True, duration: float = 1.0) -> TimingResult:
    r = TimingResult(job_id=job_id, success=success)
    r.duration = duration
    return r


def _key(attr: str):
    return lambda r: getattr(r, attr, None)


def test_empty_returns_empty_report():
    report = pivot_results([], key_fn=lambda r: "x", pivot_key="env")
    assert isinstance(report, PivotReport)
    assert report.job_ids == []
    assert report.pivot_values == []


def test_single_result_creates_one_cell():
    r = _r("job-a", duration=2.0)
    r.env = "prod"
    report = pivot_results([r], key_fn=lambda x: getattr(x, "env", None), pivot_key="env")
    assert "job-a" in report.job_ids
    assert "prod" in report.pivot_values
    cell = report.get("job-a", "prod")
    assert cell is not None
    assert cell.count == 1
    assert cell.avg_duration == pytest.approx(2.0)


def test_multiple_pivot_values_per_job():
    r1 = _r("job-a", duration=1.0)
    r1.env = "dev"
    r2 = _r("job-a", duration=3.0)
    r2.env = "prod"
    report = pivot_results([r1, r2], key_fn=lambda x: getattr(x, "env", None), pivot_key="env")
    assert sorted(report.pivot_values) == ["dev", "prod"]
    assert report.get("job-a", "dev").avg_duration == pytest.approx(1.0)
    assert report.get("job-a", "prod").avg_duration == pytest.approx(3.0)


def test_avg_duration_across_multiple_results():
    r1 = _r("job-b", duration=2.0)
    r1.env = "staging"
    r2 = _r("job-b", duration=4.0)
    r2.env = "staging"
    report = pivot_results([r1, r2], key_fn=lambda x: getattr(x, "env", None), pivot_key="env")
    cell = report.get("job-b", "staging")
    assert cell.avg_duration == pytest.approx(3.0)
    assert cell.count == 2


def test_none_key_skips_result():
    r = _r("job-c", duration=5.0)
    report = pivot_results([r], key_fn=lambda x: None, pivot_key="env")
    assert report.job_ids == []


def test_success_count_tracked():
    r1 = _r("job-d", success=True, duration=1.0)
    r1.env = "qa"
    r2 = _r("job-d", success=False, duration=2.0)
    r2.env = "qa"
    report = pivot_results([r1, r2], key_fn=lambda x: getattr(x, "env", None), pivot_key="env")
    cell = report.get("job-d", "qa")
    assert cell.success_count == 1
    assert cell.count == 2


def test_to_dict_structure():
    r = _r("job-e", duration=1.5)
    r.env = "prod"
    report = pivot_results([r], key_fn=lambda x: getattr(x, "env", None), pivot_key="env")
    d = report.to_dict()
    assert d["pivot_key"] == "env"
    assert "job-e" in d["job_ids"]
    assert "prod" in d["pivot_values"]
    assert d["cells"]["job-e"]["prod"]["avg_duration"] == pytest.approx(1.5)


def test_multiple_jobs_sorted():
    for job_id in ["z-job", "a-job", "m-job"]:
        pass
    results = []
    for jid in ["z-job", "a-job", "m-job"]:
        r = _r(jid, duration=1.0)
        r.env = "prod"
        results.append(r)
    report = pivot_results(results, key_fn=lambda x: getattr(x, "env", None), pivot_key="env")
    assert report.job_ids == ["a-job", "m-job", "z-job"]
