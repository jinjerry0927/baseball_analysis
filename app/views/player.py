"""선수 대시보드 — st.navigation에서 호출되는 view 함수."""
from __future__ import annotations

import streamlit as st

from src.features import analysis
from src.features.player import (
    add_hitter_percentiles,
    add_pitcher_percentiles,
    load_hitters,
    load_pitchers,
)


@st.cache_data(ttl=3600)
def _get_hitters():
    return add_hitter_percentiles(load_hitters())


@st.cache_data(ttl=3600)
def _get_pitchers():
    return add_pitcher_percentiles(load_pitchers())


def _hitter_tab():
    h = _get_hitters()
    sort_choice = st.selectbox(
        "정렬 기준",
        options=["ops", "avg", "hr", "rbi", "h", "bb", "obp", "slg"],
        format_func=lambda x: x.upper(),
        key="h_sort",
    )
    h_sorted = h.sort_values(sort_choice, ascending=False).reset_index(drop=True)
    h_sorted.insert(0, "순위", range(1, len(h_sorted) + 1))

    display_cols = ["순위", "player", "team", "avg", "ops", "obp", "slg",
                    "hr", "rbi", "h", "bb", "so", "g", "ops_pctile"]
    event_h = st.dataframe(
        h_sorted[display_cols],
        column_config={
            "순위": st.column_config.NumberColumn(width="small"),
            "player": st.column_config.TextColumn("선수", width="medium"),
            "team": st.column_config.TextColumn("팀", width="small"),
            "avg": st.column_config.NumberColumn("AVG", format="%.3f", width="small"),
            "ops": st.column_config.NumberColumn("OPS", format="%.3f", width="small"),
            "obp": st.column_config.NumberColumn("OBP", format="%.3f", width="small"),
            "slg": st.column_config.NumberColumn("SLG", format="%.3f", width="small"),
            "hr": st.column_config.NumberColumn("HR", width="small"),
            "rbi": st.column_config.NumberColumn("RBI", width="small"),
            "h": st.column_config.NumberColumn("안타", width="small"),
            "bb": st.column_config.NumberColumn("BB", width="small"),
            "so": st.column_config.NumberColumn("SO", width="small"),
            "g": st.column_config.NumberColumn("경기", width="small"),
            "ops_pctile": st.column_config.ProgressColumn(
                "OPS 백분위", min_value=0, max_value=100, format="%.0f"),
        },
        hide_index=True,
        use_container_width=True,
        on_select="rerun",
        selection_mode="single-row",
        height=480,
    )

    sel_h = event_h.selection.rows  # type: ignore[attr-defined]
    if not sel_h:
        return
    row = h_sorted.iloc[sel_h[0]]
    st.divider()
    st.subheader(f"{row['player']} · {row['team']}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("AVG", f"{row['avg']:.3f}")
    c2.metric("OPS", f"{row['ops']:.3f}")
    c3.metric("HR", int(row["hr"]))
    c4.metric("RBI", int(row["rbi"]))

    st.progress(
        min(row["ops_pctile"] / 100, 1.0),
        text=f"OPS 백분위 — 30명 중 상위 {100 - row['ops_pctile']:.0f}%",
    )

    st.success(f"📝 {analysis.hitter_caption(row)}")

    st.markdown("##### 세부 기록")
    detail_cols = ["pa", "ab", "r", "h", "2b", "3b", "hr", "tb", "rbi",
                   "bb", "ibb", "hbp", "so", "gdp", "obp", "slg", "ops",
                   "mh", "risp", "ph_ba"]
    avail = [c for c in detail_cols if c in row.index]
    detail_df = row[avail].to_frame().T.reset_index(drop=True)
    st.dataframe(detail_df, hide_index=True, use_container_width=True)


def _pitcher_tab():
    p = _get_pitchers()
    sort_choice = st.selectbox(
        "정렬 기준 (ERA·WHIP은 낮을수록 좋음)",
        options=["era", "whip", "so", "w", "sv", "wpct", "ip"],
        format_func=lambda x: x.upper(),
        key="p_sort",
    )
    ascending = sort_choice in ("era", "whip")
    p_sorted = p.sort_values(sort_choice, ascending=ascending).reset_index(drop=True)
    p_sorted.insert(0, "순위", range(1, len(p_sorted) + 1))

    display_cols = ["순위", "player", "team", "era", "whip", "w", "l", "sv",
                    "hld", "ip", "so", "bb", "g", "era_pctile"]
    event_p = st.dataframe(
        p_sorted[display_cols],
        column_config={
            "순위": st.column_config.NumberColumn(width="small"),
            "player": st.column_config.TextColumn("선수", width="medium"),
            "team": st.column_config.TextColumn("팀", width="small"),
            "era": st.column_config.NumberColumn("ERA", format="%.2f", width="small"),
            "whip": st.column_config.NumberColumn("WHIP", format="%.2f", width="small"),
            "w": st.column_config.NumberColumn("승", width="small"),
            "l": st.column_config.NumberColumn("패", width="small"),
            "sv": st.column_config.NumberColumn("세이브", width="small"),
            "hld": st.column_config.NumberColumn("홀드", width="small"),
            "ip": st.column_config.NumberColumn("이닝", format="%.1f", width="small"),
            "so": st.column_config.NumberColumn("탈삼진", width="small"),
            "bb": st.column_config.NumberColumn("볼넷", width="small"),
            "g": st.column_config.NumberColumn("경기", width="small"),
            "era_pctile": st.column_config.ProgressColumn(
                "ERA 백분위", min_value=0, max_value=100, format="%.0f"),
        },
        hide_index=True,
        use_container_width=True,
        on_select="rerun",
        selection_mode="single-row",
        height=420,
    )

    sel_p = event_p.selection.rows  # type: ignore[attr-defined]
    if not sel_p:
        return
    row = p_sorted.iloc[sel_p[0]]
    st.divider()
    st.subheader(f"{row['player']} · {row['team']}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("ERA", f"{row['era']:.2f}")
    c2.metric("WHIP", f"{row['whip']:.2f}")
    c3.metric("승-패", f"{int(row['w'])}-{int(row['l'])}")
    c4.metric("탈삼진", int(row["so"]))

    st.progress(
        min(row["era_pctile"] / 100, 1.0),
        text=f"ERA 백분위 — 22명 중 상위 {100 - row['era_pctile']:.0f}%",
    )

    st.success(f"📝 {analysis.pitcher_caption(row)}")

    st.markdown("##### 세부 기록")
    detail_cols = ["g", "w", "l", "sv", "hld", "ip", "h", "hr", "bb",
                   "hbp", "so", "r", "er", "era", "whip", "cg", "sho",
                   "qs", "bsv", "tbf", "np", "wp", "bk"]
    avail = [c for c in detail_cols if c in row.index]
    detail_df = row[avail].to_frame().T.reset_index(drop=True)
    st.dataframe(detail_df, hide_index=True, use_container_width=True)


def player_view():
    st.title("⚾ KBO 선수 대시보드 — 2026 시즌")
    st.caption(
        "KBO 공식 사이트 (페이지 1) · 타자는 30경기 이상, 투수는 일정 이닝 이상 컷오프. "
        "페이지네이션 미구현 — 페이지 2의 선수들은 아직 보이지 않음."
    )
    tab_h, tab_p = st.tabs(["🏏 타자 (30명)", "⚾ 투수 (22명)"])
    with tab_h:
        _hitter_tab()
    with tab_p:
        _pitcher_tab()
