import time
import json
import pytest
from batchmark.timer import JobTimer
from batchmark.report import render_report


def test_basic_timing():
    timer = JobTimer()
    job = timer.start("job_a")
    time.sleep(0.01)
    job.finish()
    assert job.elapsed is not None
    assert job.elapsed >= 0.01
    assert job.success is True


def test_failed_job():
    timer = JobTimer()
    job = timer.start("job_fail")
    job.finish(success=False, error="timeout")
    assert not job.success
    assert job.error == "timeout"


def test_summary_counts():
    timer = JobTimer()
    for i in range(3):
        j = timer.start(f"job_{i}")
        j.finish(success=(i != 1))
    summary = timer.summary()
    assert summary["total_jobs"] == 3
    assert summary["completed"] == 3
    assert summary["failed"] == 1


def test_empty_summary():
    timer = JobTimer()
    summary = timer.summary()
    assert summary["total_elapsed"] == 0.0


def test_render_json():
    timer = JobTimer()
    j = timer.start("parse", metadata={"size": 100})
    j.finish()
    output = render_report(timer, fmt="json")
    data = json.loads(output)
    assert "summary" in data
    assert data["jobs"][0]["name"] == "parse"


def test_render_csv():
    timer = JobTimer()
    j = timer.start("export")
    j.finish()
    output = render_report(timer, fmt="csv")
    assert "name" in output
    assert "export" in output


def test_render_text():
    timer = JobTimer()
    j = timer.start("transform")
    j.finish()
    output = render_report(timer, fmt="text")
    assert "batchmark report" in output
    assert "transform" in output
