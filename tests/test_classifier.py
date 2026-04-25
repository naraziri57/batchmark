"""Tests for batchmark.classifier."""
from __future__ import annotations

import pytest

from batchmark.classifier import (
    ClassificationReport,
    classify_results,
    classifier_from_map,
)
from batchmark.timer import TimingResult


def _r(job_id: str, success: bool = True, duration: float | None = 1.0) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success)


def test_empty_results_returns_empty_report():
    report = classify_results([], [])
    assert report.classified == []
    assert report.category_counts() == {}


def test_no_classifiers_all_go_to_default():
    results = [_r("job-a"), _r("job-b")]
    report = classify_results(results, [], default_category="misc")
    assert all(cr.category == "misc" for cr in report.classified)


def test_first_matching_classifier_wins():
    results = [_r("fast-job")]
    classifiers = [
        ("fast", lambda r: r.duration is not None and r.duration < 0.5),
        ("slow", lambda r: True),
    ]
    report = classify_results(results, classifiers)
    assert report.classified[0].category == "slow"  # duration=1.0, not < 0.5


def test_classifier_matches_correctly():
    results = [_r("quick", duration=0.1)]
    classifiers = [
        ("fast", lambda r: r.duration is not None and r.duration < 0.5),
        ("slow", lambda r: True),
    ]
    report = classify_results(results, classifiers)
    assert report.classified[0].category == "fast"


def test_by_category_groups_correctly():
    results = [_r("a", duration=0.1), _r("b", duration=2.0), _r("c", duration=0.2)]
    classifiers = [("fast", lambda r: r.duration is not None and r.duration < 1.0)]
    report = classify_results(results, classifiers, default_category="slow")
    groups = report.by_category()
    assert len(groups["fast"]) == 2
    assert len(groups["slow"]) == 1


def test_category_counts():
    results = [_r("a"), _r("b"), _r("c")]
    classifiers = [("all", lambda r: True)]
    report = classify_results(results, classifiers)
    assert report.category_counts() == {"all": 3}


def test_classifier_from_map_prefix_match():
    category_map = {"etl": ["etl-"], "api": ["api-"]}
    classifiers = classifier_from_map(category_map)
    results = [_r("etl-load"), _r("api-fetch"), _r("other-job")]
    report = classify_results(results, classifiers, default_category="misc")
    groups = report.by_category()
    assert any(cr.result.job_id == "etl-load" and cr.category == "etl" for cr in report.classified)
    assert any(cr.result.job_id == "api-fetch" and cr.category == "api" for cr in report.classified)
    assert any(cr.result.job_id == "other-job" and cr.category == "misc" for cr in report.classified)


def test_to_dict_contains_category_counts():
    results = [_r("job-1")]
    report = classify_results(results, [], default_category="default")
    d = report.to_dict()
    assert "classified" in d
    assert "category_counts" in d
    assert d["category_counts"]["default"] == 1


def test_classified_result_to_dict_has_category():
    results = [_r("job-x")]
    report = classify_results(results, [], default_category="generic")
    d = report.classified[0].to_dict()
    assert d["category"] == "generic"
    assert d["job_id"] == "job-x"
