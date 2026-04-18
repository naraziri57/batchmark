import json
from batchmark.timer import TimingResult
from batchmark.comparator import compare
from batchmark.comparison_formatter import (
    format_comparison_text,
    format_comparison_json,
    format_comparison,
)


def _r(job_id: str, duration: float) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=True, error=None)


def test_text_empty():
    from batchmark.comparator import ComparisonReport
    out = format_comparison_text(ComparisonReport([]))
    assert "No comparisons" in out


def test_text_contains_job_id():
    report = compare([_r("myjob", 2.0)], [_r("myjob", 1.0)])
    out = format_comparison_text(report)
    assert "myjob" in out
    assert "↓" in out


def test_text_regression_arrow():
    report = compare([_r("job", 1.0)], [3.0)])
    out = format_comparison_text(report)
    assert "↑" in out


def test_json_output_is_valid():
    report =", 1.0)], [_r("j", 2.0)])
    out = format_comparison_json(report)
    data = json.loads(out)
    assert "comparisons" in data
    assert data["comparisons"][0]["job_id"] == "j"


def test_format_dispatch_json():
    report = compare([_r("j", 1.0)], [_r("j", 1.0)])
    out = format_comparison(report, fmt="json")
    json.loads(out)  # should not raise


def test_format_dispatch_text_default():
    report = compare([_r("j", 1.0)], [_r("j", 1.0)])
    out = format_comparison(report)
    assert "Job ID" in out
