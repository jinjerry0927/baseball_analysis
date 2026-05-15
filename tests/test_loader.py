"""Tests for the generic CSV loader's column aliasing and encoding sniff."""
from __future__ import annotations

from pathlib import Path

from src.data import loader


def test_load_batting_renames_korean_columns(tmp_path: Path):
    csv = tmp_path / "bat.csv"
    csv.write_text(
        "선수명,팀,연도,타율,홈런,타점\n"
        "이정후,키움,2023,0.318,6,45\n",
        encoding="utf-8",
    )
    df = loader.load_batting(csv)
    assert set(["player", "team", "year", "avg", "hr", "rbi"]).issubset(df.columns)
    assert df.iloc[0]["player"] == "이정후"
    assert df.iloc[0]["hr"] == 6


def test_load_batting_renames_english_columns(tmp_path: Path):
    csv = tmp_path / "bat.csv"
    csv.write_text(
        "Name,Team,Season,AVG,HR,RBI\n"
        "Player A,Team X,2023,0.300,20,80\n",
        encoding="utf-8",
    )
    df = loader.load_batting(csv)
    assert "player" in df.columns
    assert "year" in df.columns
    assert "avg" in df.columns


def test_sniff_encoding_handles_cp949(tmp_path: Path):
    csv = tmp_path / "bat.csv"
    csv.write_bytes(
        "선수명,팀,홈런\n이정후,키움,6\n".encode("cp949")
    )
    df = loader.load_batting(csv)
    assert df.iloc[0]["player"] == "이정후"
