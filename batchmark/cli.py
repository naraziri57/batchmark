"""CLI entry point for batchmark."""

import argparse
import subprocess
import sys
import time
from typing import List, Optional

from batchmark.report import render_report
from batchmark.timer import JobTimer


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="batchmark",
        description="Benchmark batch jobs and output structured timing reports.",
    )
    parser.add_argument(
        "commands",
        nargs="+",
        metavar="CMD",
        help="Commands to benchmark (each as a single quoted string).",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "csv"],
        default="text",
        dest="fmt",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=1,
        help="Number of times to run each command (default: 1).",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        default=None,
        help="Write report to FILE instead of stdout.",
    )
    return parser.parse_args(argv)


def run_command(cmd: str) -> tuple[bool, float]:
    """Run a shell command and return (success, elapsed_seconds)."""
    start = time.perf_counter()
    try:
        result = subprocess.run(cmd, shell=True, check=False)
        elapsed = time.perf_counter() - start
        return result.returncode == 0, elapsed
    except Exception:
        elapsed = time.perf_counter() - start
        return False, elapsed


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    timer = JobTimer()

    for cmd in args.commands:
        for run_idx in range(args.runs):
            job_id = cmd if args.runs == 1 else f"{cmd}[{run_idx + 1}]"
            timer.start(job_id)
            success, _ = run_command(cmd)
            timer.finish(job_id, success=success)

    report = render_report(timer.results, fmt=args.fmt)

    if args.output:
        with open(args.output, "w") as fh:
            fh.write(report)
    else:
        print(report)

    return 0


if __name__ == "__main__":
    sys.exit(main())
