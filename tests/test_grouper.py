import pytest
from batchmark.timer import TimingResult
from batchmark.grouper import (
    group_results,
    group_by_status,
    group_by_prefix,
    GroupReport,
)
from batchmark.grouper_formatter import format_group_text, format_group_json, format_group


def _r(job_id: str, duration: float = 1.0, success: bool = True) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success)


def test_empty_returns_empty_report():
    report = group_results([], key_fn=lambda r: r.job_id)
    assert report.groups == []
    assert report.labels == []


def test_single_result_one_group():
    results = [_r("job_a")]
    report = group_results(results, key_fn=lambda r: r.job_id)
    assert len(report.groups) == 1
    assert report.groups[0].label == "job_a"
    assert report.groups[0].count == 1


def test_multiple_keys_produce_multiple_groups():
    results = [_r("a"), _r("b"), _r("a")]
    report = group_results(results, key_fn=lambda r: r.job_id)
    assert len(report.groups) == 2
    assert report.get("a").count == 2
    assert report.get("b").count == 1


def test_sort_labels_true_returns_alphabetical():
    results = [_r("z"), _r("a"), _r("m")]
    report = group_results(results, key_fn=lambda r: r.job_id, sort_labels=True)
    assert report.labels == ["a", "m", "z"]


def test_sort_labels_false_preserves_insertion_order():
    results = [_r("z"), _r("a"), _r("m")]
    report = group_results(results, key_fn=lambda r: r.job_id, sort_labels=False)
    assert report.labels == ["z", "a", "m"]


def test_group_by_status_splits_correctly():
    results = [_r("j1", success=True), _r("j2", success=False), _r("j3", success=True)]
    report = group_by_status(results)
    success_grp = report.get("success")
    failure_grp = report.get("failure")
    assert success_grp is not None and success_grp.count == 2
    assert failure_grp is not None and failure_grp.count == 1


def test_group_by_prefix_splits_on_separator():
    results = [_r("batch_1"), _r("batch_2"), _r("stream_1")]
    report = group_by_prefix(results, sep="_")
    assert set(report.labels) == {"batch", "stream"}
    assert report.get("batch").count == 2


def test_group_by_prefix_no_separator_uses_full_id():
    results = [_r("jobA"), _r("jobB")]
    report = group_by_prefix(results, sep="_")
    assert set(report.labels) == {"jobA", "jobB"}


def test_success_and_failure_counts_in_group():
    results = [_r("g", success=True), _r("g", success=False), _r("g", success=True)]
    report = group_results(results, key_fn=lambda r: r.job_id)
    grp = report.get("g")
    assert grp.success_count == 2
    assert grp.failure_count == 1


def test_to_dict_contains_expected_keys():
    results = [_r("x", duration=2.0)]
    report = group_results(results, key_fn=lambda r: r.job_id)
    d = report.to_dict()
    assert "groups" in d
    g = d["groups"][0]
    for key in ("label", "count", "success_count", "failure_count", "avg_duration", "median_duration"):
        assert key in g


def test_format_text_empty():
    report = GroupReport(groups=[])
    out = format_group_text(report)
    assert "No groups" in out


def test_format_text_contains_label():
    results = [_r("alpha", duration=1.5)]
    report = group_results(results, key_fn=lambda r: r.job_id)
    out = format_group_text(report)
    assert "alpha" in out


def test_format_json_is_valid():
    import json
    results = [_r("beta", duration=0.5)]
    report = group_results(results, key_fn=lambda r: r.job_id)
    out = format_group_json(report)
    data = json.loads(out)
    assert "groups" in data


def test_format_dispatch_defaults_to_text():
    report = GroupReport(groups=[])
    assert format_group(report, fmt="text") == format_group_text(report)
    assert format_group(report, fmt="json") == format_group_json(report)
