"""Tests for batchmark.cutter."""
import pytest
from batchmark.timer import TimingResult
from batchmark.cutter import cut_results, CutReport, Page


def _r(job_id: str, duration: float = 1.0, success: bool = True) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success)


def test_empty_results_returns_one_empty_page():
    report = cut_results([], page_size=5)
    assert report.total == 0
    assert report.page_count == 1
    assert report.pages[0].count == 0


def test_single_result_one_page():
    report = cut_results([_r("job-1")], page_size=5)
    assert report.total == 1
    assert report.page_count == 1
    assert report.pages[0].count == 1


def test_exact_fit_one_page():
    results = [_r(f"job-{i}") for i in range(5)]
    report = cut_results(results, page_size=5)
    assert report.page_count == 1
    assert report.pages[0].count == 5


def test_overflow_creates_second_page():
    results = [_r(f"job-{i}") for i in range(7)]
    report = cut_results(results, page_size=5)
    assert report.page_count == 2
    assert report.pages[0].count == 5
    assert report.pages[1].count == 2


def test_page_size_one_each_result_is_own_page():
    results = [_r(f"job-{i}") for i in range(4)]
    report = cut_results(results, page_size=1)
    assert report.page_count == 4
    for idx, page in enumerate(report.pages):
        assert page.count == 1
        assert page.results[0].job_id == f"job-{idx}"


def test_get_valid_index():
    results = [_r(f"job-{i}") for i in range(6)]
    report = cut_results(results, page_size=3)
    page = report.get(1)
    assert page is not None
    assert page.index == 1
    assert page.count == 3


def test_get_out_of_range_returns_none():
    report = cut_results([_r("j")], page_size=5)
    assert report.get(99) is None
    assert report.get(-1) is None


def test_invalid_page_size_raises():
    with pytest.raises(ValueError):
        cut_results([], page_size=0)


def test_to_dict_structure():
    results = [_r("a", 1.5), _r("b", 2.0, success=False)]
    report = cut_results(results, page_size=10)
    d = report.to_dict()
    assert d["page_size"] == 10
    assert d["total"] == 2
    assert d["page_count"] == 1
    first_page = d["pages"][0]
    assert first_page["page"] == 0
    assert first_page["count"] == 2
    assert first_page["results"][0]["job_id"] == "a"


def test_page_indices_are_sequential():
    results = [_r(f"job-{i}") for i in range(15)]
    report = cut_results(results, page_size=4)
    for i, page in enumerate(report.pages):
        assert page.index == i
