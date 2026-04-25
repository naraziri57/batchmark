"""Tests for batchmark.leveler and batchmark.leveler_formatter."""
import json
import pytest
from batchmark.timer import TimingResult
from batchmark.leveler import level_results, LevelReport
from batchmark.leveler_formatter import format_level, format_level_csv


def _r(job_id: str, duration=None, success: bool = True) -> TimingResult:
    r = TimingResult(job_id=job_id)
    r.duration = duration
    r.success = success
    r.error = None if success else "err"
    return r


def test_empty_returns_empty_report():
    report = level_results([])
    assert report.items == []
    assert report.critical_count == 0
    assert report.warn_count == 0


def test_all_ok_when_no_thresholds():
    results = [_r("job1", 1.0), _r("job2", 5.0)]
    report = level_results(results)
    assert all(i.level == "ok" for i in report.items)


def test_warn_threshold_triggers():
    results = [_r("job1", 1.5), _r("job2", 0.5)]
    report = level_results(results, warn_above=1.0)
    levels = {i.result.job_id: i.level for i in report.items}
    assert levels["job1"] == "warn"
    assert levels["job2"] == "ok"


def test_critical_threshold_overrides_warn():
    results = [_r("job1", 3.0)]
    report = level_results(results, warn_above=1.0, critical_above=2.0)
    assert report.items[0].level == "critical"
    assert report.critical_count == 1


def test_failed_job_gets_critical_by_default():
    results = [_r("job1", success=False)]
    report = level_results(results)
    assert report.items[0].level == "critical"
    assert "failed" in report.items[0].reason


def test_failed_job_custom_failure_level():
    results = [_r("job1", success=False)]
    report = level_results(results, failure_level="warn")
    assert report.items[0].level == "warn"


def test_per_job_override_takes_precedence():
    results = [_r("job1", 2.0), _r("job2", 2.0)]
    report = level_results(
        results,
        warn_above=3.0,
        per_job={"job1": {"warn_above": 1.0}},
    )
    levels = {i.result.job_id: i.level for i in report.items}
    assert levels["job1"] == "warn"
    assert levels["job2"] == "ok"


def test_none_duration_is_ok():
    results = [_r("job1", None)]
    report = level_results(results, warn_above=0.1, critical_above=0.5)
    assert report.items[0].level == "ok"


def test_to_dict_structure():
    results = [_r("j1", 0.5), _r("j2", 2.0), _r("j3", success=False)]
    report = level_results(results, warn_above=1.0, critical_above=1.5)
    d = report.to_dict()
    assert d["total"] == 3
    assert "ok" in d and "warn" in d and "critical" in d
    assert isinstance(d["items"], list)


def test_format_text_empty():
    report = level_results([])
    out = format_level(report, fmt="text")
    assert "No results" in out


def test_format_text_contains_level():
    results = [_r("myjob", 3.0)]
    report = level_results(results, warn_above=1.0)
    out = format_level(report, fmt="text")
    assert "myjob" in out
    assert "warn" in out


def test_format_json_is_valid():
    results = [_r("j1", 0.2), _r("j2", 5.0)]
    report = level_results(results, critical_above=3.0)
    out = format_level(report, fmt="json")
    data = json.loads(out)
    assert data["total"] == 2


def test_format_csv_has_header():
    results = [_r("j1", 1.0)]
    report = level_results(results)
    out = format_level_csv(report)
    assert out.startswith("job_id,duration,success,level,reason")
    assert "j1" in out
