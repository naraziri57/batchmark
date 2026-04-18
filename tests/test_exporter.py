"""Tests for batchmark.exporter."""

import json
import os
import tempfile
from pathlib import Path

import pytest

from batchmark.exporter import export_report, _infer_format, SUPPORTED_FORMATS
from batchmark.summary import summarize
from batchmark.timer import TimingResult


def _make_result(name, duration, success=True):
    return TimingResult(job_name=name, duration=duration, success=success, error=None)


def test_infer_format_json():
    assert _infer_format("report.json") == "json"


def test_infer_format_csv():
    assert _infer_format("/tmp/out.csv") == "csv"


def test_infer_format_txt():
    assert _infer_format("results.txt") == "text"


def test_infer_format_unknown_defaults_text():
    assert _infer_format("report.xyz") == "text"


def test_export_json(tmp_path):
    results = [_make_result("job1", 1.0), _make_result("job2", 2.0)]
    summary = summarize(results)
    out = tmp_path / "report.json"
    returned_path = export_report(summary, results, str(out))
    assert Path(returned_path).exists()
    data = json.loads(out.read_text())
    assert "summary" in data
    assert "results" in data


def test_export_csv(tmp_path):
    results = [_make_result("jobA", 0.5, success=True), _make_result("jobB", 1.5, success=False)]
    summary = summarize(results)
    out = tmp_path / "report.csv"
    export_report(summary, results, str(out))
    content = out.read_text()
    assert "job_name" in content
    assert "jobA" in content


def test_export_text(tmp_path):
    results = [_make_result("jobX", 3.0)]
    summary = summarize(results)
    out = tmp_path / "report.txt"
    export_report(summary, results, str(out))
    content = out.read_text()
    assert "jobX" in content


def test_export_creates_parent_dirs(tmp_path):
    results = [_make_result("j", 1.0)]
    summary = summarize(results)
    out = tmp_path / "nested" / "dir" / "report.json"
    export_report(summary, results, str(out))
    assert out.exists()


def test_export_unsupported_format(tmp_path):
    results = [_make_result("j", 1.0)]
    summary = summarize(results)
    with pytest.raises(ValueError, match="Unsupported format"):
        export_report(summary, results, str(tmp_path / "out.txt"), fmt="xml")


def test_export_fmt_override(tmp_path):
    results = [_make_result("j", 1.0)]
    summary = summarize(results)
    # file extension is .txt but we force json
    out = tmp_path / "out.txt"
    export_report(summary, results, str(out), fmt="json")
    data = json.loads(out.read_text())
    assert "summary" in data
