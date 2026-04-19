"""CLI entry point for segmenter."""
from __future__ import annotations
import argparse
import json
import sys
from batchmark.timer import TimingResult
from batchmark.segmenter import segment_by_window
from batchmark.segmenter_formatter import format_segment


def _load_results(path: str):
    with open(path) as f:
        data = json.load(f)
    results = []
    for d in data:
        r = TimingResult(
            job_id=d["job_id"],
            duration=d.get("duration"),
            success=d.get("success", True),
            error=d.get("error"),
            start_time=d.get("start_time"),
        )
        results.append(r)
    return results


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Segment batch results into time windows")
    p.add_argument("input", help="JSON file of timing results")
    p.add_argument("--window", type=float, default=1.0, help="Window size in seconds")
    p.add_argument("--origin", type=float, default=None, help="Start time origin")
    p.add_argument("--format", choices=["text", "json"], default="text")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    results = _load_results(args.input)
    segments = segment_by_window(results, args.window, args.origin)
    print(format_segment(segments, args.format))


if __name__ == "__main__":
    main()
