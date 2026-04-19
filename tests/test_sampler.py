import pytest
from batchmark.timer import TimingResult
from batchmark.sampler import sample_results, stratified_sample, SampleReport


def _r(job_id: str, duration: float = 1.0, success: bool = True) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success, error=None)


def test_empty_returns_empty_report():
    report = sample_results([], n=5)
    assert report.total == 0
    assert report.sampled == 0
    assert report.results == []


def test_sample_by_n():
    results = [_r(f"job-{i}") for i in range(10)]
    report = sample_results(results, n=4, seed=42)
    assert report.total == 10
    assert report.sampled == 4
    assert len(report.results) == 4


def test_sample_by_fraction():
    results = [_r(f"job-{i}") for i in range(20)]
    report = sample_results(results, fraction=0.5, seed=0)
    assert report.sampled == 10


def test_n_capped_at_total():
    results = [_r(f"job-{i}") for i in range(3)]
    report = sample_results(results, n=100)
    assert report.sampled == 3


def test_seed_reproducible():
    results = [_r(f"job-{i}") for i in range(20)]
    r1 = sample_results(results, n=5, seed=7)
    r2 = sample_results(results, n=5, seed=7)
    assert [x.job_id for x in r1.results] == [x.job_id for x in r2.results]


def test_no_n_or_fraction_raises():
    with pytest.raises(ValueError, match="Provide either"):
        sample_results([_r("a")], n=None, fraction=None)


def test_invalid_fraction_raises():
    with pytest.raises(ValueError, match="fraction"):
        sample_results([_r("a")], fraction=1.5)


def test_stratified_sample_proportional():
    successes = [_r(f"s{i}", success=True) for i in range(10)]
    failures = [_r(f"f{i}", success=False) for i in range(10)]
    report = stratified_sample(successes + failures, fraction=0.5, seed=1)
    ok = sum(1 for r in report.results if r.success)
    fail = sum(1 for r in report.results if not r.success)
    assert ok >= 1 and fail >= 1


def test_to_dict_structure():
    results = [_r("job-1")]
    report = sample_results(results, n=1)
    d = report.to_dict()
    assert "total" in d and "sampled" in d and "results" in d
    assert isinstance(d["results"], list)
