import pytest
from batchmark.timer import TimingResult
from batchmark.normalizer import normalize_by_max, normalize_by_baseline, normalize


def _r(job_id, duration, success=True):
    return TimingResult(job_id=job_id, duration=duration, success=success, error=None)


def test_normalize_by_max_basic():
    results = [_r("a", 2.0), _r("b", 4.0), _r("c", 1.0)]
    out = normalize_by_max(results)
    by_id = {d["job_id"]: d for d in out}
    assert by_id["b"]["normalized"] == pytest.approx(1.0)
    assert by_id["a"]["normalized"] == pytest.approx(0.5)
    assert by_id["c"]["normalized"] == pytest.approx(0.25)


def test_normalize_by_max_none_duration():
    results = [_r("a", None, success=False), _r("b", 4.0)]
    out = normalize_by_max(results)
    by_id = {d["job_id"]: d for d in out}
    assert by_id["a"]["normalized"] is None
    assert by_id["b"]["normalized"] == pytest.approx(1.0)


def test_normalize_by_max_all_none():
    results = [_r("a", None, success=False), _r("b", None, success=False)]
    out = normalize_by_max(results)
    assert all(d["normalized"] is None for d in out)


def test_normalize_by_baseline_basic():
    results = [_r("a", 2.0), _r("b", 4.0)]
    out = normalize_by_baseline(results, baseline=2.0)
    by_id = {d["job_id"]: d for d in out}
    assert by_id["a"]["normalized"] == pytest.approx(1.0)
    assert by_id["b"]["normalized"] == pytest.approx(2.0)


def test_normalize_by_baseline_invalid():
    with pytest.raises(ValueError):
        normalize_by_baseline([_r("a", 1.0)], baseline=0)


def test_normalize_by_baseline_none_duration():
    results = [_r("a", None, success=False)]
    out = normalize_by_baseline(results, baseline=1.0)
    assert out[0]["normalized"] is None


def test_normalize_dispatches_to_baseline():
    results = [_r("a", 3.0)]
    out = normalize(results, baseline=3.0)
    assert out[0]["normalized"] == pytest.approx(1.0)


def test_normalize_dispatches_to_max():
    results = [_r("a", 5.0), _r("b", 10.0)]
    out = normalize(results)
    by_id = {d["job_id"]: d for d in out}
    assert by_id["b"]["normalized"] == pytest.approx(1.0)
    assert by_id["a"]["normalized"] == pytest.approx(0.5)
