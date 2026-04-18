import pytest
from batchmark.timer import TimingResult
from batchmark.comparator import compare, ComparisonReport, JobComparison


def _r(job_id: str, duration: float, success: bool = True) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success, error=None)


def test_compare_single_job_improvement():
    baseline = [_r("job1", 2.0), _r("job1", 2.0)]
    candidate = [_r("job1", 1.0), _r("job1", 1.0)]
    report = compare(baseline, candidate)
    assert len(report.comparisons) == 1
    c = report.comparisons[0]
    assert c.job_id == "job1"
    assert c.baseline_avg == pytest.approx(2.0)
    assert c.candidate_avg == pytest.approx(1.0)
    assert c.delta == pytest.approx(-1.0)
    assert c.improved is True


def test_compare_regression():
    baseline = [_r("job1", 1.0)]
    candidate = [_r("job1", 3.0)]
    report = compare(baseline, candidate)
    c = report.comparisons[0]
    assert c.delta == pytest.approx(2.0)
    assert c.improved is False
    assert c.pct_change == pytest.approx(200.0)


def test_compare_missing_in_candidate():
    baseline = [_r("job1", 1.0)]
    candidate = [_r("job2", 2.0)]
    report = compare(baseline, candidate)
    ids = {c.job_id: c for c in report.comparisons}
    assert ids["job1"].candidate_avg is None
    assert ids["job1"].delta is None
    assert ids["job2"].baseline_avg is None


def test_compare_empty_both():
    report = compare([], [])
    assert report.comparisons == []


def test_compare_multiple_jobs():
    baseline = [_r("a", 1.0), _r("b", 4.0)]
    candidate = [_r("a", 0.5), _r("b", 5.0)]
    report = compare(baseline, candidate)
    assert len(report.comparisons) == 2


def test_to_dict_structure():
    baseline = [_r("job1", 2.0)]
    candidate = [_r("job1", 1.0)]
    d = compare(baseline, candidate).to_dict()
    assert "comparisons" in d
    assert d["comparisons"][0]["job_id"] == "job1"
    assert "pct_change" in d["comparisons"][0]
