"""Tests for batchmark.retention."""

import time
from pathlib import Path

import pytest

from batchmark.retention import RetentionPolicy, apply_retention


def _touch(p: Path, content: str = "{}") -> Path:
    p.write_text(content)
    return p


def test_no_policy_keeps_all(tmp_path):
    for i in range(3):
        _touch(tmp_path / f"run_{i}.json")
    policy = RetentionPolicy()
    result = apply_retention(tmp_path, "*.json", policy)
    assert len(result.removed) == 0
    assert len(result.kept) == 3


def test_max_count_prunes_oldest(tmp_path):
    files = []
    for i in range(5):
        f = _touch(tmp_path / f"run_{i:02d}.json")
        time.sleep(0.02)
        files.append(f)
    policy = RetentionPolicy(max_count=3)
    result = apply_retention(tmp_path, "*.json", policy)
    assert len(result.kept) == 3
    assert len(result.removed) == 2
    for r in result.removed:
        assert not r.exists()


def test_dry_run_does_not_delete(tmp_path):
    for i in range(4):
        _touch(tmp_path / f"run_{i}.json")
        time.sleep(0.01)
    policy = RetentionPolicy(max_count=2)
    result = apply_retention(tmp_path, "*.json", policy, dry_run=True)
    assert len(result.removed) == 2
    for r in result.removed:
        assert r.exists()  # not actually deleted


def test_max_age_days_removes_old(tmp_path):
    old = _touch(tmp_path / "old.json")
    # backdate mtime by 10 days
    old_mtime = old.stat().st_mtime - 10 * 86400
    import os
    os.utime(old, (old_mtime, old_mtime))
    _touch(tmp_path / "new.json")

    policy = RetentionPolicy(max_age_days=5)
    result = apply_retention(tmp_path, "*.json", policy)
    assert any(r.name == "old.json" for r in result.removed)
    assert any(k.name == "new.json" for k in result.kept)


def test_to_dict_keys(tmp_path):
    for i in range(2):
        _touch(tmp_path / f"r{i}.json")
        time.sleep(0.01)
    policy = RetentionPolicy(max_count=1)
    result = apply_retention(tmp_path, "*.json", policy)
    d = result.to_dict()
    assert "removed" in d and "kept" in d
    assert d["removed_count"] == 1
    assert d["kept_count"] == 1


def test_pattern_filters_files(tmp_path):
    _touch(tmp_path / "a.json")
    _touch(tmp_path / "b.csv")
    _touch(tmp_path / "c.json")
    time.sleep(0.01)
    policy = RetentionPolicy(max_count=1)
    result = apply_retention(tmp_path, "*.json", policy)
    assert len(result.kept) + len(result.removed) == 2  # only json files considered
