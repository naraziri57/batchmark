import json
from batchmark.timer import TimingResult
from batchmark.segmenter import segment_by_window
from batchmark.segmenter_formatter import format_segment_text, format_segment_json, format_segment


def _r(job_id, duration=1.0, success=True, start_time=0.0):
    return TimingResult(job_id=job_id, duration=duration, success=success, start_time=start_time)


def test_text_empty():
    out = format_segment_text([])
    assert "No segments" in out


def test_text_contains_label():
    r = _r("j1", start_time=0.0)
    segs = segment_by_window([r], window_size=1.0)
    out = format_segment_text(segs)
    assert "0.00-1.00" in out


def test_text_shows_count():
    r1 = _r("j1", start_time=0.1)
    r2 = _r("j2", start_time=0.5)
    segs = segment_by_window([r1, r2], window_size=1.0)
    out = format_segment_text(segs)
    assert "count=2" in out


def test_json_is_valid():
    r = _r("j1", start_time=0.0)
    segs = segment_by_window([r], window_size=1.0)
    out = format_segment_json(segs)
    data = json.loads(out)
    assert isinstance(data, list)
    assert data[0]["count"] == 1


def test_format_dispatch_text():
    out = format_segment([], fmt="text")
    assert "No segments" in out


def test_format_dispatch_json():
    out = format_segment([], fmt="json")
    assert json.loads(out) == []
