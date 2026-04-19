"""CLI entry point for outlier detection on batchmark result files."""
from __future__ import annotations
import argparse
import json
import sys
from batchmark.timer import TimingResult
from batchmark.outlier import detect_outliers
from batchmark.outlier_formatter import format_outlier


def _load_results(path: str) -> list[TimingResult]:
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
        prog="batchmark-outlier",
        description="Detect outlier jobs from a batchmark results JSON file.",
    )
    p.add_argument("input", help="Path to results JSON file")
    p.add_argument(
        "--threshold", type=float, default=2.0,
        help="Z-score threshold for outlier detection (default: 2.0)"
    )
    p.add_argument(
        "--format", choices=["text", "json"], default="text",
        dest="fmt", help="Output format"
    )
    p.add_argument(
        "--outliers-only", action="store_true",
        help="Only print jobs flagged as outliers"
    )
    return p


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        results = _load_results(args.input)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {args.input}: {e}", file=sys.stderr)
        sys.exit(1)

    report = detect_outliers(results, threshold=args.threshold)

    if args.outliers_only:
        from dataclasses import replace
        report.results[:] = report.outliers

    print(format_outlier(report, fmt=args.fmt))


if __name__ == "__main__":
    main()
