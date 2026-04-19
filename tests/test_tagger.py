import pytest
from batchmark.timer import TimingResult
from batchmark.tagger import (
    TaggedResult,
    tag_results,
    tagger_from_map,
    tagger_static,
    filter_by_tag,
)


def _r(job_id: str, duration: float = 1.0, success: bool = True) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success)


def test_tag_results_empty():
    assert tag_results([], []) == []


def test_tag_results_no_taggers():
    results = [_r("a"), _r("b")]
    tagged = tag_results(results, [])
    assert len(tagged) == 2
    assert all(t.tags == {} for t in tagged)


def test_static_tagger_applies_to_all():
    results = [_r("a"), _r("b")]
    tagged = tag_results(results, [tagger_static({"env": "prod"})])
    assert all(t.tags["env"] == "prod" for t in tagged)


def test_map_tagger_sets_value():
    results = [_r("job1"), _r("job2"), _r("job3")]
    tagger = tagger_from_map("team", {"job1": "alpha", "job2": "beta"})
    tagged = tag_results(results, [tagger])
    assert tagged[0].tags["team"] == "alpha"
    assert tagged[1].tags["team"] == "beta"
    assert tagged[2].tags["team"] is None


def test_multiple_taggers_merge():
    results = [_r("x")]
    tagged = tag_results(
        results,
        [tagger_static({"env": "dev"}), tagger_from_map("owner", {"x": "alice"})],
    )
    assert tagged[0].tags == {"env": "dev", "owner": "alice"}


def test_later_tagger_overwrites_earlier():
    results = [_r("x")]
    tagged = tag_results(
        results,
        [tagger_static({"env": "dev"}), tagger_static({"env": "prod"})],
    )
    assert tagged[0].tags["env"] == "prod"


def test_filter_by_tag():
    results = [_r("a"), _r("b"), _r("c")]
    tagger = tagger_from_map("team", {"a": "alpha", "b": "alpha", "c": "beta"})
    tagged = tag_results(results, [tagger])
    filtered = filter_by_tag(tagged, "team", "alpha")
    assert len(filtered) == 2
    assert all(t.tags["team"] == "alpha" for t in filtered)


def test_filter_by_tag_no_match():
    results = [_r("a")]
    tagged = tag_results(results, [tagger_static({"env": "dev"})])
    assert filter_by_tag(tagged, "env", "prod") == []


def test_to_dict_includes_tags():
    r = _r("myjob", duration=2.5)
    tr = TaggedResult(result=r, tags={"env": "test"})
    d = tr.to_dict()
    assert d["job_id"] == "myjob"
    assert d["duration"] == 2.5
    assert d["tags"] == {"env": "test"}
