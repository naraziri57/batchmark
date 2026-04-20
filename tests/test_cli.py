"""Tests for the CLI module."""

import json
from unittest.mock import patch

import pytest

from batchmark.cli import main, parse_args


def test_parse_args_defaults():
    args = parse_args(["echo hello"])
    assert args.commands == ["echo hello"]
    assert args.fmt == "text"
    assert args.runs == 1
    assert args.output is None


def test_parse_args_custom():
    args = parse_args(["ls", "pwd", "--format", "json", "--runs", "3"])
    assert args.commands == ["ls", "pwd"]
    assert args.fmt == "json"
    assert args.runs == 3


def test_main_text_output(capsys):
    ret = main(["echo hi"])
    assert ret == 0
    captured = capsys.readouterr()
    assert "echo hi" in captured.out


def test_main_json_output(capsys):
    ret = main(["echo hi", "--format", "json"])
    assert ret == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "results" in data
    assert len(data["results"]) == 1
    assert data["results"][0]["job_id"] == "echo hi"


def test_main_multiple_runs(capsys):
    ret = main(["echo hi", "--runs", "2", "--format", "json"])
    assert ret == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert len(data["results"]) == 2
    job_ids = [r["job_id"] for r in data["results"]]
    assert "echo hi[1]" in job_ids
    assert "echo hi[2]" in job_ids


def test_main_failed_command(capsys):
    ret = main(["false", "--format", "json"])
    assert ret == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["results"][0]["success"] is False


def test_main_output_file(tmp_path, capsys):
    out_file = tmp_path / "report.txt"
    ret = main(["echo hi", "--output", str(out_file)])
    assert ret == 0
    assert out_file.exists()
    content = out_file.read_text()
    assert "echo hi" in content
    captured = capsys.readouterr()
    assert captured.out == ""


def test_main_output_file_json(tmp_path, capsys):
    """Output file should contain valid JSON when --format json is used."""
    out_file = tmp_path / "report.json"
    ret = main(["echo hi", "--format", "json", "--output", str(out_file)])
    assert ret == 0
    assert out_file.exists()
    data = json.loads(out_file.read_text())
    assert "results" in data
    assert data["results"][0]["job_id"] == "echo hi"
    # Nothing should be printed to stdout when writing to a file
    captured = capsys.readouterr()
    assert captured.out == ""
