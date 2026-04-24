"""Formatters for WeightedScoringReport."""
from __future__ import annotations
import json
from batchmark.scorer2 import WeightedScoringReport


def format_weighted_score_text(report: WeightedScoringReport) -> str:
    if not report.scores:
        return "No weighted scores available.\n"
    lines = ["Weighted Scoring Report", "=" * 40]
    for s in sorted(report.scores, key=lambda x: x.weighted_total, reverse=True):
        line = f"  {s.job_id:<30} total={s.weighted_total:.4f}  dur={s.duration_score:.4f}  suc={s.success_score:.4f}"
        if s.tags:
            extras = "  ".join(f"{k}={v:.4f}" for k, v in s.tags.items())
            line += f"  [{extras}]"
        lines.append(line)
    overall = report.overall()
    if overall is not None:
        lines.append("-" * 40)
        lines.append(f"  Overall average: {overall:.4f}")
    return "\n".join(lines) + "\n"


def format_weighted_score_json(report: WeightedScoringReport) -> str:
    return json.dumps(report.to_dict(), indent=2)


def format_weighted_score(report: WeightedScoringReport, fmt: str = "text") -> str:
    if fmt == "json":
        return format_weighted_score_json(report)
    return format_weighted_score_text(report)
