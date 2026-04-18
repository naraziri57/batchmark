"""Tests for batchmark.profiler."""
import time
import pytest
from batchmark.profiler import Profiler, ProfileSnapshot, _peak_memory_kb


def test_snapshot_to_dict_keys():
    snap = ProfileSnapshot(job_id="j1", wall_time=1.23, cpu_time=0.5, peak_memory_kb=1024)
    d = snap.to_dict()
    assert set(d.keys()) == {"job_id", "wall_time", "cpu_time", "peak_memory_kb", "extra"}
    assert d["job_id"] == "j1"
    assert d["peak_memory_kb"] == 1024


def test_snapshot_to_dict_rounding():
    snap = ProfileSnapshot(job_id="x", wall_time=1.123456789, cpu_time=0.987654321)
    d = snap.to_dict()
    assert d["wall_time"] == round(1.123456789, 6)
    assert d["cpu_time"] == round(0.987654321, 6)


def test_profiler_measures_wall_time():
    p = Profiler("job-a")
    p.start()
    time.sleep(0.05)
    snap = p.stop()
    assert snap.wall_time >= 0.04
    assert snap.job_id == "job-a"


def test_profiler_stop_before_start_raises():
    p = Profiler("bad")
    with pytest.raises(RuntimeError, match="before start"):
        p.stop()


def test_profiler_context_manager():
    with Profiler("ctx-job") as p:
        time.sleep(0.02)
    snap = p.snapshot
    assert isinstance(snap, ProfileSnapshot)
    assert snap.wall_time >= 0.01
    assert snap.job_id == "ctx-job"


def test_profiler_snapshot_before_exit_raises():
    p = Profiler("early")
    p.start()
    with pytest.raises(RuntimeError, match="not yet exited"):
        _ = p.snapshot


def test_cpu_time_nonnegative():
    with Profiler("cpu-test") as p:
        _ = [i * i for i in range(10000)]
    assert p.snapshot.cpu_time >= 0.0


def test_peak_memory_returns_none_or_int():
    result = _peak_memory_kb()
    assert result is None or isinstance(result, int)
