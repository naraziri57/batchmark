import json
import pytest
from batchmark.timer import TimingResult
from batchmark.streaker import detect_streaks, Streak
from batchmark.streaker_formatter import format_streaker_text, format_streaker_json, format_streaker


def _r(job_id: str, success: bool, duration: float = 1.0) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success)


def test_empty_returns_empty_report():
    report = detect_streaks([])
    assert report.streaks == []
    assert report.longest() is None


def test_single_result_streak_length_one():
    report = detect_streaks([_r("job1", True)])
    assert len(report.streaks) == 1
    assert report.streaks[0].length == 1
    assert report.streaks[0].status == "success"


def test_consecutive_successes_merged():
    results = [_r("job1", True), _r("job1", True), _r("job1", True)]
    report = detect_streaks(results)
    assert len(report.streaks) == 1
    assert report.streaks[0].length == 3


def test_alternating_creates_multiple_streaks():
    results = [_r("job1", True), _r("job1", False), _r("job1", True)]
    report = detect_streaks(results)
    assert len(report.streaks) == 3


def test_multiple_jobs_tracked_separately():
    results = [_r("a", True), _r("b", False), _r("a", True)]
    report = detect_streaks(results)
    job_ids = [s.job_id for s in report.streaks]
    assert "a" in job_ids
    assert "b" in job_ids


def test_longest_picks_max_length():
    results = [
        _r("job1", True), _r("job1", True),
        _r("job2", False),
    ]
    report = detect_streaks(results)
    longest = report.longest()
    assert longest.job_id == "job1"
    assert longest.length == 2


def test_to_dict_structure():
    results = [_r("job1", True), _r("job1", True)]
    d = detect_streaks(results).to_dict()
    assert "streaks" in d
    assert "longest" in d
    assert d["longest"]["length"] == 2


def test_format_text_empty():
    report = detect_streaks([])
    out = format_streaker_text(report)
    assert "No streaks" in out


def test_format_text_contains_job_id():
    report = detect_streaks([_r("myjob", True), _r("myjob", True)])
    out = format_streaker_text(report)
    assert "myjob" in out
    assert "2x success" in out


def test_format_json_valid():
    report = detect_streaks([_r("j", False)])
    out = format_streaker_json(report)
    data = json.loads(out)
    assert "streaks" in data


def test_format_dispatcher():
    report = detect_streaks([_r("j", True)])
    assert format_streaker(report, "json") == format_streaker_json(report)
    assert format_streaker(report, "text") == format_streaker_text(report)
