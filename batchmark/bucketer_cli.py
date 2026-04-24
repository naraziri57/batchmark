"""CLI entry-point for the bucketer feature."""
from __future__ import annotations
import argparse
import json
import sys
from batchmark.timer import TimingResult
from batchmark.bucketer import bucket_results
from batchmark.bucketer_formatter import format_bucket


def _load_results(path: str):
    with open(path) as fh:
        raw = json.load(fh)
    out = []
    for d in raw:
        r = TimingResult(
            job_id=d["job_id"],
            duration=d.get("duration"),
            success=d.get("success", True),
            error=d.get("error"),
            metadata=d.get("metadata", {}),
        )
        out.append(r)
    return out


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="batchmark-bucketer",
        description="Group timing results into duration buckets.",
    )
    p.add_argument("input", help="JSON file of timing results")
    p.add_argument(
        "--boundaries",
        nargs="+",
        type=float,
        default=[1.0, 5.0, 10.0],
        metavar="SEC",
        help="Bucket boundary values in seconds (default: 1 5 10)",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
    )
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    results = _load_results(args.input)
    report = bucket_results(results, args.boundaries)
    print(format_bucket(report, args.fmt))


if __name__ == "__main__":
    main()
