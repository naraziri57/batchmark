import pytest
from batchmark.timer import TimingResult
from batchmark.budget import check_budget, BudgetViolation, BudgetReport


def _r(job_id, duration, success=True):
    return TimingResult(job_id=job_id, duration=duration, success=success, error=None)


def test_no_budgets_returns_empty():
    results = [_r("job1", 5.0), _r("job2", 10.0)]
    report = check_budget(results)
    assert not report.has_violations
    assert report.violations == []


def test_global_budget_no_violation():
    results = [_r("job1", 2.0), _r("job2", 3.0)]
    report = check_budget(results, global_budget=5.0)
    assert not report.has_violations


def test_global_budget_with_violation():
    results = [_r("job1", 2.0), _r("job2", 8.0)]
    report = check_budget(results, global_budget=5.0)
    assert report.has_violations
    assert len(report.violations) == 1
    assert report.violations[0].job_id == "job2"
    assert report.violations[0].overage == pytest.approx(3.0)


def test_per_job_budget_overrides_global():
    results = [_r("job1", 6.0), _r("job2", 6.0)]
    report = check_budget(results, global_budget=5.0, per_job_budgets={"job1": 10.0})
    assert len(report.violations) == 1
    assert report.violations[0].job_id == "job2"


def test_none_duration_skipped():
    results = [_r("job1", None)]
    report = check_budget(results, global_budget=1.0)
    assert not report.has_violations


def test_to_dict_structure():
    results = [_r("job1", 9.0)]
    report = check_budget(results, global_budget=5.0)
    d = report.to_dict()
    assert d["has_violations"] is True
    assert len(d["violations"]) == 1
    v = d["violations"][0]
    assert v["job_id"] == "job1"
    assert v["budget"] == 5.0
    assert v["overage"] == pytest.approx(4.0)


def test_multiple_violations():
    results = [_r("a", 10.0), _r("b", 20.0), _r("c", 1.0)]
    report = check_budget(results, global_budget=5.0)
    ids = [v.job_id for v in report.violations]
    assert "a" in ids
    assert "b" in ids
    assert "c" not in ids
