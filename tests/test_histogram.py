"""Tests for batchmark.histogram."""
import json
import pytest
from batchmark.timer import TimingResult
from batchmark.histogram import (
    build_histogram,
    format_histogram_text,
    format_histogram_json,
    format_histogram,
)


def _r(job_id: str, duration: float | None, success: bool = True) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success)


def test_empty_returns_empty():
    assert build_histogram([]) == []


def test_all_none_duration_returns_empty():
    results = [_r("a", None), _r("b", None)]
    assert build_histogram(results) == []


def test_bucket_count_equals_num_buckets():
    results = [_r(str(i), float(i)) for i in range(10)]
    buckets = build_histogram(results, num_buckets=5)
    assert len(buckets) == 5


def test_all_counts_sum_to_total():
    results = [_r(str(i), float(i)) for i in range(20)]
    buckets = build_histogram(results, num_buckets=4)
    assert sum(b.count for b in buckets) == 20


def test_single_value_no_crash():
    results = [_r("only", 3.14)]
    buckets = build_histogram(results, num_buckets=3)
    assert sum(b.count for b in buckets) == 1


def test_job_ids_tracked():
    results = [_r("fast", 1.0), _r("slow", 100.0)]
    buckets = build_histogram(results, num_buckets=2)
    all_ids = [jid for b in buckets for jid in b.job_ids]
    assert sorted(all_ids) == ["fast", "slow"]


def test_format_text_empty():
    out = format_histogram_text([])
    assert "No data" in out


def test_format_text_contains_label():
    results = [_r(str(i), float(i)) for i in range(5)]
    buckets = build_histogram(results, num_buckets=2)
    out = format_histogram_text(buckets)
    assert "Histogram" in out
    assert "|" in out


def test_format_json_valid():
    results = [_r(str(i), float(i)) for i in range(6)]
    buckets = build_histogram(results, num_buckets=3)
    data = json.loads(format_histogram_json(buckets))
    assert isinstance(data, list)
    assert "count" in data[0]
    assert "range" in data[0]


def test_format_dispatch():
    results = [_r("x", 1.0)]
    buckets = build_histogram(results)
    assert format_histogram(buckets, fmt="text") == format_histogram_text(buckets)
    assert format_histogram(buckets, fmt="json") == format_histogram_json(buckets)
