import pytest
from batchmark.timer import TimingResult
from batchmark.segmenter import segment_by_window, Segment


def _r(job_id, duration=1.0, success=True, start_time=0.0):
    return TimingResult(job_id=job_id, duration=duration, success=success, start_time=start_time)


def test_empty_returns_empty():
    assert segment_by_window([], window_size=1.0) == []


def test_no_start_time_skipped():
    r = TimingResult(job_id="j", duration=1.0, success=True, start_time=None)
    assert segment_by_window([r], window_size=1.0) == []


def test_single_result_one_segment():
    r = _r("j1", start_time=0.5)
    segs = segment_by_window([r], window_size=1.0)
    assert len(segs) == 1
    assert segs[0].count() == 1


def test_two_windows():
    r1 = _r("j1", start_time=0.0)
    r2 = _r("j2", start_time=1.5)
    segs = segment_by_window([r1, r2], window_size=1.0)
    assert len(segs) == 2
    assert segs[0].count() == 1
    assert segs[1].count() == 1


def test_same_window_grouped():
    r1 = _r("j1", start_time=0.1)
    r2 = _r("j2", start_time=0.8)
    segs = segment_by_window([r1, r2], window_size=1.0)
    assert segs[0].count() == 2


def test_avg_duration():
    r1 = _r("j1", duration=2.0, start_time=0.0)
    r2 = _r("j2", duration=4.0, start_time=0.5)
    segs = segment_by_window([r1, r2], window_size=1.0)
    assert segs[0].avg_duration() == pytest.approx(3.0)


def test_success_count():
    r1 = _r("j1", success=True, start_time=0.0)
    r2 = _r("j2", success=False, start_time=0.3)
    segs = segment_by_window([r1, r2], window_size=1.0)
    assert segs[0].success_count() == 1


def test_to_dict_keys():
    r = _r("j1", start_time=0.0)
    segs = segment_by_window([r], window_size=1.0)
    d = segs[0].to_dict()
    assert set(d.keys()) == {"label", "start", "end", "count", "success_count", "avg_duration"}


def test_origin_shifts_base():
    r = _r("j1", start_time=5.0)
    segs = segment_by_window([r], window_size=1.0, origin=5.0)
    assert segs[0].start == pytest.approx(5.0)
