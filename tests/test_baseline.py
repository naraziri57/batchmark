"""Tests for batchmark.baseline save/load/list functionality."""

import os
import pytest

from batchmark.baseline import save_baseline, load_baseline, list_baselines
from batchmark.timer import TimingResult


def _r(job_id, duration=1.0, success=True, error=None):
    return TimingResult(job_id=job_id, duration=duration, success=success, error=error)


def test_save_and_load_roundtrip(tmp_path):
    results = [_r("job-1", 1.5), _r("job-2", 2.0)]
    path = save_baseline("run1", results, directory=str(tmp_path))
    assert os.path.exists(path)
    loaded = load_baseline("run1", directory=str(tmp_path))
    assert len(loaded) == 2
    assert loaded[0].job_id == "job-1"
    assert loaded[0].duration == pytest.approx(1.5)
    assert loaded[1].job_id == "job-2"


def test_load_preserves_failure(tmp_path):
    results = [_r("job-fail", duration=None, success=False, error="timeout")]
    save_baseline("failures", results, directory=str(tmp_path))
    loaded = load_baseline("failures", directory=str(tmp_path))
    assert loaded[0].success is False
    assert loaded[0].error == "timeout"
    assert loaded[0].duration is None


def test_load_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError, match="Baseline 'ghost' not found"):
        load_baseline("ghost", directory=str(tmp_path))


def test_list_baselines_empty(tmp_path):
    names = list_baselines(directory=str(tmp_path))
    assert names == []


def test_list_baselines_nonexistent_dir(tmp_path):
    names = list_baselines(directory=str(tmp_path / "no_such_dir"))
    assert names == []


def test_list_baselines_multiple(tmp_path):
    save_baseline("alpha", [_r("j1")], directory=str(tmp_path))
    save_baseline("beta", [_r("j2")], directory=str(tmp_path))
    names = sorted(list_baselines(directory=str(tmp_path)))
    assert names == ["alpha", "beta"]


def test_save_returns_correct_path(tmp_path):
    results = [_r("j1")]
    path = save_baseline("myrun", results, directory=str(tmp_path))
    assert path.endswith("myrun.json")
