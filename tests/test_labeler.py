"""Tests for batchmark.labeler."""

from __future__ import annotations

from batchmark.timer import TimingResult
from batchmark.labeler import (
    LabeledResult,
    label_results,
    labeler_from_map,
    status_labeler,
    duration_tier_labeler,
)


def _r(job_id: str, duration: float | None = 1.0, success: bool = True) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success)


def test_empty_returns_empty():
    assert label_results([], {}) == []


def test_no_labelers_produces_empty_labels():
    results = [_r("job1"), _r("job2")]
    labeled = label_results(results, {})
    assert len(labeled) == 2
    assert all(lr.labels == {} for lr in labeled)


def test_status_labeler_success():
    r = _r("j1", success=True)
    labeled = label_results([r], {"status": status_labeler})
    assert labeled[0].labels["status"] == "ok"


def test_status_labeler_failure():
    r = _r("j1", success=False)
    labeled = label_results([r], {"status": status_labeler})
    assert labeled[0].labels["status"] == "fail"


def test_duration_tier_fast():
    r = _r("j1", duration=0.1)
    fn = duration_tier_labeler(fast_threshold=0.5, slow_threshold=2.0)
    labeled = label_results([r], {"tier": fn})
    assert labeled[0].labels["tier"] == "fast"


def test_duration_tier_medium():
    r = _r("j1", duration=1.0)
    fn = duration_tier_labeler(fast_threshold=0.5, slow_threshold=2.0)
    labeled = label_results([r], {"tier": fn})
    assert labeled[0].labels["tier"] == "medium"


def test_duration_tier_slow():
    r = _r("j1", duration=5.0)
    fn = duration_tier_labeler(fast_threshold=0.5, slow_threshold=2.0)
    labeled = label_results([r], {"tier": fn})
    assert labeled[0].labels["tier"] == "slow"


def test_duration_tier_none_duration_returns_no_label():
    r = _r("j1", duration=None)
    fn = duration_tier_labeler()
    labeled = label_results([r], {"tier": fn})
    assert "tier" not in labeled[0].labels


def test_labeler_from_map_hit():
    r = _r("job-a")
    fn = labeler_from_map("team", {"job-a": "alpha", "job-b": "beta"})
    labeled = label_results([r], {"team": fn})
    assert labeled[0].labels["team"] == "alpha"


def test_labeler_from_map_miss_omits_key():
    r = _r("job-z")
    fn = labeler_from_map("team", {"job-a": "alpha"})
    labeled = label_results([r], {"team": fn})
    assert "team" not in labeled[0].labels


def test_to_dict_includes_labels():
    r = _r("j1", duration=0.3, success=True)
    fn = duration_tier_labeler()
    labeled = label_results([r], {"tier": fn})
    d = labeled[0].to_dict()
    assert "labels" in d
    assert d["labels"]["tier"] == "fast"
    assert d["job_id"] == "j1"


def test_multiple_labelers_combined():
    r = _r("j1", duration=0.2, success=True)
    labeled = label_results(
        [r],
        {
            "status": status_labeler,
            "tier": duration_tier_labeler(),
        },
    )
    assert labeled[0].labels["status"] == "ok"
    assert labeled[0].labels["tier"] == "fast"
