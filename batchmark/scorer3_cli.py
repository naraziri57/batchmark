"""CLI entry-point for composite scorer."""
from __future__ import annotations
import argparse
import json
import sys
from batchmark.scorer3 import score_composite
from batchmark.scorer3_formatter import format_composite
from batchmark.timer import TimingResult


def _load_results(path: str):
    with open(path) as fh:
        data = json.load(fh)
    results = []
    for item in data:
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
    p = argparse.ArgumentParser(
        prog="batchmark-scorer3",
        description="Composite job scorer: duration + success + consistency.",
    )
    p.add_argument("results", help="JSON file with timing results")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.add_argument("--w-duration", type=float, default=0.4, dest="w_duration")
    p.add_argument("--w-success", type=float, default=0.4, dest="w_success")
    p.add_argument("--w-consistency", type=float, default=0.2, dest="w_consistency")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    results = _load_results(args.results)
    weights = {
        "duration": args.w_duration,
        "success": args.w_success,
        "consistency": args.w_consistency,
    }
    report = score_composite(results, weights=weights)
    print(format_composite(report, fmt=args.format), end="")


if __name__ == "__main__":
    main()
