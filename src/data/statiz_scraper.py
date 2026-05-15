"""STATIZ scraper skeleton.

STATIZ (statiz.sports-conference.com) provides KBO sabermetric stats
(WAR, wRC+, FIP, etc.) by season.

IMPORTANT — before running for real:
  1. Manually open https://statiz.sports-conference.com/robots.txt and
     confirm that the paths you plan to scrape are not disallowed.
  2. Keep delay_seconds >= 1.5 (see PoliteClient).
  3. Only scrape what you need; cache aggressively.

This module is intentionally a stub for now. The first concrete endpoint
will be implemented in week 1, day 2-3 after URL/path discovery.
"""
from __future__ import annotations

from .http_client import FetchResult, PoliteClient

BASE_URL = "https://statiz.sports-conference.com"


def fetch_season_batting(year: int, *, client: PoliteClient | None = None) -> FetchResult:
    """TODO: identify the correct STATIZ URL for season batting leaderboard."""
    raise NotImplementedError(
        "Week 1 day 2-3: open STATIZ in a browser, find the season batting "
        "leaderboard URL, then implement this function. Pass `year` in the URL."
    )


def fetch_season_pitching(year: int, *, client: PoliteClient | None = None) -> FetchResult:
    """TODO: identify the correct STATIZ URL for season pitching leaderboard."""
    raise NotImplementedError(
        "Week 1 day 2-3: same as fetch_season_batting, for pitching."
    )
