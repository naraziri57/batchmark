"""Tests for batchmark.clusterizer."""

from __future__ import annotations

from batchmark.timer import TimingResult
from batchmark.clusterizer import clusterize, Cluster, ClusterReport


def _r(job_id: str, duration: float | None, success: bool = True) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success, error=None)


def test_empty_results_returns_empty_clusters():
    report = clusterize([], boundaries=[1.0, 2.0])
    assert isinstance(report, ClusterReport)
    for cluster in report.clusters:
        assert cluster.count == 0


def test_no_boundaries_puts_all_in_one_cluster():
    results = [_r("a", 0.5), _r("b", 1.5), _r("c", 3.0)]
    report = clusterize(results, boundaries=[])
    assert len(report.clusters) == 1
    assert report.clusters[0].count == 3
    assert report.clusters[0].label == "all"


def test_single_boundary_creates_two_clusters():
    results = [_r("a", 0.5), _r("b", 1.5)]
    report = clusterize(results, boundaries=[1.0])
    assert len(report.clusters) == 2
    labels = [c.label for c in report.clusters]
    assert "<1.0s" in labels
    assert ">=1.0s" in labels


def test_results_distributed_correctly():
    results = [
        _r("fast", 0.2),
        _r("mid", 1.5),
        _r("slow", 4.0),
    ]
    report = clusterize(results, boundaries=[1.0, 3.0])
    clusters = {c.label: c for c in report.clusters}
    assert clusters["<1.0s"].count == 1
    assert clusters["<3.0s"].count == 1
    assert clusters[">=3.0s"].count == 1


def test_none_duration_goes_to_first_cluster():
    results = [_r("x", None), _r("y", 2.0)]
    report = clusterize(results, boundaries=[1.0, 3.0])
    first = report.clusters[0]
    assert any(r.job_id == "x" for r in first.results)


def test_success_count_correct():
    results = [
        _r("a", 0.5, success=True),
        _r("b", 0.6, success=False),
    ]
    report = clusterize(results, boundaries=[1.0])
    first = report.clusters[0]
    assert first.success_count == 1
    assert first.count == 2


def test_avg_duration_calculated():
    results = [_r("a", 0.4), _r("b", 0.6)]
    report = clusterize(results, boundaries=[1.0])
    avg = report.clusters[0].avg_duration
    assert avg is not None
    assert abs(avg - 0.5) < 1e-9


def test_avg_duration_none_when_no_durations():
    results = [_r("a", None)]
    report = clusterize(results, boundaries=[1.0])
    assert report.clusters[0].avg_duration is None


def test_to_dict_structure():
    results = [_r("a", 0.3)]
    report = clusterize(results, boundaries=[1.0])
    d = report.to_dict()
    assert "clusters" in d
    cluster_dict = d["clusters"][0]
    for key in ("label", "min_duration", "max_duration", "count", "success_count", "avg_duration"):
        assert key in cluster_dict


def test_boundaries_sorted_automatically():
    results = [_r("a", 0.5), _r("b", 2.0)]
    report_unsorted = clusterize(results, boundaries=[3.0, 1.0])
    report_sorted = clusterize(results, boundaries=[1.0, 3.0])
    labels_unsorted = [c.label for c in report_unsorted.clusters]
    labels_sorted = [c.label for c in report_sorted.clusters]
    assert labels_unsorted == labels_sorted
