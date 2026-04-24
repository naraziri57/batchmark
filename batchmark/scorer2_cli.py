"""CLI entry point for weighted scoring."""
from __future__ import annotations
import argparse
import json
import sys
from batchmark.scorer2 import weighted_score
from batchmark.scorer2_formatter import format_weighted_score
from batchmark.timer import TimingResult


def _load_results(path: str):
    with open(path) as fh:
        raw = json.load(fh)
    results = []
    for item in raw:
        results.append(
            TimingResult(
                job_id=item["job_id"],
                duration=item.get("duration"),
                success=item.get("success", True),
                error=item.get("error"),
            )
        )
    return results


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Weighted multi-metric scorer")
    p.add_argument("results", help="JSON file of timing results")
    p.add_argument("--duration-weight", type=float, default=0.6)
    p.add_argument("--success-weight", type=float, default=0.4)
    p.add_argument("--baseline", help="JSON file mapping job_id -> baseline_duration")
    p.add_argument("--format", choices=["text", "json"], default="text")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    results = _load_results(args.results)
    baseline = None
    if args.baseline:
        with open(args.baseline) as fh:
            baseline = json.load(fh)
    report = weighted_score(
        results,
        duration_weight=args.duration_weight,
        success_weight=args.success_weight,
        baseline_durations=baseline,
    )
    print(format_weighted_score(report, fmt=args.format))


if __name__ == "__main__":
    main()
