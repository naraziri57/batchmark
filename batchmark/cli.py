"""CLI entry point for batchmark."""

import argparse
import subprocess
import sys
from typing import List, Optional

from batchmark.exporter import export_report
from batchmark.report import render_report
from batchmark.summary import summarize
from batchmark.timer import JobTimer


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="batchmark",
        description="Benchmark batch jobs and output structured timing reports.",
    )
    parser.add_argument("command", nargs="+", help="Command to benchmark.")
    parser.add_argument(
        "--runs", type=int, default=1, help="Number of times to run the command."
    )
    parser.add_argument(
        "--format", dest="fmt", choices=("text", "json", "csv"), default="text"
    )
    parser.add_argument(
        "--output", dest="output", default=None, help="Write report to this file."
    )
    return parser.parse_args(argv)


def run_command(command: List[str]) -> tuple:
    """Run a shell command, return (success, error_msg)."""
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            return False, result.stderr.strip() or f"exit code {result.returncode}"
        return True, None
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)

    results = []
    for i in range(args.runs):
        job_name = " ".join(args.command)
        if args.runs > 1:
            job_name = f"{job_name} (run {i + 1})"
        timer = JobTimer(job_name)
        timer.start()
        success, error = run_command(args.command)
        result = timer.finish(success=success, error=error)
        results.append(result)

    summary = summarize(results)

    if args.output:
        written = export_report(summary, results, args.output, fmt=args.fmt if args.fmt != "text" else None)
        print(f"Report written to {written}", file=sys.stderr)
    else:
        print(render_report(summary, results, fmt=args.fmt))

    return 0 if summary.failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
