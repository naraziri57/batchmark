"""Tests for batchmark.binner and batchmark.binner_formatter."""
import json
import pytest
from batchmark.timer import TimingResult
from batchmark.binner import bin_results, Bin, BinReport
from batchmark.binner_formatter import format_bin_text, format_bin_json, format_bin


def _r(job_id: str, duration: float | None, success: bool = True) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success)


def test_empty_returns_empty_report():
    report = bin_results([])
    assert report.bins == []
    assert report.total == 0


def test_all_none_duration_returns_empty_report():
    results = [_r("a", None), _r("b", None)]
    report = bin_results(results)
    assert report.bins == []


def test_single_result_lands_in_first_bin():
    results = [_r("a", 0.2)]
    report = bin_results(results, bin_width=0.5)
    assert report.total == 1
    assert report.bins[0].count == 1


def test_two_results_in_different_bins():
    results = [_r("a", 0.1), _r("b", 0.9)]
    report = bin_results(results, bin_width=0.5)
    counts = [b.count for b in report.bins]
    assert counts[0] == 1
    assert counts[1] == 1


def test_bin_width_respected():
    results = [_r(f"j{i}", float(i) * 0.1) for i in range(10)]
    report = bin_results(results, bin_width=1.0)
    assert len(report.bins) >= 1
    assert report.total == 10


def test_success_count_correct():
    results = [_r("a", 0.3, success=True), _r("b", 0.4, success=False)]
    report = bin_results(results, bin_width=1.0)
    assert report.bins[0].success_count == 1
    assert report.bins[0].count == 2


def test_avg_duration_in_bin():
    results = [_r("a", 0.2), _r("b", 0.4)]
    report = bin_results(results, bin_width=1.0)
    assert abs(report.bins[0].avg_duration - 0.3) < 1e-9


def test_to_dict_structure():
    results = [_r("a", 0.5)]
    report = bin_results(results, bin_width=1.0)
    d = report.to_dict()
    assert "bins" in d
    assert "bin_width" in d
    assert "total" in d
    assert "label" in d["bins"][0]


def test_format_text_empty():
    report = BinReport(bins=[], bin_width=0.5)
    out = format_bin_text(report)
    assert "No binned" in out


def test_format_text_contains_bin_label():
    results = [_r("a", 0.2)]
    report = bin_results(results, bin_width=0.5)
    out = format_bin_text(report)
    assert "0.00" in out


def test_format_json_is_valid():
    results = [_r("a", 0.2), _r("b", 0.7)]
    report = bin_results(results, bin_width=0.5)
    out = format_bin_json(report)
    data = json.loads(out)
    assert "bins" in data


def test_format_dispatch_text():
    results = [_r("a", 0.1)]
    report = bin_results(results, bin_width=0.5)
    assert format_bin(report, fmt="text") == format_bin_text(report)


def test_format_dispatch_json():
    results = [_r("a", 0.1)]
    report = bin_results(results, bin_width=0.5)
    assert format_bin(report, fmt="json") == format_bin_json(report)
