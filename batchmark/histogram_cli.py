"""CLI entry point for generating duration histograms."""
from __future__ import annotations
import argparse
import json
import sys
from typing import List

from batchmark.timer import TimingResult
from batchmark.histogram import build_histogram, format_histogram


def _load_results(path: str) -> List[TimingResult]:
    with open(path) as f:
        data = json.load(f)
    results = []
    for item in data:
        results.append(
            TimingResult(
                job_id=item["job_id"],
                duration=item.get("duration"),
                success=item.get("success", True),
            )
        )
    return results


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="batchmark-histogram",
        description="Show a duration histogram for batch job results.",
    )
    p.add_argument("results_file", help="JSON file with timing results")
    p.add_argument(
        "--buckets", type=int, default=5, help="Number of histogram buckets (default: 5)"
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
        help="Output format",
    )
    return p


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        results = _load_results(args.results_file)
    except FileNotFoundError:
        print(f"Error: file not found: {args.results_file}", file=sys.stderr)
        sys.exit(1)
    except (json.JSONDecodeError, KeyError) as exc:
        print(f"Error reading results: {exc}", file=sys.stderr)
        sys.exit(1)

    buckets = build_histogram(results, num_buckets=args.buckets)
    print(format_histogram(buckets, fmt=args.fmt))


if __name__ == "__main__":
    main()
