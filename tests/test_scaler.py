"""Tests for batchmark.scaler."""
import pytest
from batchmark.timer import TimingResult
from batchmark.scaler import scale_results, ScaleReport


def _r(job_id: str, duration, success: bool = True) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success, error=None)


def test_empty_returns_empty_report():
    report = scale_results([])
    assert report.total == 0
    assert report.affected == 0


def test_scale_by_factor_doubles_duration():
    results = [_r("job1", 2.0), _r("job2", 4.0)]
    report = scale_results(results, factor=2.0)
    assert report.total == 2
    durations = {s.result.job_id: s.scaled_duration for s in report.scaled}
    assert durations["job1"] == pytest.approx(4.0)
    assert durations["job2"] == pytest.approx(8.0)


def test_scale_by_factor_half():
    results = [_r("a", 10.0)]
    report = scale_results(results, factor=0.5)
    assert report.scaled[0].scaled_duration == pytest.approx(5.0)
    assert report.scaled[0].scale_factor == pytest.approx(0.5)


def test_none_duration_preserved():
    results = [_r("job1", None)]
    report = scale_results(results, factor=3.0)
    s = report.scaled[0]
    assert s.original_duration is None
    assert s.scaled_duration is None


def test_target_range_maps_correctly():
    results = [_r("a", 0.0), _r("b", 5.0), _r("c", 10.0)]
    report = scale_results(results, target_min=0.0, target_max=1.0)
    durations = {s.result.job_id: s.scaled_duration for s in report.scaled}
    assert durations["a"] == pytest.approx(0.0)
    assert durations["b"] == pytest.approx(0.5)
    assert durations["c"] == pytest.approx(1.0)


def test_target_range_all_equal_maps_to_midpoint():
    results = [_r("a", 4.0), _r("b", 4.0)]
    report = scale_results(results, target_min=2.0, target_max=6.0)
    for s in report.scaled:
        assert s.scaled_duration == pytest.approx(4.0)


def test_factor_and_target_range_raises():
    results = [_r("a", 1.0)]
    with pytest.raises(ValueError):
        scale_results(results, factor=2.0, target_min=0.0, target_max=1.0)


def test_affected_count_excludes_none_duration():
    results = [_r("a", 2.0), _r("b", None)]
    report = scale_results(results, factor=2.0)
    # only "a" has a changed duration; "b" has None so original == scaled (both None)
    assert report.affected == 1


def test_to_dict_structure():
    results = [_r("job1", 3.0)]
    report = scale_results(results, factor=2.0)
    d = report.to_dict()
    assert "total" in d
    assert "affected" in d
    assert "scaled" in d
    entry = d["scaled"][0]
    assert entry["job_id"] == "job1"
    assert entry["original_duration"] == pytest.approx(3.0)
    assert entry["scaled_duration"] == pytest.approx(6.0)
    assert entry["scale_factor"] == pytest.approx(2.0)


def test_no_factor_no_range_leaves_unchanged():
    results = [_r("x", 5.0)]
    report = scale_results(results)
    assert report.scaled[0].scaled_duration == pytest.approx(5.0)
    assert report.affected == 0
