"""Team-season feature engineering.

Take raw batting + pitching CSVs and produce a single tidy dataframe of
team-seasons with percentiles and a grade — the data layer the dashboard
renders.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.data import loader

BATTING_CSV = Path("data/raw/kbo_team_batting.csv")
PITCHING_CSV = Path("data/raw/kbo_team_pitching.csv")

# Columns we keep from each side; pitching gets explicit renames to avoid
# colliding with batting (h, hr, bb, so mean opposite things).
BATTING_KEEP = ["year", "team", "g", "pa", "ab", "r", "h", "hr",
                "rbi", "bb", "so", "avg", "obp", "slg", "ops"]
PITCHING_KEEP = ["year", "team", "w", "l", "ip", "era", "whip",
                 "so", "bb", "hr", "h", "er"]
PITCHING_RENAME = {"so": "k_pit", "bb": "bb_pit", "hr": "hr_allowed",
                   "h": "h_allowed", "er": "er_pit"}


def merge_team_season(bat: pd.DataFrame, pit: pd.DataFrame) -> pd.DataFrame:
    """Inner-join batting and pitching on (year, team) and add win_pct."""
    b = bat[BATTING_KEEP].copy()
    p = pit[PITCHING_KEEP].rename(columns=PITCHING_RENAME)
    merged = b.merge(p, on=["year", "team"], how="inner")
    merged["win_pct"] = merged["w"] / (merged["w"] + merged["l"])
    return merged


def add_percentiles(df: pd.DataFrame) -> pd.DataFrame:
    """Add percentile columns. Higher-is-better stats get standard pct rank;
    ERA/WHIP (lower-is-better) get inverted."""
    df = df.copy()
    df["ops_pctile"] = df["ops"].rank(pct=True) * 100
    df["obp_pctile"] = df["obp"].rank(pct=True) * 100
    df["slg_pctile"] = df["slg"].rank(pct=True) * 100
    df["era_pctile"] = (1 - df["era"].rank(pct=True)) * 100
    df["whip_pctile"] = (1 - df["whip"].rank(pct=True)) * 100
    df["win_pctile"] = df["win_pct"].rank(pct=True) * 100
    return df


def add_grade(df: pd.DataFrame) -> pd.DataFrame:
    """Composite grade from OPS percentile + ERA percentile.

    Thresholds tuned so historic dominators (2000 현대, 1985 삼성) reach S,
    and the distribution is roughly normal across the 323 team-seasons.
    """
    df = df.copy()
    composite = (df["ops_pctile"] + df["era_pctile"]) / 2

    def to_grade(score: float) -> str:
        if score >= 85:
            return "S"
        if score >= 70:
            return "A"
        if score >= 50:
            return "B"
        if score >= 30:
            return "C"
        return "D"

    df["grade"] = composite.map(to_grade)
    df["composite_score"] = composite
    return df


def build(project_root: Path | None = None) -> pd.DataFrame:
    """Convenience: load CSVs from data/raw/ and return enriched team-seasons."""
    root = project_root or Path(__file__).resolve().parents[2]
    bat = loader.load_batting(root / BATTING_CSV)
    pit = loader.load_pitching(root / PITCHING_CSV)
    df = merge_team_season(bat, pit)
    df = add_percentiles(df)
    df = add_grade(df)
    return df
