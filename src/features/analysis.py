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


def hitter_caption(row: pd.Series) -> str:
    """타자 한 명의 시즌 캐릭터를 한 문장으로.

    규칙 기반. 가장 두드러진 특징 하나를 잡아서 표현.
    """
    ops = row.get("ops", 0) or 0
    avg = row.get("avg", 0) or 0
    hr = row.get("hr", 0) or 0
    rbi = row.get("rbi", 0) or 0
    so = row.get("so", 0) or 0
    bb = row.get("bb", 0) or 0
    pa = row.get("pa", 1) or 1
    obp = row.get("obp", 0) or 0
    slg = row.get("slg", 0) or 0
    iso = slg - avg                                # 순장타율 근사
    so_rate = so / pa if pa else 0
    bb_rate = bb / pa if pa else 0

    if avg >= 0.330 and hr >= 10 and ops >= 1.000:
        return "5툴 전성기 — AVG·HR·OPS 모두 최상위급"
    if hr >= 12 and iso >= 0.220:
        return "거포형 슬러거 — 장타 비율 매우 높음"
    if avg >= 0.330 and so_rate <= 0.13:
        return "교타형 — 높은 타율과 낮은 삼진율"
    if obp >= 0.420 and slg < 0.450:
        return "출루형 — 볼넷·안타로 출루, 장타는 적음"
    if bb_rate >= 0.15:
        return "선구안 좋은 타자 — 볼넷 비율 매우 높음"
    if ops <= 0.700:
        return "부진한 시즌 — 전반적으로 평균 이하"
    if hr >= 8 and rbi >= 25:
        return "찬스 활약형 — 중심타자급 생산성"
    return "꾸준한 활약 — 평균 이상의 안정적 기록"


def pitcher_caption(row: pd.Series) -> str:
    """투수 한 명의 시즌 캐릭터를 한 문장으로."""
    era = row.get("era", 99) or 99
    whip = row.get("whip", 99) or 99
    so = row.get("so", 0) or 0
    ip = row.get("ip", 0) or 0
    bb = row.get("bb", 0) or 0
    sv = row.get("sv", 0) or 0
    hld = row.get("hld", 0) or 0

    k_per_9 = (so * 9 / ip) if ip > 0 else 0
    bb_per_9 = (bb * 9 / ip) if ip > 0 else 0

    if era <= 2.50 and whip <= 1.10 and ip >= 30:
        return "에이스급 시즌 — ERA·WHIP 모두 최상위"
    if sv >= 10:
        return "마무리 투수 — 세이브 누적"
    if hld >= 10:
        return "필승조 — 홀드 누적, 핵심 셋업맨"
    if k_per_9 >= 10 and so >= 30:
        return f"탈삼진형 — 9이닝당 {k_per_9:.1f}K"
    if bb_per_9 <= 2.0 and ip >= 30:
        return "제구파 — 볼넷이 매우 적음"
    if era >= 5.50:
        return "부진 — 평균자책점 높음"
    if whip <= 1.15 and era <= 3.50:
        return "안정형 — 주자 허용 적고 점수도 적음"
    return "평균적 활약 — 그럭저럭 안정적 기록"


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
