"""Tests for batchmark.capper2 (rate capper)."""
import pytest
from batchmark.timer import TimingResult
from batchmark.capper2 import rate_cap, RateCapReport


def _r(job_id: str, duration: float = 1.0, success: bool = True, start_time: float = 0.0) -> TimingResult:
    return TimingResult(
        job_id=job_id,
        duration=duration,
        success=success,
        error=None,
        start_time=start_time,
    )


def test_empty_returns_empty_report():
    report = rate_cap([], max_per_job=5)
    assert report.total == 0
    assert report.accepted_count == 0
    assert report.rejected_count == 0


def test_all_accepted_when_under_cap():
    results = [_r("job-a"), _r("job-a"), _r("job-b")]
    report = rate_cap(results, max_per_job=5)
    assert report.accepted_count == 3
    assert report.rejected_count == 0


def test_excess_results_rejected():
    results = [_r("job-a")] * 5
    report = rate_cap(results, max_per_job=3)
    assert report.accepted_count == 3
    assert report.rejected_count == 2


def test_cap_applied_per_job_id_independently():
    results = [_r("job-a")] * 3 + [_r("job-b")] * 3
    report = rate_cap(results, max_per_job=2)
    assert report.accepted_count == 4
    assert report.rejected_count == 2


def test_max_per_job_zero_rejects_all():
    results = [_r("job-a"), _r("job-b")]
    report = rate_cap(results, max_per_job=0)
    assert report.accepted_count == 0
    assert report.rejected_count == 2


def test_rejected_item_has_reason():
    results = [_r("job-a")] * 2
    report = rate_cap(results, max_per_job=1)
    rejected = [i for i in report.items if not i.accepted]
    assert len(rejected) == 1
    assert rejected[0].reason is not None
    assert "max_per_job=1" in rejected[0].reason


def test_window_seconds_resets_count_per_window():
    # Two results in window 0 and two in window 1 (each 10s wide)
    results = [
        _r("job-a", start_time=0.0),
        _r("job-a", start_time=5.0),
        _r("job-a", start_time=10.0),
        _r("job-a", start_time=15.0),
    ]
    report = rate_cap(results, max_per_job=1, window_seconds=10.0)
    assert report.accepted_count == 2
    assert report.rejected_count == 2


def test_accepted_returns_timing_results():
    results = [_r("job-a")] * 3
    report = rate_cap(results, max_per_job=2)
    accepted = report.accepted()
    assert len(accepted) == 2
    assert all(r.job_id == "job-a" for r in accepted)


def test_to_dict_structure():
    results = [_r("job-a")] * 2
    report = rate_cap(results, max_per_job=1)
    d = report.to_dict()
    assert d["total"] == 2
    assert d["accepted"] == 1
    assert d["rejected"] == 1
    assert len(d["items"]) == 2


def test_negative_max_per_job_raises():
    with pytest.raises(ValueError):
        rate_cap([_r("job-a")], max_per_job=-1)
