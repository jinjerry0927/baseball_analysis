"""Tests for team-season feature engineering."""
from __future__ import annotations

import pandas as pd

from src.features import analysis, team_season


def _toy_data():
    bat = pd.DataFrame([
        {"year": 2020, "team": "A", "g": 144, "pa": 5000, "ab": 4500, "r": 700,
         "h": 1200, "hr": 100, "rbi": 670, "bb": 400, "so": 1000,
         "avg": 0.267, "obp": 0.340, "slg": 0.400, "ops": 0.740},
        {"year": 2020, "team": "B", "g": 144, "pa": 5000, "ab": 4500, "r": 800,
         "h": 1300, "hr": 150, "rbi": 770, "bb": 450, "so": 950,
         "avg": 0.289, "obp": 0.360, "slg": 0.460, "ops": 0.820},
        {"year": 2020, "team": "C", "g": 144, "pa": 5000, "ab": 4500, "r": 600,
         "h": 1100, "hr": 80, "rbi": 570, "bb": 350, "so": 1100,
         "avg": 0.244, "obp": 0.320, "slg": 0.370, "ops": 0.690},
    ])
    pit = pd.DataFrame([
        {"year": 2020, "team": "A", "w": 75, "l": 69, "ip": 1296.0, "era": 4.20,
         "whip": 1.35, "so": 1000, "bb": 400, "hr": 120, "h": 1300, "er": 600},
        {"year": 2020, "team": "B", "w": 85, "l": 59, "ip": 1296.0, "era": 3.80,
         "whip": 1.25, "so": 1100, "bb": 380, "hr": 100, "h": 1200, "er": 550},
        {"year": 2020, "team": "C", "w": 60, "l": 84, "ip": 1296.0, "era": 5.10,
         "whip": 1.45, "so": 900, "bb": 450, "hr": 140, "h": 1400, "er": 730},
    ])
    return bat, pit


def test_merge_and_derive():
    bat, pit = _toy_data()
    df = team_season.merge_team_season(bat, pit)
    assert set(df["team"]) == {"A", "B", "C"}
    assert "win_pct" in df.columns
    b_row = df[df["team"] == "B"].iloc[0]
    assert abs(b_row["win_pct"] - 85 / (85 + 59)) < 1e-9
    # Pitching columns were renamed to avoid collision
    assert "k_pit" in df.columns and "h_allowed" in df.columns


def test_percentiles_and_grade():
    bat, pit = _toy_data()
    df = team_season.add_grade(team_season.add_percentiles(
        team_season.merge_team_season(bat, pit)))
    # Team B has best OPS and ERA -> highest grade
    grades = {row["team"]: row["grade"] for _, row in df.iterrows()}
    assert grades["B"] in ("S", "A")
    assert grades["C"] in ("D", "C")


def test_caption_picks_offense_pitching_balance():
    row_offense = pd.Series({"ops_pctile": 95, "era_pctile": 50, "win_pct": 0.65})
    assert "타선" in analysis.style_caption(row_offense)
    row_pitching = pd.Series({"ops_pctile": 50, "era_pctile": 95, "win_pct": 0.65})
    assert "마운드" in analysis.style_caption(row_pitching)
