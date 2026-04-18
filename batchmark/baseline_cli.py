"""CLI helpers for baseline subcommands: save, load-compare, list."""

import argparse
import sys

from batchmark.baseline import save_baseline, load_baseline, list_baselines
from batchmark.comparator import compare
from batchmark.comparison_formatter import format_comparison
from batchmark.pipeline import run_pipeline


def cmd_save(args: argparse.Namespace) -> None:
    results = run_pipeline(
        command=args.command,
        runs=args.runs,
        success_only=False,
        failed_only=False,
        sort_by=None,
        top=None,
    )
    path = save_baseline(args.name, results)
    print(f"Saved {len(results)} result(s) to baseline '{args.name}' -> {path}")


def cmd_compare(args: argparse.Namespace) -> None:
    baseline = load_baseline(args.baseline)
    candidate = load_baseline(args.candidate)
    report = compare(baseline, candidate)
    output = format_comparison(report, fmt=args.format)
    print(output)


def cmd_list(args: argparse.Namespace) -> None:
    names = list_baselines()
    if not names:
        print("No baselines saved yet.")
    else:
        for name in sorted(names):
            print(name)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="batchmark-baseline", description="Manage baselines")
    sub = parser.add_subparsers(dest="subcommand", required=True)

    p_save = sub.add_parser("save", help="Run a command and save results as a baseline")
    p_save.add_argument("name", help="Baseline name")
    p_save.add_argument("command", help="Command to benchmark")
    p_save.add_argument("--runs", type=int, default=5)
    p_save.set_defaults(func=cmd_save)

    p_cmp = sub.add_parser("compare", help="Compare two saved baselines")
    p_cmp.add_argument("baseline", help="Name of the baseline run")
    p_cmp.add_argument("candidate", help="Name of the candidate run")
    p_cmp.add_argument("--format", choices=["text", "json"], default="text")
    p_cmp.set_defaults(func=cmd_compare)

    p_list = sub.add_parser("list", help="List saved baselines")
    p_list.set_defaults(func=cmd_list)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
