import json
import pytest
from batchmark.timer import TimingResult
from batchmark.heatmap import (
    build_heatmap,
    format_heatmap_text,
    format_heatmap_json,
    format_heatmap,
    _bucket,
)


def _r(job_id, duration, success=True):
    return TimingResult(job_id=job_id, duration=duration, success=success, error=None)


def test_bucket_cold():
    assert _bucket(1.0, 2.0, 4.0) == "cold"


def test_bucket_warm():
    assert _bucket(3.0, 2.0, 4.0) == "warm"


def test_bucket_hot():
    assert _bucket(5.0, 2.0, 4.0) == "hot"


def test_bucket_none():
    assert _bucket(None, 2.0, 4.0) == "none"


def test_build_heatmap_empty():
    cells = build_heatmap([])
    assert cells == []


def test_build_heatmap_single_run():
    run = [_r("job-a", 1.0), _r("job-b", 5.0)]
    cells = build_heatmap([run])
    assert len(cells) == 2
    job_ids = {c.job_id for c in cells}
    assert job_ids == {"job-a", "job-b"}


def test_build_heatmap_assigns_buckets():
    run1 = [_r("a", 1.0), _r("b", 5.0), _r("c", 10.0)]
    run2 = [_r("a", 1.5), _r("b", 5.5), _r("c", 9.0)]
    cells = build_heatmap([run1, run2])
    buckets = {c.bucket for c in cells}
    assert buckets <= {"cold", "warm", "hot", "none"}


def test_build_heatmap_none_duration():
    run = [_r("a", None, success=False)]
    cells = build_heatmap([run])
    assert cells[0].bucket == "none"


def test_format_text_empty():
    result = format_heatmap_text([])
    assert result == "(no data)"


def test_format_text_contains_job_id():
    run = [_r("job-x", 2.0)]
    cells = build_heatmap([run])
    text = format_heatmap_text(cells)
    assert "job-x" in text


def test_format_text_contains_legend():
    run = [_r("job-x", 2.0)]
    cells = build_heatmap([run])
    text = format_heatmap_text(cells)
    assert "legend" in text


def test_format_json_valid():
    run = [_r("job-a", 3.0), _r("job-b", 7.0)]
    cells = build_heatmap([run])
    data = json.loads(format_heatmap_json(cells))
    assert isinstance(data, list)
    assert data[0]["job_id"] in {"job-a", "job-b"}


def test_format_dispatch_json():
    run = [_r("j", 1.0)]
    cells = build_heatmap([run])
    out = format_heatmap(cells, fmt="json")
    json.loads(out)  # should not raise


def test_format_dispatch_text():
    run = [_r("j", 1.0)]
    cells = build_heatmap([run])
    out = format_heatmap(cells, fmt="text")
    assert "j" in out
