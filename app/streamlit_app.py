"""KBO 분석 대시보드 — 통합 진입점.

실행: streamlit run app/streamlit_app.py
사이드바에서 팀/선수 페이지를 선택할 수 있습니다.
"""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

st.set_page_config(
    page_title="KBO 분석 대시보드",
    page_icon="⚾",
    layout="wide",
)

from app.views.team import team_view  # noqa: E402
from app.views.player import player_view  # noqa: E402

pg = st.navigation([
    st.Page(team_view, title="팀 시즌 (1982~2021)", icon="🏆", default=True),
    st.Page(player_view, title="선수 (현재 시즌)", icon="🏏"),
])
pg.run()
