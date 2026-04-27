"""tests for funneler.py and funneler_formatter.py"""
import json
import pytest
from batchmark.timer import TimingResult
from batchmark.funneler import FunnelStage, funnel_results
from batchmark.funneler_formatter import format_funnel_text, format_funnel_json, format_funnel


def _r(job_id: str, success: bool = True, duration: float = 1.0) -> TimingResult:
    return TimingResult(job_id=job_id, success=success, duration=duration, error=None)


def test_empty_results_returns_empty_report():
    report = funnel_results([], [])
    assert report.final_results == []
    assert report.steps == []
    assert report.total_dropped == 0


def test_no_stages_passes_all_through():
    results = [_r("a"), _r("b")]
    report = funnel_results(results, [])
    assert len(report.final_results) == 2
    assert report.total_dropped == 0


def test_single_stage_drops_failures():
    results = [_r("a", success=True), _r("b", success=False), _r("c", success=True)]
    stages = [FunnelStage(name="success_only", predicate=lambda r: r.success)]
    report = funnel_results(results, stages)
    assert len(report.final_results) == 2
    assert report.steps[0].dropped == 1
    assert report.steps[0].passed == 2


def test_multiple_stages_chain_correctly():
    results = [
        _r("a", success=True, duration=0.5),
        _r("b", success=True, duration=2.0),
        _r("c", success=False, duration=0.1),
    ]
    stages = [
        FunnelStage("success", lambda r: r.success),
        FunnelStage("fast", lambda r: r.duration is not None and r.duration < 1.0),
    ]
    report = funnel_results(results, stages)
    assert len(report.final_results) == 1
    assert report.final_results[0].job_id == "a"
    assert report.total_dropped == 2


def test_step_counts_are_recorded_per_stage():
    results = [_r(str(i)) for i in range(5)]
    stages = [
        FunnelStage("all", lambda r: True),
        FunnelStage("none", lambda r: False),
    ]
    report = funnel_results(results, stages)
    assert report.steps[0].passed == 5
    assert report.steps[0].dropped == 0
    assert report.steps[1].passed == 0
    assert report.steps[1].dropped == 5


def test_to_dict_structure():
    results = [_r("x", success=True)]
    stages = [FunnelStage("keep_all", lambda r: True)]
    report = funnel_results(results, stages)
    d = report.to_dict()
    assert "steps" in d
    assert "total_dropped" in d
    assert "final_count" in d
    assert d["final_count"] == 1


def test_format_text_empty():
    from batchmark.funneler import FunnelReport
    out = format_funnel_text(FunnelReport())
    assert "No funnel stages" in out


def test_format_text_shows_stage_name():
    results = [_r("a"), _r("b", success=False)]
    stages = [FunnelStage("only_ok", lambda r: r.success)]
    report = funnel_results(results, stages)
    out = format_funnel_text(report)
    assert "only_ok" in out
    assert "dropped=1" in out


def test_format_json_is_valid():
    results = [_r("a"), _r("b")]
    stages = [FunnelStage("pass_all", lambda r: True)]
    report = funnel_results(results, stages)
    out = format_funnel_json(report)
    data = json.loads(out)
    assert "steps" in data


def test_format_dispatch_default_is_text():
    from batchmark.funneler import FunnelReport
    report = FunnelReport()
    assert format_funnel(report) == format_funnel_text(report)
