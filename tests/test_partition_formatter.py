"""Tests for batchmark.partition_formatter."""
from __future__ import annotations

import json

from batchmark.timer import TimingResult
from batchmark.partitioner import partition_results
from batchmark.partition_formatter import (
    format_partition_text,
    format_partition_json,
    format_partition_csv,
    format_partition,
)


def _r(job_id: str, success: bool = True, duration: float = 1.0) -> TimingResult:
    return TimingResult(job_id=job_id, success=success, duration=duration)


def _report(results, key_fn=None):
    if key_fn is None:
        key_fn = lambda r: "ok" if r.success else "fail"
    return partition_results(results, key_fn=key_fn)


def test_text_empty():
    report = _report([])
    out = format_partition_text(report)
    assert out == "No partitions."


def test_text_contains_label():
    report = _report([_r("a", True, 2.0), _r("b", True, 4.0)])
    out = format_partition_text(report)
    assert "[ok]" in out


def test_text_shows_counts():
    results = [_r("a", True), _r("b", False), _r("c", False)]
    report = _report(results)
    out = format_partition_text(report)
    assert "ok=1" in out or "ok=2" in out  # depends on partition
    assert "fail" in out


def test_json_is_valid():
    results = [_r("a", True, 1.5), _r("b", False, 0.5)]
    report = _report(results)
    out = format_partition_json(report)
    parsed = json.loads(out)
    assert "partitions" in parsed
    assert len(parsed["partitions"]) == 2


def test_csv_header_present():
    report = _report([_r("a", True)])
    out = format_partition_csv(report)
    assert out.startswith("label,count,success,failure,avg_duration,median_duration")


def test_csv_row_values():
    report = _report([_r("a", True, 3.0)])
    lines = format_partition_csv(report).splitlines()
    data_line = lines[1]
    assert "ok" in data_line
    assert "3." in data_line


def test_format_dispatch_json():
    report = _report([_r("a", True)])
    out = format_partition(report, fmt="json")
    assert out.startswith("{")


def test_format_dispatch_csv():
    report = _report([_r("a", True)])
    out = format_partition(report, fmt="csv")
    assert "label" in out


def test_format_dispatch_default_text():
    report = _report([])
    out = format_partition(report)
    assert out == "No partitions."
