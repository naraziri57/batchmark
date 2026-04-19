"""Retention policy: prune old baseline/replay files by count or age."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional


@dataclass
class RetentionPolicy:
    max_count: Optional[int] = None  # keep newest N files
    max_age_days: Optional[float] = None  # drop files older than N days


@dataclass
class PruneResult:
    removed: List[Path]
    kept: List[Path]

    def to_dict(self) -> dict:
        return {
            "removed": [str(p) for p in self.removed],
            "kept": [str(p) for p in self.kept],
            "removed_count": len(self.removed),
            "kept_count": len(self.kept),
        }


def _mtime(p: Path) -> datetime:
    return datetime.fromtimestamp(p.stat().st_mtime)


def apply_retention(directory: Path, pattern: str, policy: RetentionPolicy, dry_run: bool = False) -> PruneResult:
    """Apply retention policy to files matching pattern in directory."""
    files = sorted(directory.glob(pattern), key=_mtime, reverse=True)  # newest first

    to_remove: List[Path] = []
    to_keep: List[Path] = []

    cutoff = datetime.now() - timedelta(days=policy.max_age_days) if policy.max_age_days is not None else None

    for i, f in enumerate(files):
        age_expired = cutoff is not None and _mtime(f) < cutoff
        count_expired = policy.max_count is not None and i >= policy.max_count
        if age_expired or count_expired:
            to_remove.append(f)
        else:
            to_keep.append(f)

    if not dry_run:
        for f in to_remove:
            f.unlink()

    return PruneResult(removed=to_remove, kept=to_keep)
