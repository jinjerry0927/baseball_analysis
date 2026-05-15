"""4개 엔드포인트 모두 parse → DataFrame까지 깨끗하게 되는지 확인."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data.kbo_scraper import (
    fetch_hitter_basic,
    fetch_hitter_detail,
    fetch_pitcher_basic,
    fetch_pitcher_detail,
    parse_record_table,
)

endpoints = [
    ("HitterBasic",   fetch_hitter_basic),
    ("HitterDetail",  fetch_hitter_detail),
    ("PitcherBasic",  fetch_pitcher_basic),
    ("PitcherDetail", fetch_pitcher_detail),
]

for name, fn in endpoints:
    r = fn()
    df = parse_record_table(r.content)
    print(f"{name:14} shape={df.shape}  top1: rank={df.iloc[0]['rank']} player={df.iloc[0]['player']} team={df.iloc[0]['team']}")
    # Check that no header stayed in raw Korean (means HEADER_CANONICAL covered it)
    untranslated = [c for c in df.columns if any(ord(ch) > 127 for ch in c)]
    if untranslated:
        print(f"  ⚠️  untranslated columns: {untranslated}")
    else:
        print(f"  ✓ all columns canonicalized")
