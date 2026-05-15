"""Auto-generate plain-Korean comments and similar-season lookups.

These power the detail page so the user doesn't have to read raw numbers.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def style_caption(row: pd.Series) -> str:
    """One-line summary describing what kind of team-season this was."""
    ops_pct = row["ops_pctile"]
    era_pct = row["era_pctile"]
    win_pct = row["win_pct"]

    offense_strong = ops_pct >= 75
    pitching_strong = era_pct >= 75
    offense_weak = ops_pct <= 25
    pitching_weak = era_pct <= 25
    elite_win = win_pct >= 0.6
    poor_win = win_pct <= 0.4

    if elite_win and offense_strong and pitching_strong:
        return "전 부문 압도 — 역대급 강팀 시즌"
    if elite_win and offense_strong and not pitching_strong:
        return "타선의 힘으로 우승급 성적. 마운드는 평범"
    if elite_win and pitching_strong and not offense_strong:
        return "마운드의 힘으로 우승급 성적. 타선은 평범"
    if poor_win and offense_weak and pitching_weak:
        return "공·수 모두 부진했던 힘든 시즌"
    if poor_win and pitching_weak:
        return "마운드가 무너진 시즌. 타선은 그럭저럭"
    if poor_win and offense_weak:
        return "타선이 부진했던 시즌. 마운드는 견뎌줌"
    if offense_strong and not pitching_strong:
        return "타선 강세, 마운드 평범"
    if pitching_strong and not offense_strong:
        return "마운드 강세, 타선 평범"
    return "전반적으로 평범한 시즌"


def similar_seasons(df: pd.DataFrame, year: int, team: str,
                    n: int = 5) -> pd.DataFrame:
    """Find n team-seasons most similar to (year, team) by OPS, ERA, WHIP, win_pct.

    Excludes the query row itself. Distance is Euclidean on z-scored stats.
    """
    target = df[(df["year"] == year) & (df["team"] == team)]
    if target.empty:
        raise ValueError(f"Team-season not found: {year} {team}")
    target = target.iloc[0]

    cols = ["ops", "era", "whip", "win_pct"]
    mu = df[cols].mean()
    sigma = df[cols].std(ddof=0)
    z = (df[cols] - mu) / sigma
    z_target = (target[cols] - mu) / sigma

    dist = np.sqrt(((z - z_target) ** 2).sum(axis=1))
    out = df.assign(_dist=dist)
    out = out[~((out["year"] == year) & (out["team"] == team))]
    return out.nsmallest(n, "_dist").drop(columns="_dist")
