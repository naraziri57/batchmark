"""CLI entry point for the classifier module."""
from __future__ import annotations

import argparse
import json
import sys

from batchmark.classifier import classify_results, classifier_from_map
from batchmark.classifier_formatter import format_classifier
from batchmark.timer import TimingResult


def _load_results(path: str) -> list[TimingResult]:
    with open(path) as f:
        data = json.load(f)
    results = []
    for d in data:
        r = TimingResult(
            job_id=d["job_id"],
            duration=d.get("duration"),
            success=d.get("success", True),
            error=d.get("error"),
        )
        results.append(r)
    return results


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="batchmark-classifier",
        description="Classify batch job results into named categories.",
    )
    p.add_argument("results", help="Path to JSON results file")
    p.add_argument(
        "--map",
        metavar="CATEGORY:PREFIX",
        action="append",
        default=[],
        help="Category rule: CATEGORY:job_id_prefix (repeatable)",
    )
    p.add_argument(
        "--default", default="uncategorized", help="Default category name"
    )
    p.add_argument(
        "--format", choices=["text", "json", "csv"], default="text"
    )
    return p


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    results = _load_results(args.results)

    category_map: dict[str, list[str]] = {}
    for rule in args.map:
        if ":" not in rule:
            print(f"Invalid rule (expected CATEGORY:PREFIX): {rule}", file=sys.stderr)
            sys.exit(1)
        cat, prefix = rule.split(":", 1)
        category_map.setdefault(cat, []).append(prefix)

    classifiers = classifier_from_map(category_map)
    report = classify_results(results, classifiers, default_category=args.default)
    print(format_classifier(report, fmt=args.format))


if __name__ == "__main__":
    main()
