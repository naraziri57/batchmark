"""Tests for batchmark.zipper."""
import pytest
from batchmark.timer import TimingResult
from batchmark.zipper import zip_results, ZippedPair


def _r(job_id: str, duration: float | None = 1.0, success: bool = True) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success)


def test_empty_both_returns_empty_report():
    report = zip_results([], [])
    assert report.pairs == []
    assert report.matched == []


def test_matched_pair_has_both_sides():
    left = [_r("job-a", 1.0)]
    right = [_r("job-a", 0.8)]
    report = zip_results(left, right)
    assert len(report.matched) == 1
    p = report.matched[0]
    assert p.job_id == "job-a"
    assert p.left_duration == 1.0
    assert p.right_duration == 0.8


def test_delta_calculated_correctly():
    p = ZippedPair(job_id="x", left=_r("x", 2.0), right=_r("x", 1.5))
    assert p.delta == pytest.approx(-0.5)


def test_delta_none_when_left_missing():
    p = ZippedPair(job_id="x", left=None, right=_r("x", 1.5))
    assert p.delta is None


def test_delta_none_when_right_missing():
    p = ZippedPair(job_id="x", left=_r("x", 1.0), right=None)
    assert p.delta is None


def test_only_in_left_detected():
    left = [_r("job-a"), _r("job-b")]
    right = [_r("job-a")]
    report = zip_results(left, right)
    assert len(report.only_in_left) == 1
    assert report.only_in_left[0].job_id == "job-b"


def test_only_in_right_detected():
    left = [_r("job-a")]
    right = [_r("job-a"), _r("job-c")]
    report = zip_results(left, right)
    assert len(report.only_in_right) == 1
    assert report.only_in_right[0].job_id == "job-c"


def test_pairs_sorted_by_job_id():
    left = [_r("z-job"), _r("a-job")]
    right = [_r("m-job")]
    report = zip_results(left, right)
    ids = [p.job_id for p in report.pairs]
    assert ids == sorted(ids)


def test_to_dict_structure():
    left = [_r("job-a", 1.0)]
    right = [_r("job-a", 0.5)]
    report = zip_results(left, right)
    d = report.to_dict()
    assert "pairs" in d
    assert d["matched_count"] == 1
    assert d["only_in_left_count"] == 0
    assert d["only_in_right_count"] == 0
    pair_d = d["pairs"][0]
    assert pair_d["job_id"] == "job-a"
    assert pair_d["delta"] == pytest.approx(-0.5)


def test_none_duration_pair():
    left = [_r("job-x", None)]
    right = [_r("job-x", 1.0)]
    report = zip_results(left, right)
    p = report.matched[0]
    assert p.left_duration is None
    assert p.delta is None
