"""선수 대시보드 — st.navigation에서 호출되는 view 함수.

탭 3개:
  - 타자: 30경기 이상 컷오프 선수 리더보드
  - 투수: 일정 이닝 이상 컷오프 선수 리더보드
  - 비교: 두 선수 골라 주요 지표 side-by-side
사이드바에서 팀 필터로 좁힐 수 있다 (비교 탭은 전체 데이터 사용).
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from src.features import analysis
from src.features.player import (
    add_hitter_percentiles,
    add_pitcher_percentiles,
    load_hitters,
    load_pitchers,
)


@st.cache_data(ttl=3600)
def _get_hitters() -> pd.DataFrame:
    return add_hitter_percentiles(load_hitters())


@st.cache_data(ttl=3600)
def _get_pitchers() -> pd.DataFrame:
    return add_pitcher_percentiles(load_pitchers())


# ─────────────────────── 타자 탭 ───────────────────────

def _hitter_tab(h: pd.DataFrame) -> None:
    if h.empty:
        st.info("해당 팀의 타자가 컷오프(30경기) 이상에 없습니다.")
        return

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

    sel = event_h.selection.rows  # type: ignore[attr-defined]
    if not sel:
        return
    row = h_sorted.iloc[sel[0]]
    st.divider()
    st.subheader(f"{row['player']} · {row['team']}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("AVG", f"{row['avg']:.3f}")
    c2.metric("OPS", f"{row['ops']:.3f}")
    c3.metric("HR", int(row["hr"]))
    c4.metric("RBI", int(row["rbi"]))

    st.progress(
        min(row["ops_pctile"] / 100, 1.0),
        text=f"OPS 백분위 — 전체 30명 중 상위 {100 - row['ops_pctile']:.0f}%",
    )
    st.success(f"📝 {analysis.hitter_caption(row)}")

    st.markdown("##### 세부 기록")
    detail_cols = ["pa", "ab", "r", "h", "2b", "3b", "hr", "tb", "rbi",
                   "bb", "ibb", "hbp", "so", "gdp", "obp", "slg", "ops",
                   "mh", "risp", "ph_ba"]
    avail = [c for c in detail_cols if c in row.index]
    st.dataframe(row[avail].to_frame().T.reset_index(drop=True),
                 hide_index=True, use_container_width=True)


# ─────────────────────── 투수 탭 ───────────────────────

def _pitcher_tab(p: pd.DataFrame) -> None:
    if p.empty:
        st.info("해당 팀의 투수가 컷오프 이상에 없습니다.")
        return

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

    sel = event_p.selection.rows  # type: ignore[attr-defined]
    if not sel:
        return
    row = p_sorted.iloc[sel[0]]
    st.divider()
    st.subheader(f"{row['player']} · {row['team']}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("ERA", f"{row['era']:.2f}")
    c2.metric("WHIP", f"{row['whip']:.2f}")
    c3.metric("승-패", f"{int(row['w'])}-{int(row['l'])}")
    c4.metric("탈삼진", int(row["so"]))

    st.progress(
        min(row["era_pctile"] / 100, 1.0),
        text=f"ERA 백분위 — 전체 22명 중 상위 {100 - row['era_pctile']:.0f}%",
    )
    st.success(f"📝 {analysis.pitcher_caption(row)}")

    st.markdown("##### 세부 기록")
    detail_cols = ["g", "w", "l", "sv", "hld", "ip", "h", "hr", "bb",
                   "hbp", "so", "r", "er", "era", "whip", "cg", "sho",
                   "qs", "bsv", "tbf", "np", "wp", "bk"]
    avail = [c for c in detail_cols if c in row.index]
    st.dataframe(row[avail].to_frame().T.reset_index(drop=True),
                 hide_index=True, use_container_width=True)


# ─────────────────────── 비교 탭 ───────────────────────

# (col, label, format, higher_is_better)
_HITTER_COMPARE_STATS = [
    ("avg", "AVG", "{:.3f}", True),
    ("ops", "OPS", "{:.3f}", True),
    ("obp", "OBP", "{:.3f}", True),
    ("slg", "SLG", "{:.3f}", True),
    ("hr", "HR", "{:d}", True),
    ("rbi", "RBI", "{:d}", True),
    ("h", "안타", "{:d}", True),
    ("bb", "볼넷", "{:d}", True),
    ("so", "삼진", "{:d}", False),
]

_PITCHER_COMPARE_STATS = [
    ("era", "ERA", "{:.2f}", False),
    ("whip", "WHIP", "{:.2f}", False),
    ("w", "승", "{:d}", True),
    ("l", "패", "{:d}", False),
    ("sv", "세이브", "{:d}", True),
    ("hld", "홀드", "{:d}", True),
    ("ip", "이닝", "{:.1f}", True),
    ("so", "탈삼진", "{:d}", True),
    ("bb", "볼넷", "{:d}", False),
]


def _comparison_tab() -> None:
    role = st.radio("비교 대상", ["타자", "투수"], horizontal=True, key="cmp_role")
    if role == "타자":
        df = _get_hitters()
        stats = _HITTER_COMPARE_STATS
    else:
        df = _get_pitchers()
        stats = _PITCHER_COMPARE_STATS

    options = [f"{r['player']} ({r['team']})" for _, r in df.iterrows()]
    if len(options) < 2:
        st.info("비교할 선수가 부족합니다.")
        return

    c1, c2 = st.columns(2)
    a = c1.selectbox("선수 A", options, key=f"cmp_a_{role}")
    b = c2.selectbox("선수 B", options, index=1, key=f"cmp_b_{role}")
    if a == b:
        st.warning("같은 선수입니다. 다른 선수를 선택하세요.")
        return

    def _row(label: str) -> pd.Series:
        nm = label.rsplit(" (", 1)[0]
        tm = label.rsplit(" (", 1)[1].rstrip(")")
        return df[(df["player"] == nm) & (df["team"] == tm)].iloc[0]

    ra, rb = _row(a), _row(b)

    st.divider()
    ha, hb = st.columns(2)
    ha.markdown(f"### 🅰️ {ra['player']}")
    ha.caption(ra["team"])
    hb.markdown(f"### 🅱️ {rb['player']}")
    hb.caption(rb["team"])

    wins_a = wins_b = ties = 0
    for col, label, fmt, higher_better in stats:
        if col not in ra.index or col not in rb.index:
            continue
        try:
            va = int(ra[col]) if "d" in fmt else float(ra[col])
            vb = int(rb[col]) if "d" in fmt else float(rb[col])
        except (ValueError, TypeError):
            continue
        a_str = fmt.format(va)
        b_str = fmt.format(vb)

        if va == vb:
            mark_a = mark_b = "🟰"
            ties += 1
        elif (va > vb) == higher_better:
            mark_a, mark_b = "🟢", ""
            wins_a += 1
        else:
            mark_a, mark_b = "", "🟢"
            wins_b += 1

        ca, cmid, cb = st.columns([3, 2, 3])
        ca.markdown(f"<div style='text-align:right; font-size:1.05rem;'><b>{a_str}</b> {mark_a}</div>",
                    unsafe_allow_html=True)
        cmid.markdown(f"<div style='text-align:center; color:#666;'>{label}</div>",
                      unsafe_allow_html=True)
        cb.markdown(f"<div style='text-align:left; font-size:1.05rem;'>{mark_b} <b>{b_str}</b></div>",
                    unsafe_allow_html=True)

    st.divider()
    sa, sb, st_ = st.columns(3)
    sa.metric(f"🅰️ {ra['player']} 우세", f"{wins_a}개")
    sb.metric(f"🅱️ {rb['player']} 우세", f"{wins_b}개")
    st_.metric("동률", f"{ties}개")


# ─────────────────────── 뷰 진입점 ───────────────────────

def player_view() -> None:
    st.title("⚾ KBO 선수 대시보드 — 2026 시즌")
    st.caption(
        "KBO 공식 사이트 (페이지 1) · 타자는 30경기 이상, 투수는 일정 이닝 이상 컷오프. "
        "페이지네이션 미구현 — 페이지 2의 선수들은 아직 보이지 않음."
    )

    # 사이드바 팀 필터 (G — 양 탭 동시 필터)
    h_all = _get_hitters()
    p_all = _get_pitchers()
    all_teams = sorted(set(h_all["team"]) | set(p_all["team"]))
    selected_teams = st.sidebar.multiselect("팀 필터 (비우면 전체)", all_teams)

    if selected_teams:
        h_view = h_all[h_all["team"].isin(selected_teams)]
        p_view = p_all[p_all["team"].isin(selected_teams)]
    else:
        h_view, p_view = h_all, p_all

    tab_h, tab_p, tab_cmp = st.tabs([
        f"🏏 타자 ({len(h_view)}명)",
        f"⚾ 투수 ({len(p_view)}명)",
        "🔍 선수 비교",
    ])
    with tab_h:
        _hitter_tab(h_view)
    with tab_p:
        _pitcher_tab(p_view)
    with tab_cmp:
        _comparison_tab()
