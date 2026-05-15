"""Sanity tests for the SQLite HTTP cache."""
from __future__ import annotations

import time
from pathlib import Path

from src.data import cache


def test_round_trip(tmp_path: Path):
    db = tmp_path / "test.sqlite"
    assert cache.get("https://example.com", db_path=db) is None

    cache.put("https://example.com", b"<html>hi</html>", 200, db_path=db)
    assert cache.get("https://example.com", db_path=db) == b"<html>hi</html>"


def test_max_age_expires(tmp_path: Path):
    db = tmp_path / "test.sqlite"
    cache.put("https://example.com", b"x", 200, db_path=db)
    time.sleep(0.05)
    assert cache.get("https://example.com", max_age_seconds=0.01, db_path=db) is None
    assert cache.get("https://example.com", max_age_seconds=10, db_path=db) == b"x"
