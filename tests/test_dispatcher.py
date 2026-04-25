"""Tests for batchmark.dispatcher and batchmark.dispatcher_formatter."""
import json
import pytest
from batchmark.timer import TimingResult
from batchmark.dispatcher import (
    dispatch,
    route_by_status,
    route_by_job_prefix,
    DispatchReport,
)
from batchmark.dispatcher_formatter import format_dispatch, format_dispatch_text, format_dispatch_json


def _r(job_id: str, success: bool = True, duration: float = 1.0) -> TimingResult:
    return TimingResult(job_id=job_id, success=success, duration_seconds=duration)


def test_empty_results_returns_empty_report():
    report = dispatch([], routes=[])
    assert report.entries == []
    assert report.route_counts() == {}


def test_no_routes_uses_default():
    results = [_r("job-1"), _r("job-2")]
    report = dispatch(results, routes=[], default_route="unrouted")
    assert all(e.route == "unrouted" for e in report.entries)


def test_route_by_status_success():
    results = [_r("job-1", success=True), _r("job-2", success=False)]
    report = dispatch(results, routes=[route_by_status()])
    routes = {e.result.job_id: e.route for e in report.entries}
    assert routes["job-1"] == "success"
    assert routes["job-2"] == "failure"


def test_route_by_status_custom_labels():
    results = [_r("j", success=False)]
    report = dispatch(results, routes=[route_by_status(success_label="ok", failure_label="err")])
    assert report.entries[0].route == "err"


def test_route_by_job_prefix_matches():
    results = [_r("batch-1"), _r("stream-1")]
    report = dispatch(results, routes=[route_by_job_prefix("batch", "batch_jobs")])
    routes = {e.result.job_id: e.route for e in report.entries}
    assert routes["batch-1"] == "batch_jobs"
    assert routes["stream-1"] == "default"


def test_first_matching_route_wins():
    results = [_r("job-1", success=True)]
    report = dispatch(
        results,
        routes=[
            route_by_job_prefix("job", "prefix_match"),
            route_by_status(success_label="status_match"),
        ],
    )
    assert report.entries[0].route == "prefix_match"


def test_route_counts_correct():
    results = [_r("a", True), _r("b", True), _r("c", False)]
    report = dispatch(results, routes=[route_by_status()])
    counts = report.route_counts()
    assert counts["success"] == 2
    assert counts["failure"] == 1


def test_to_dict_structure():
    results = [_r("job-1")]
    report = dispatch(results, routes=[route_by_status()], default_route="default")
    d = report.to_dict()
    assert "entries" in d
    assert "route_counts" in d
    assert "default_route" in d


def test_format_text_empty():
    report = DispatchReport()
    out = format_dispatch_text(report)
    assert "No dispatched" in out


def test_format_text_contains_route():
    results = [_r("job-1", success=True)]
    report = dispatch(results, routes=[route_by_status()])
    out = format_dispatch_text(report)
    assert "success" in out
    assert "job-1" in out


def test_format_json_is_valid():
    results = [_r("job-1"), _r("job-2", success=False)]
    report = dispatch(results, routes=[route_by_status()])
    out = format_dispatch_json(report)
    data = json.loads(out)
    assert "entries" in data
    assert len(data["entries"]) == 2


def test_format_dispatch_delegates_by_fmt():
    report = DispatchReport()
    assert format_dispatch(report, fmt="text") == format_dispatch_text(report)
    results = [_r("x")]
    r2 = dispatch(results, routes=[])
    assert format_dispatch(r2, fmt="json") == format_dispatch_json(r2)
