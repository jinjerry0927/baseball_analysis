"""선수 단위 데이터 로드 — KBO 공식 사이트의 기본+세부 endpoint를 merge.

현재 데이터 양 (2026 시즌 진행 중, 30+ 경기 / 일정 이닝 컷):
  타자  ~30명
  투수  ~22명
"""
from __future__ import annotations

import pandas as pd

from src.data.kbo_scraper import (
    fetch_hitter_basic,
    fetch_hitter_detail,
    fetch_pitcher_basic,
    fetch_pitcher_detail,
    parse_record_table,
)


def _merge_basic_detail(basic: pd.DataFrame, detail: pd.DataFrame) -> pd.DataFrame:
    """basic + detail을 (player, team)으로 join. 중복 컬럼은 basic 쪽 유지."""
    # rank는 정렬 기준이 달라서 의미 없음 → detail에서 제거
    detail = detail.drop(columns=[c for c in ("rank",) if c in detail.columns])
    merged = basic.merge(detail, on=["player", "team"], how="inner", suffixes=("", "_dup"))
    # _dup 으로 끝나는 중복 컬럼 제거 (avg, era 등)
    dup_cols = [c for c in merged.columns if c.endswith("_dup")]
    return merged.drop(columns=dup_cols)


def load_hitters() -> pd.DataFrame:
    basic = parse_record_table(fetch_hitter_basic().content)
    detail = parse_record_table(fetch_hitter_detail().content)
    return _merge_basic_detail(basic, detail)


def load_pitchers() -> pd.DataFrame:
    basic = parse_record_table(fetch_pitcher_basic().content)
    detail = parse_record_table(fetch_pitcher_detail().content)
    return _merge_basic_detail(basic, detail)


def add_hitter_percentiles(df: pd.DataFrame) -> pd.DataFrame:
    """주요 타격 지표 백분위 추가 (높을수록 좋음)."""
    df = df.copy()
    for col, out in [("ops", "ops_pctile"), ("avg", "avg_pctile"),
                     ("hr", "hr_pctile"), ("rbi", "rbi_pctile")]:
        if col in df.columns:
            df[out] = df[col].rank(pct=True) * 100
    return df


def add_pitcher_percentiles(df: pd.DataFrame) -> pd.DataFrame:
    """주요 투수 지표 백분위 추가 (ERA/WHIP은 낮을수록 좋아서 반전)."""
    df = df.copy()
    if "era" in df.columns:
        df["era_pctile"] = (1 - df["era"].rank(pct=True)) * 100
    if "whip" in df.columns:
        df["whip_pctile"] = (1 - df["whip"].rank(pct=True)) * 100
    if "wpct" in df.columns:
        df["wpct_pctile"] = df["wpct"].rank(pct=True) * 100
    if "so" in df.columns:
        df["so_pctile"] = df["so"].rank(pct=True) * 100
    return df
