"""CLI entry point for the partitioner feature."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from batchmark.replay import load_replay
from batchmark.partitioner import partition_results
from batchmark.partition_formatter import format_partition


def _load_results(path: str):
    p = Path(path)
    if not p.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        sys.exit(1)
    return load_replay(path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="batchmark-partition",
        description="Partition batch results by job_id prefix or custom label.",
    )
    parser.add_argument("input", help="Path to replay JSON file")
    parser.add_argument(
        "--key",
        choices=["job_id", "status"],
        default="status",
        help="Field to partition by (default: status)",
    )
    parser.add_argument(
        "--labels",
        nargs="*",
        default=None,
        help="Ordered list of partition labels to include",
    )
    parser.add_argument(
        "--format",
        dest="fmt",
        choices=["text", "json", "csv"],
        default="text",
    )
    return parser


def main(argv=None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    results = _load_results(args.input)

    if args.key == "status":
        key_fn = lambda r: "ok" if r.success else "fail"
    else:
        key_fn = lambda r: r.job_id

    report = partition_results(results, key_fn=key_fn, labels=args.labels)
    print(format_partition(report, fmt=args.fmt))


if __name__ == "__main__":
    main()
