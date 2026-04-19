import json
import pytest
from batchmark.timer import TimingResult
from batchmark.watchdog import check_timeouts, TimeoutViolation, WatchdogReport
from batchmark.watchdog_formatter import format_watchdog, format_watchdog_text, format_watchdog_json


def _r(job_id, duration, success=True):
    return TimingResult(job_id=job_id, duration=duration, success=success, error=None)


def test_no_limits_returns_empty():
    results = [_r("a", 1.0), _r("b", 2.0)]
    report = check_timeouts(results)
    assert not report.has_violations
    assert report.violations == []


def test_global_limit_no_violation():
    results = [_r("a", 1.0), _r("b", 0.5)]
    report = check_timeouts(results, global_limit=2.0)
    assert not report.has_violations


def test_global_limit_with_violation():
    results = [_r("a", 3.0), _r("b", 0.5)]
    report = check_timeouts(results, global_limit=2.0)
    assert report.has_violations
    assert len(report.violations) == 1
    assert report.violations[0].job_id == "a"
    assert report.violations[0].limit == 2.0


def test_per_job_limit_overrides_global():
    results = [_r("a", 3.0), _r("b", 3.0)]
    report = check_timeouts(results, global_limit=2.0, per_job_limits={"a": 5.0})
    assert report.has_violations
    assert len(report.violations) == 1
    assert report.violations[0].job_id == "b"


def test_none_duration_skipped():
    results = [_r("a", None)]
    report = check_timeouts(results, global_limit=1.0)
    assert not report.has_violations


def test_to_dict_structure():
    v = TimeoutViolation(job_id="x", duration=4.0, limit=2.0)
    d = v.to_dict()
    assert d["job_id"] == "x"
    assert d["duration"] == 4.0
    assert d["limit"] == 2.0


def test_format_text_no_violations():
    report = WatchdogReport()
    out = format_watchdog_text(report)
    assert "no timeout" in out


def test_format_text_with_violation():
    report = WatchdogReport(violations=[TimeoutViolation("job1", 5.0, 3.0)])
    out = format_watchdog_text(report)
    assert "job1" in out
    assert "5.000s" in out


def test_format_json_valid():
    report = WatchdogReport(violations=[TimeoutViolation("job1", 5.0, 3.0)])
    out = format_watchdog_json(report)
    data = json.loads(out)
    assert data["has_violations"] is True
    assert data["violations"][0]["job_id"] == "job1"


def test_format_dispatch():
    report = WatchdogReport()
    assert format_watchdog(report, fmt="text") == format_watchdog_text(report)
    assert format_watchdog(report, fmt="json") == format_watchdog_json(report)
