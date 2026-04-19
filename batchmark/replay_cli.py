"""CLI entry point for replay sub-commands."""

from __future__ import annotations

import argparse
import sys

from batchmark.replay import load_replay, filter_replay
from batchmark.report import render_report
from batchmark.summary import summarize


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="batchmark-replay",
        description="Re-analyse a saved replay file",
    )
    p.add_argument("file", help="Path to replay JSON file")
    p.add_argument("--job-id", default=None, help="Filter to a specific job id")
    p.add_argument("--success-only", action="store_true", help="Include only successful results")
    p.add_argument(
        "--format",
        choices=["text", "json", "csv"],
        default="text",
        help="Output format (default: text)",
    )
    return p


def main(argv=None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        results = load_replay(args.file)
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    results = filter_replay(results, job_id=args.job_id, success_only=args.success_only)

    if not results:
        print("No results matched the given filters.", file=sys.stderr)
        sys.exit(0)

    summary = summarize(results)
    print(render_report(summary, fmt=args.format))


if __name__ == "__main__":
    main()
