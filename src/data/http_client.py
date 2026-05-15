"""Polite HTTP client: cache-first, rate-limited, identifies itself."""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

import requests

from . import cache

USER_AGENT = (
    "baseball_analysis-study/0.1 "
    "(personal portfolio project; contact: jinuk.james.lee@gmail.com)"
)
DEFAULT_DELAY_SECONDS = 1.5


@dataclass
class FetchResult:
    url: str
    content: bytes
    status: int
    from_cache: bool


class PoliteClient:
    """HTTP client that caches responses and rate-limits live requests."""

    def __init__(self, delay_seconds: float = DEFAULT_DELAY_SECONDS,
                 user_agent: str = USER_AGENT):
        self.delay_seconds = delay_seconds
        self.session = requests.Session()
        self.session.headers["User-Agent"] = user_agent
        self._last_request_at: float = 0.0

    def get(self, url: str, *, max_age_seconds: Optional[float] = 7 * 24 * 3600) -> FetchResult:
        cached = cache.get(url, max_age_seconds=max_age_seconds)
        if cached is not None:
            return FetchResult(url=url, content=cached, status=200, from_cache=True)

        elapsed = time.time() - self._last_request_at
        if elapsed < self.delay_seconds:
            time.sleep(self.delay_seconds - elapsed)

        resp = self.session.get(url, timeout=30)
        self._last_request_at = time.time()
        resp.raise_for_status()
        cache.put(url, resp.content, resp.status_code)
        return FetchResult(url=url, content=resp.content, status=resp.status_code, from_cache=False)

    def post(self, url: str, data: dict,
             *, cache_key: Optional[str] = None,
             max_age_seconds: Optional[float] = 7 * 24 * 3600) -> FetchResult:
        """POST with rate-limit and cache. cache_key disambiguates POSTs to the same URL."""
        key = cache_key or url
        cached = cache.get(key, max_age_seconds=max_age_seconds)
        if cached is not None:
            return FetchResult(url=url, content=cached, status=200, from_cache=True)

        elapsed = time.time() - self._last_request_at
        if elapsed < self.delay_seconds:
            time.sleep(self.delay_seconds - elapsed)

        resp = self.session.post(url, data=data, timeout=30)
        self._last_request_at = time.time()
        resp.raise_for_status()
        cache.put(key, resp.content, resp.status_code)
        return FetchResult(url=url, content=resp.content, status=resp.status_code, from_cache=False)
