"""Tests for batchmark.annotator."""
import pytest
from batchmark.timer import TimingResult
from batchmark.annotator import (
    AnnotatedResult,
    annotate,
    tag_by_status,
    tag_by_duration_bucket,
)


def _r(job_id="job1", duration=1.0, success=True) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success, error=None)


def test_annotate_empty_results():
    assert annotate([], [tag_by_status]) == []


def test_annotate_no_annotators():
    results = [_r(), _r("job2")]
    out = annotate(results, [])
    assert len(out) == 2
    for a in out:
        assert a.tags == {}


def test_tag_by_status_success():
    r = _r(success=True)
    assert tag_by_status(r) == {"status": "success"}


def test_tag_by_status_failed():
    r = _r(success=False)
    assert tag_by_status(r) == {"status": "failed"}


def test_annotate_with_status():
    results = [_r("a", success=True), _r("b", success=False)]
    out = annotate(results, [tag_by_status])
    assert out[0].tags["status"] == "success"
    assert out[1].tags["status"] == "failed"


def test_tag_by_duration_bucket_fast():
    fn = tag_by_duration_bucket()
    assert fn(_r(duration=0.5)) == {"bucket": "fast"}


def test_tag_by_duration_bucket_medium():
    fn = tag_by_duration_bucket()
    assert fn(_r(duration=3.0)) == {"bucket": "medium"}


def test_tag_by_duration_bucket_slow():
    fn = tag_by_duration_bucket()
    assert fn(_r(duration=10.0)) == {"bucket": "slow"}


def test_tag_by_duration_bucket_none_duration():
    fn = tag_by_duration_bucket()
    r = TimingResult(job_id="x", duration=None, success=False, error="timeout")
    assert fn(r) == {"bucket": "unknown"}


def test_annotate_multiple_annotators_merge():
    results = [_r("j", duration=0.2, success=True)]
    out = annotate(results, [tag_by_status, tag_by_duration_bucket()])
    assert out[0].tags["status"] == "success"
    assert out[0].tags["bucket"] == "fast"


def test_annotate_later_annotator_wins_on_conflict():
    def always_a(_r):
        return {"status": "A"}

    def always_b(_r):
        return {"status": "B"}

    out = annotate([_r()], [always_a, always_b])
    assert out[0].tags["status"] == "B"


def test_annotated_result_to_dict_includes_tags():
    r = _r("myjob", duration=2.5, success=True)
    ar = AnnotatedResult(result=r, tags={"env": "prod"})
    d = ar.to_dict()
    assert d["job_id"] == "myjob"
    assert d["tags"] == {"env": "prod"}
