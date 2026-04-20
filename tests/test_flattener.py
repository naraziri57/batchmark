"""Tests for batchmark.flattener."""

from __future__ import annotations

from batchmark.timer import TimingResult
from batchmark.flattener import (
    FlatRecord,
    flatten_results,
    flatten_annotated,
    records_to_dicts,
)


def _r(job_id: str, duration: float | None = 1.0, success: bool = True) -> TimingResult:
    return TimingResult(job_id=job_id, duration=duration, success=success)


def test_flatten_results_empty():
    assert flatten_results([]) == []


def test_flatten_results_basic():
    results = [_r("job-a", 1.5), _r("job-b", 2.0, success=False)]
    records = flatten_results(results)
    assert len(records) == 2
    assert records[0].job_id == "job-a"
    assert records[0].duration == 1.5
    assert records[0].success is True
    assert records[1].success is False


def test_flatten_results_extra_fields():
    results = [_r("job-x", 0.5)]
    records = flatten_results(results, extra_fields={"env": "prod"})
    assert records[0].extra == {"env": "prod"}


def test_flatten_results_none_duration():
    results = [_r("job-nil", None, success=False)]
    records = flatten_results(results)
    assert records[0].duration is None


def test_flat_record_to_dict_keys():
    rec = FlatRecord(job_id="j", duration=1.0, success=True, tags={"env": "ci"})
    d = rec.to_dict()
    assert "job_id" in d
    assert "duration" in d
    assert "success" in d
    assert "tag_env" in d
    assert d["tag_env"] == "ci"


def test_flat_record_extra_merged():
    rec = FlatRecord(job_id="j", duration=0.1, success=True, extra={"run": 3})
    d = rec.to_dict()
    assert d["run"] == 3


class _FakeAnnotated:
    def __init__(self, result, tags):
        self.result = result
        self.tags = tags


def test_flatten_annotated_empty():
    assert flatten_annotated([]) == []


def test_flatten_annotated_preserves_tags():
    ar = _FakeAnnotated(_r("job-a", 1.0), {"bucket": "fast"})
    records = flatten_annotated([ar])
    assert len(records) == 1
    assert records[0].tags == {"bucket": "fast"}
    assert records[0].job_id == "job-a"


def test_records_to_dicts():
    records = [FlatRecord(job_id="j", duration=0.5, success=True)]
    dicts = records_to_dicts(records)
    assert isinstance(dicts, list)
    assert dicts[0]["job_id"] == "j"
