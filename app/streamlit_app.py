"""KBO 팀 시즌 대시보드.

실행: streamlit run app/streamlit_app.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.features import analysis, team_season  # noqa: E402

st.set_page_config(
    page_title="KBO 팀 시즌 대시보드",
    page_icon="⚾",
    layout="wide",
)


@st.cache_data
def load():
    return team_season.build(PROJECT_ROOT)


df = load()

# ─────────────────────── Sidebar ───────────────────────
st.sidebar.header("필터")

y_min, y_max = int(df["year"].min()), int(df["year"].max())
year_range = st.sidebar.slider("연도 범위", y_min, y_max, (y_min, y_max))

teams = st.sidebar.multiselect(
    "팀 (비우면 전체)",
    options=sorted(df["team"].unique()),
)

grades = st.sidebar.multiselect(
    "등급",
    options=["S", "A", "B", "C", "D"],
    default=["S", "A", "B", "C", "D"],
)

# ─────────────────────── Filter + Rank ───────────────────────
filtered = df[
    df["year"].between(*year_range) & df["grade"].isin(grades)
].copy()
if teams:
    filtered = filtered[filtered["team"].isin(teams)]
filtered = filtered.sort_values("composite_score", ascending=False).reset_index(drop=True)
filtered.insert(0, "rank", range(1, len(filtered) + 1))

# ─────────────────────── Header ───────────────────────
st.title("⚾ KBO 팀 시즌 대시보드 (1982~2021)")
st.caption(
    f"{len(filtered)}개 팀-시즌 · 종합 점수 = (OPS 백분위 + ERA 백분위) / 2 · "
    "행을 클릭하면 아래에 상세 분석"
)

# ─────────────────────── Leaderboard ───────────────────────
display_cols = [
    "rank", "year", "team", "grade", "w", "l", "win_pct",
    "ops", "ops_pctile", "era", "era_pctile", "composite_score",
]
event = st.dataframe(
    filtered[display_cols],
    column_config={
        "rank": st.column_config.NumberColumn("순위", width="small"),
        "year": st.column_config.NumberColumn("연도", format="%d", width="small"),
        "team": st.column_config.TextColumn("팀", width="medium"),
        "grade": st.column_config.TextColumn("등급", width="small"),
        "w": st.column_config.NumberColumn("승", width="small"),
        "l": st.column_config.NumberColumn("패", width="small"),
        "win_pct": st.column_config.NumberColumn("승률", format="%.3f", width="small"),
        "ops": st.column_config.NumberColumn("OPS", format="%.3f", width="small"),
        "ops_pctile": st.column_config.ProgressColumn(
            "타격 백분위", min_value=0, max_value=100, format="%.0f"),
        "era": st.column_config.NumberColumn("ERA", format="%.2f", width="small"),
        "era_pctile": st.column_config.ProgressColumn(
            "투수 백분위", min_value=0, max_value=100, format="%.0f"),
        "composite_score": st.column_config.NumberColumn(
            "종합", format="%.1f", width="small"),
    },
    hide_index=True,
    use_container_width=True,
    on_select="rerun",
    selection_mode="single-row",
    height=500,
)

# ─────────────────────── Detail Panel ───────────────────────
selected = event.selection.rows  # type: ignore[attr-defined]
st.divider()

if not selected:
    st.info("📌 위 표에서 한 시즌을 클릭하세요. 등급의 근거와 비슷한 시즌이 표시됩니다.")
else:
    row = filtered.iloc[selected[0]]
    year, team = int(row["year"]), row["team"]

    st.subheader(f"📊 {year} {team}")

    grade_color = {"S": "🟣", "A": "🔵", "B": "🟢", "C": "🟡", "D": "🔴"}[row["grade"]]
    st.markdown(
        f"### {grade_color} 등급 **{row['grade']}** · 종합 점수 {row['composite_score']:.1f}"
    )

    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("#### 핵심 지표")
        m1, m2, m3 = st.columns(3)
        m1.metric("승", int(row["w"]))
        m2.metric("패", int(row["l"]))
        m3.metric("승률", f"{row['win_pct']:.3f}")

        st.progress(
            min(row["ops_pctile"] / 100, 1.0),
            text=f"⚔️ 타격력 — OPS {row['ops']:.3f} (역대 상위 {100-row['ops_pctile']:.0f}%)",
        )
        st.progress(
            min(row["era_pctile"] / 100, 1.0),
            text=f"🛡️ 투수력 — ERA {row['era']:.2f} (역대 상위 {100-row['era_pctile']:.0f}%)",
        )
        st.progress(
            min(row["win_pctile"] / 100, 1.0),
            text=f"📊 승률 백분위 — 역대 상위 {100-row['win_pctile']:.0f}%",
        )

    with c2:
        st.markdown("#### 시즌 캐릭터")
        st.success(analysis.style_caption(row))

        st.markdown("#### 🔍 비슷했던 시즌 TOP 5")
        sim = analysis.similar_seasons(df, year, team, n=5)
        sim_disp = sim[["year", "team", "grade", "win_pct", "ops", "era"]].rename(
            columns={"year": "연도", "team": "팀", "grade": "등급",
                     "win_pct": "승률", "ops": "OPS", "era": "ERA"}
        )
        st.dataframe(
            sim_disp,
            column_config={
                "승률": st.column_config.NumberColumn(format="%.3f"),
                "OPS": st.column_config.NumberColumn(format="%.3f"),
                "ERA": st.column_config.NumberColumn(format="%.2f"),
            },
            hide_index=True,
            use_container_width=True,
        )
