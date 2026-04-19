import json
from batchmark.timer import TimingResult
from batchmark.sampler import SampleReport
from batchmark.sampler_formatter import format_sample, format_sample_text, format_sample_json


def _r(job_id: str, duration: float = 1.0, success: bool = True) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success, error=None)


def _report(*results) -> SampleReport:
    return SampleReport(total=10, sampled=len(results), results=list(results))


def test_text_empty():
    report = SampleReport(total=0, sampled=0, results=[])
    out = format_sample_text(report)
    assert "No samples" in out


def test_text_contains_job_id():
    report = _report(_r("my-job"))
    out = format_sample_text(report)
    assert "my-job" in out


def test_text_shows_status_ok():
    report = _report(_r("j1", success=True))
    assert "OK" in format_sample_text(report)


def test_text_shows_status_fail():
    report = _report(_r("j2", success=False))
    assert "FAIL" in format_sample_text(report)


def test_text_shows_none_duration():
    r = TimingResult(job_id="j3", duration=None, success=False, error="boom")
    report = _report(r)
    assert "n/a" in format_sample_text(report)


def test_json_is_valid():
    report = _report(_r("j1"), _r("j2"))
    out = format_sample_json(report)
    data = json.loads(out)
    assert data["sampled"] == 2


def test_format_dispatches_json():
    report = _report(_r("j1"))
    out = format_sample(report, fmt="json")
    json.loads(out)  # should not raise


def test_format_dispatches_text():
    report = _report(_r("j1"))
    out = format_sample(report, fmt="text")
    assert "Sample:" in out
