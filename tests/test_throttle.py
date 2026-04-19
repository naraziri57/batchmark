"""Tests for throttle module."""
import json
from unittest.mock import patch

import pytest

from batchmark.throttle import ThrottleConfig, ThrottleReport, apply_throttle, _required_gap
from batchmark.throttle_formatter import format_throttle_text, format_throttle_json, format_throttle
from batchmark.timer import TimingResult


def _r(job_id="job1", duration=1.0, success=True):
    return TimingResult(job_id=job_id, duration=duration, success=success, error=None)


def test_required_gap_min_gap_only():
    cfg = ThrottleConfig(min_gap_seconds=0.5)
    assert _required_gap(cfg) == 0.5


def test_required_gap_max_per_second():
    cfg = ThrottleConfig(max_per_second=2.0)
    assert _required_gap(cfg) == pytest.approx(0.5)


def test_required_gap_takes_max():
    cfg = ThrottleConfig(max_per_second=2.0, min_gap_seconds=0.7)
    assert _required_gap(cfg) == pytest.approx(0.7)


def test_empty_results_returns_empty_report():
    cfg = ThrottleConfig(min_gap_seconds=0.1)
    report = apply_throttle([], cfg)
    assert report.total_jobs == 0
    assert report.total_wait_seconds == 0.0
    assert report.waits == []


def test_single_result_no_wait():
    cfg = ThrottleConfig(min_gap_seconds=0.1)
    report = apply_throttle([_r()], cfg)
    assert report.total_jobs == 1
    assert report.waits == []


def test_no_gap_no_sleep_called():
    cfg = ThrottleConfig()
    results = [_r("a"), _r("b"), _r("c")]
    sleeps = []
    report = apply_throttle(results, cfg, _sleep=sleeps.append)
    assert sleeps == []
    assert report.total_wait_seconds == 0.0


def test_gap_triggers_sleep_when_needed():
    cfg = ThrottleConfig(min_gap_seconds=1.0)
    results = [_r("a"), _r("b")]
    sleeps = []
    # monotonic will say very little time passed, so sleep should be called
    with patch("batchmark.throttle.time.monotonic", side_effect=[0.0, 0.01, 0.01]):
        report = apply_throttle(results, cfg, _sleep=sleeps.append)
    assert len(sleeps) == 1
    assert sleeps[0] > 0


def test_to_dict_keys():
    report = ThrottleReport(
        config=ThrottleConfig(min_gap_seconds=0.1),
        total_jobs=3,
        total_wait_seconds=0.2,
        waits=[0.1, 0.1],
    )
    d = report.to_dict()
    assert "total_jobs" in d
    assert "total_wait_seconds" in d
    assert "avg_wait_seconds" in d
    assert "waits" in d


def test_format_text_empty():
    report = ThrottleReport(config=ThrottleConfig(), total_jobs=0, total_wait_seconds=0.0)
    out = format_throttle_text(report)
    assert "no jobs" in out


def test_format_text_shows_stats():
    report = ThrottleReport(
        config=ThrottleConfig(max_per_second=5.0),
        total_jobs=4,
        total_wait_seconds=0.6,
        waits=[0.2, 0.2, 0.2],
    )
    out = format_throttle_text(report)
    assert "4" in out
    assert "0.6" in out


def test_format_json_valid():
    report = ThrottleReport(
        config=ThrottleConfig(),
        total_jobs=2,
        total_wait_seconds=0.0,
        waits=[0.0],
    )
    out = format_throttle_json(report)
    data = json.loads(out)
    assert data["total_jobs"] == 2


def test_format_dispatch():
    report = ThrottleReport(config=ThrottleConfig(), total_jobs=0, total_wait_seconds=0.0)
    assert format_throttle(report, "json") == format_throttle_json(report)
    assert format_throttle(report, "text") == format_throttle_text(report)
