"""각 KBO 엔드포인트의 헤더만 확인 (큰 출력 회피)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bs4 import BeautifulSoup

from src.data.kbo_scraper import (
    fetch_hitter_basic,
    fetch_hitter_detail,
    fetch_pitcher_basic,
    fetch_pitcher_detail,
)

endpoints = [
    ("HitterBasic",   fetch_hitter_basic),
    ("HitterDetail",  fetch_hitter_detail),
    ("PitcherBasic",  fetch_pitcher_basic),
    ("PitcherDetail", fetch_pitcher_detail),
]

for name, fn in endpoints:
    r = fn()
    soup = BeautifulSoup(r.content, "lxml")
    t = soup.find("table", class_="tData01")
    if t is None:
        print(f"{name:14} bytes={len(r.content):>6} from_cache={r.from_cache} HEADERS=<no table>")
        continue
    rows = t.find_all("tr")
    headers = [c.get_text(strip=True) for c in rows[0].find_all(["th", "td"])]
    print(f"{name:14} bytes={len(r.content):>6} from_cache={r.from_cache} "
          f"rows={len(rows)-1} cols={len(headers)}")
    print(f"  headers: {headers}")
