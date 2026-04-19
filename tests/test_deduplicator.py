import pytest
from batchmark.timer import TimingResult
from batchmark.deduplicator import deduplicate, dedup_stats


def _r(job_id: str, duration=1.0, success=True) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success, error=None)


def test_no_duplicates_returns_all():
    results = [_r("a"), _r("b"), _r("c")]
    out = deduplicate(results)
    assert [r.job_id for r in out] == ["a", "b", "c"]


def test_empty_returns_empty():
    assert deduplicate([]) == []


def test_strategy_latest_keeps_last():
    results = [_r("a", duration=5.0), _r("b"), _r("a", duration=1.0)]
    out = deduplicate(results, strategy="latest")
    assert len(out) == 2
    a = next(r for r in out if r.job_id == "a")
    assert a.duration == 1.0


def test_strategy_first_keeps_first():
    results = [_r("a", duration=5.0), _r("b"), _r("a", duration=1.0)]
    out = deduplicate(results, strategy="first")
    assert len(out) == 2
    a = next(r for r in out if r.job_id == "a")
    assert a.duration == 5.0


def test_strategy_fastest_keeps_lowest_duration():
    results = [_r("a", duration=3.0), _r("a", duration=1.0), _r("a", duration=2.0)]
    out = deduplicate(results, strategy="fastest")
    assert len(out) == 1
    assert out[0].duration == 1.0


def test_strategy_fastest_none_duration_treated_as_slow():
    results = [_r("a", duration=None), _r("a", duration=2.0)]
    out = deduplicate(results, strategy="fastest")
    assert out[0].duration == 2.0


def test_strategy_fastest_both_none_keeps_first():
    results = [_r("a", duration=None), _r("a", duration=None)]
    out = deduplicate(results, strategy="fastest")
    assert len(out) == 1


def test_invalid_strategy_raises():
    with pytest.raises(ValueError, match="Unknown deduplication strategy"):
        deduplicate([_r("a")], strategy="random")  # type: ignore


def test_order_preserved_for_latest():
    results = [_r("b"), _r("a"), _r("c"), _r("a", duration=0.5)]
    out = deduplicate(results, strategy="latest")
    assert [r.job_id for r in out] == ["b", "a", "c"]


def test_dedup_stats_counts():
    original = [_r("a"), _r("b"), _r("a")]
    deduped = deduplicate(original)
    stats = dedup_stats(original, deduped)
    assert stats["original_count"] == 3
    assert stats["deduped_count"] == 2
    assert stats["removed_count"] == 1
