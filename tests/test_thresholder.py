import pytest
from batchmark.timer import TimingResult
from batchmark.thresholder import check_thresholds, ThresholdReport, ThresholdViolation


def _r(job_id, duration, success=True):
    return TimingResult(job_id=job_id, duration=duration, success=success, error=None)


def test_no_thresholds_returns_empty():
    results = [_r("a", 1.0), _r("b", 2.0)]
    report = check_thresholds(results)
    assert not report.has_violations
    assert report.violations == []


def test_global_threshold_no_violation():
    results = [_r("a", 0.5), _r("b", 0.8)]
    report = check_thresholds(results, global_threshold=1.0)
    assert not report.has_violations


def test_global_threshold_with_violation():
    results = [_r("a", 0.5), _r("b", 2.5)]
    report = check_thresholds(results, global_threshold=1.0)
    assert report.has_violations
    assert len(report.violations) == 1
    assert report.violations[0].job_id == "b"
    assert report.violations[0].threshold == 1.0


def test_per_job_threshold_overrides_global():
    results = [_r("a", 1.5), _r("b", 1.5)]
    report = check_thresholds(
        results,
        global_threshold=2.0,
        per_job_thresholds={"a": 1.0},
    )
    assert report.has_violations
    assert report.violations[0].job_id == "a"


def test_multiple_violations():
    results = [_r("a", 3.0), _r("b", 4.0), _r("c", 0.1)]
    report = check_thresholds(results, global_threshold=1.0)
    assert len(report.violations) == 2
    ids = {v.job_id for v in report.violations}
    assert ids == {"a", "b"}


def test_none_duration_skipped():
    results = [_r("a", None, success=False)]
    report = check_thresholds(results, global_threshold=1.0)
    assert not report.has_violations


def test_to_dict_structure():
    results = [_r("slow", 5.0)]
    report = check_thresholds(results, global_threshold=2.0)
    d = report.to_dict()
    assert d["has_violations"] is True
    assert len(d["violations"]) == 1
    v = d["violations"][0]
    assert v["job_id"] == "slow"
    assert v["duration"] == 5.0
    assert v["threshold"] == 2.0
    assert "exceeds" in v["message"]


def test_violation_message_format():
    results = [_r("myjob", 3.123)]
    report = check_thresholds(results, global_threshold=1.0)
    msg = report.violations[0].message
    assert "myjob" in msg
    assert "3.123" in msg
    assert "1.000" in msg
