"""Tests for batchmark.censor."""
from __future__ import annotations

import pytest

from batchmark.timer import TimingResult
from batchmark.censor import censor_results, CensorReport, _MASK


def _r(
    job_id: str = "job-1",
    success: bool = True,
    duration: float | None = 1.0,
    error: str | None = None,
) -> TimingResult:
    r = TimingResult(job_id=job_id, success=success, duration=duration, error=error)
    return r


# ---------------------------------------------------------------------------
# basic behaviour
# ---------------------------------------------------------------------------

def test_empty_returns_empty_report():
    report = censor_results([])
    assert isinstance(report, CensorReport)
    assert report.results == []
    assert report.redacted_count == 0


def test_no_flags_leaves_results_unchanged():
    results = [_r("job-a"), _r("job-b", success=False, error="oops")]
    report = censor_results(results)
    assert report.redacted_count == 0
    assert report.results[0].job_id == "job-a"
    assert report.results[1].error == "oops"


# ---------------------------------------------------------------------------
# mask_job_id
# ---------------------------------------------------------------------------

def test_mask_job_id_replaces_all_ids():
    results = [_r("alpha"), _r("beta"), _r("gamma")]
    report = censor_results(results, mask_job_id=True)
    assert all(r.job_id == _MASK for r in report.results)
    assert report.redacted_count == 3


def test_mask_job_id_preserves_other_fields():
    result = _r("my-job", success=False, duration=2.5, error="bad")
    report = censor_results([result], mask_job_id=True)
    cr = report.results[0]
    assert cr.success is False
    assert cr.duration == 2.5
    assert cr.error == "bad"


# ---------------------------------------------------------------------------
# mask_error
# ---------------------------------------------------------------------------

def test_mask_error_hides_error_message():
    result = _r("job-x", success=False, error="secret error detail")
    report = censor_results([result], mask_error=True)
    assert report.results[0].error == _MASK
    assert report.redacted_count == 1


def test_mask_error_leaves_none_error_as_none():
    result = _r("job-ok", success=True, error=None)
    report = censor_results([result], mask_error=True)
    assert report.results[0].error is None
    assert report.redacted_count == 0


# ---------------------------------------------------------------------------
# redact_metadata_keys
# ---------------------------------------------------------------------------

def test_redact_metadata_key_masks_value():
    result = _r("job-1")
    result.metadata = {"api_key": "super-secret", "region": "us-east"}
    report = censor_results([result], redact_metadata_keys=["api_key"])
    assert report.results[0].metadata["api_key"] == _MASK
    assert report.results[0].metadata["region"] == "us-east"
    assert report.redacted_count == 1


def test_redact_metadata_key_missing_key_no_error():
    result = _r("job-1")
    result.metadata = {"region": "eu-west"}
    report = censor_results([result], redact_metadata_keys=["api_key"])
    assert report.redacted_count == 0


# ---------------------------------------------------------------------------
# custom_job_id_fn
# ---------------------------------------------------------------------------

def test_custom_job_id_fn_overrides_mask_job_id():
    result = _r("original-id")
    report = censor_results(
        [result],
        custom_job_id_fn=lambda r: r.job_id[:3] + "***",
    )
    assert report.results[0].job_id == "ori***"
    assert report.redacted_count == 1


# ---------------------------------------------------------------------------
# to_dict
# ---------------------------------------------------------------------------

def test_to_dict_structure():
    result = _r("job-z", success=True, duration=0.5)
    report = censor_results([result], mask_job_id=True)
    d = report.to_dict()
    assert "redacted_count" in d
    assert "results" in d
    assert d["results"][0]["job_id"] == _MASK
