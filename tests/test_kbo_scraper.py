"""Tests for KBO 공식 사이트 scraper + parser."""
from __future__ import annotations

import pandas as pd

from src.data.kbo_scraper import parse_record_table


SAMPLE_HTML = b"""
<html><body>
<table class="tData01 tt">
  <tr>
    <th>\xec\x88\x9c\xec\x9c\x84</th>
    <th>\xec\x84\xa0\xec\x88\x98\xeb\xaa\x85</th>
    <th>\xed\x8c\x80\xeb\xaa\x85</th>
    <th>AVG</th><th>G</th><th>HR</th>
  </tr>
  <tr><td>1</td><td>\xeb\xb0\x95\xec\x84\xb1\xed\x95\x9c</td><td>SSG</td>
      <td>0.370</td><td>39</td><td>3</td></tr>
  <tr><td>2</td><td>\xec\x98\xa4\xec\x8a\xa4\xed\x8b\xb4</td><td>LG</td>
      <td>0.358</td><td>39</td><td>9</td></tr>
</table>
</body></html>
""".decode("utf-8").encode("utf-8")


def test_parse_returns_dataframe_with_canonical_columns():
    df = parse_record_table(SAMPLE_HTML)
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, 6)
    assert list(df.columns) == ["rank", "player", "team", "avg", "g", "hr"]


def test_parse_korean_text_decoded_correctly():
    df = parse_record_table(SAMPLE_HTML)
    assert df.iloc[0]["player"] == "박성한"
    assert df.iloc[1]["player"] == "오스틴"
    assert df.iloc[0]["team"] == "SSG"


def test_parse_numeric_columns_typed():
    df = parse_record_table(SAMPLE_HTML)
    assert df["rank"].dtype.kind == "i"          # int
    assert df["avg"].dtype.kind == "f"           # float
    assert df["hr"].dtype.kind == "i"
    # pandas may use StringDtype or object; both mean "text"
    assert df["player"].dtype.kind in ("O",) or str(df["player"].dtype) == "string"


def test_parse_missing_table_raises():
    import pytest
    with pytest.raises(ValueError, match="not found"):
        parse_record_table(b"<html><body>no table here</body></html>")
