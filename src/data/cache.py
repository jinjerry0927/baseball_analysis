"""SQLite-backed HTTP response cache.

Avoid re-hitting the source on every run. Cache key = URL.
"""
from __future__ import annotations

import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

DEFAULT_CACHE_PATH = Path(__file__).resolve().parents[2] / "data" / "cache" / "http.sqlite"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS http_cache (
    url        TEXT PRIMARY KEY,
    content    BLOB NOT NULL,
    status     INTEGER NOT NULL,
    fetched_at REAL NOT NULL
);
"""


@contextmanager
def _connect(db_path: Path):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(_SCHEMA)
        yield conn
        conn.commit()
    finally:
        conn.close()


def get(url: str, *, max_age_seconds: Optional[float] = None,
        db_path: Path = DEFAULT_CACHE_PATH) -> Optional[bytes]:
    """Return cached bytes for `url`, or None if missing/expired."""
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT content, fetched_at FROM http_cache WHERE url = ?", (url,)
        ).fetchone()
    if row is None:
        return None
    content, fetched_at = row
    if max_age_seconds is not None and (time.time() - fetched_at) > max_age_seconds:
        return None
    return content


def put(url: str, content: bytes, status: int,
        db_path: Path = DEFAULT_CACHE_PATH) -> None:
    with _connect(db_path) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO http_cache (url, content, status, fetched_at) "
            "VALUES (?, ?, ?, ?)",
            (url, content, status, time.time()),
        )
