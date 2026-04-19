"""CLI for applying retention policies to baseline/replay directories."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from batchmark.retention import RetentionPolicy, apply_retention


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Prune old batchmark files by retention policy")
    p.add_argument("directory", help="Directory to prune")
    p.add_argument("--pattern", default="*.json", help="Glob pattern (default: *.json)")
    p.add_argument("--max-count", type=int, default=None, help="Keep newest N files")
    p.add_argument("--max-age-days", type=float, default=None, help="Remove files older than N days")
    p.add_argument("--dry-run", action="store_true", help="Show what would be removed without deleting")
    p.add_argument("--format", choices=["text", "json"], default="text")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)

    directory = Path(args.directory)
    if not directory.is_dir():
        print(f"error: {directory} is not a directory", file=sys.stderr)
        sys.exit(1)

    if args.max_count is None and args.max_age_days is None:
        print("error: specify --max-count and/or --max-age-days", file=sys.stderr)
        sys.exit(1)

    policy = RetentionPolicy(max_count=args.max_count, max_age_days=args.max_age_days)
    result = apply_retention(directory, args.pattern, policy, dry_run=args.dry_run)

    if args.format == "json":
        print(json.dumps(result.to_dict(), indent=2))
    else:
        tag = "[dry-run] " if args.dry_run else ""
        print(f"{tag}kept: {result.kept_count if hasattr(result, 'kept_count') else len(result.kept)}, "
              f"removed: {len(result.removed)}")
        for f in result.removed:
            print(f"  - {f}")


if __name__ == "__main__":
    main()
