import json
import pytest
from batchmark.timer import TimingResult
from batchmark.differ import diff_results
from batchmark.differ_formatter import format_diff_text, format_diff_json, format_diff


def _r(job_id: str, duration: float = 1.0) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=True, error=None)


def test_text_empty():
    report = diff_results([], [])
    out = format_diff_text(report)
    assert "No differences" in out


def test_text_shows_added():
    report = diff_results([], [_r("new_job", 1.5)])
    out = format_diff_text(report)
    assert "[+]" in out
    assert "new_job" in out


def test_text_shows_removed():
    report = diff_results([_r("old_job", 1.0)], [])
    out = format_diff_text(report)
    assert "[-]" in out
    assert "old_job" in out


def test_text_shows_changed_with_arrow():
    report = diff_results([_r("j", 1.0)], [_r("j", 3.0)])
    out = format_diff_text(report)
    assert "[~]" in out
    assert "↑" in out


def test_text_summary_line():
    report = diff_results([_r("a", 1.0)], [_r("b", 2.0)])
    out = format_diff_text(report)
    assert "Summary" in out


def test_json_is_valid():
    report = diff_results([_r("x", 1.0)], [_r("x", 2.0), _r("y", 3.0)])
    out = format_diff_json(report)
    data = json.loads(out)
    assert "entries" in data


def test_format_dispatch_text():
    report = diff_results([], [])
    assert format_diff(report, "text") == format_diff_text(report)


def test_format_dispatch_json():
    report = diff_results([], [])
    assert format_diff(report, "json") == format_diff_json(report)
