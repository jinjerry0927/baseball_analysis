"""Generic CSV loader for downloaded baseball datasets.

Drop any KBO/MLB CSV into data/raw/ and use these helpers to peek at the
schema and load it into a DataFrame. The Phase 1 plan only needs season-
level batting and pitching stats — column names vary by source, so we
sniff and normalize.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"

# Aliases for common stats. Add to these as you encounter new column names.
# Left side = canonical name we'll use throughout the project.
BATTING_ALIASES: dict[str, tuple[str, ...]] = {
    "player": ("player", "name", "선수", "선수명", "player_name", "batter"),
    "team":   ("team", "팀", "team_name", "tm"),
    "year":   ("year", "season", "연도", "yr"),
    "g":      ("g", "games", "경기", "gp"),
    "pa":     ("pa", "plate_appearances", "타석"),
    "ab":     ("ab", "at_bats", "타수"),
    "h":      ("h", "hits", "안타"),
    "hr":     ("hr", "home_runs", "homeruns", "홈런"),
    "rbi":    ("rbi", "runs_batted_in", "타점"),
    "r":      ("r", "runs", "득점"),
    "bb":     ("bb", "walks", "bases_on_balls", "볼넷", "사사구"),
    "so":     ("so", "k", "strikeouts", "삼진"),
    "avg":    ("avg", "ba", "타율", "batting_average"),
    "obp":    ("obp", "출루율", "on_base_pct"),
    "slg":    ("slg", "장타율", "slugging"),
    "ops":    ("ops",),
    "war":    ("war", "wins_above_replacement"),
}

PITCHING_ALIASES: dict[str, tuple[str, ...]] = {
    "player": ("player", "name", "선수", "선수명", "pitcher"),
    "team":   ("team", "팀", "team_name", "tm"),
    "year":   ("year", "season", "연도"),
    "g":      ("g", "games", "경기"),
    "gs":     ("gs", "games_started", "선발"),
    "w":      ("w", "wins", "승"),
    "l":      ("l", "losses", "패"),
    "sv":     ("sv", "saves", "세이브"),
    "ip":     ("ip", "innings_pitched", "이닝"),
    "h":      ("h", "hits_allowed", "hits", "피안타"),
    "hr":     ("hr_allowed", "home_runs", "피홈런"),
    "bb":     ("bb", "walks_issued", "walks", "볼넷"),
    "so":     ("so", "k", "strikeouts", "탈삼진"),
    "er":     ("er", "earned_runs", "자책점"),
    "era":    ("era", "평균자책점"),
    "whip":   ("whip",),
    "fip":    ("fip",),
    "war":    ("war",),
}


def list_raw_files(pattern: str = "*.csv") -> list[Path]:
    """Return CSV files sitting in data/raw/."""
    return sorted(RAW_DIR.glob(pattern))


def peek(path: Path, nrows: int = 5) -> pd.DataFrame:
    """Quick look at the first few rows so you can see the columns."""
    return pd.read_csv(path, nrows=nrows, encoding=_sniff_encoding(path))


def _sniff_encoding(path: Path) -> str:
    """KBO CSVs sometimes come in cp949/euc-kr; try utf-8 first, then fall back."""
    for enc in ("utf-8", "utf-8-sig", "cp949", "euc-kr"):
        try:
            with open(path, encoding=enc) as f:
                f.read(2048)
            return enc
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError(f"Could not decode {path} with utf-8/cp949/euc-kr")


def _build_rename_map(columns: Iterable[str],
                      aliases: dict[str, tuple[str, ...]]) -> dict[str, str]:
    """Map source columns -> canonical names where we can match (case-insensitive)."""
    lowered = {c.lower(): c for c in columns}
    rename: dict[str, str] = {}
    for canonical, options in aliases.items():
        for opt in options:
            if opt.lower() in lowered:
                rename[lowered[opt.lower()]] = canonical
                break
    return rename


def load_batting(path: Path) -> pd.DataFrame:
    """Load a batting CSV and rename columns to canonical names where possible."""
    df = pd.read_csv(path, encoding=_sniff_encoding(path))
    df = df.rename(columns=_build_rename_map(df.columns, BATTING_ALIASES))
    return df


def load_pitching(path: Path) -> pd.DataFrame:
    """Load a pitching CSV and rename columns to canonical names where possible."""
    df = pd.read_csv(path, encoding=_sniff_encoding(path))
    df = df.rename(columns=_build_rename_map(df.columns, PITCHING_ALIASES))
    return df
