"""연도 드롭다운이 GET 기반인지 POST(postback) 기반인지 확인."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bs4 import BeautifulSoup

html = (Path(__file__).resolve().parents[1] / "data" / "raw" /
        "kbo_hitter_basic_default.html").read_text(encoding="utf-8")
soup = BeautifulSoup(html, "lxml")

# 연도 셀렉트 박스 찾기 (보통 <select>나 그 안에 1982~2026 옵션 있음)
print("== <select> 요소들 ==")
for sel in soup.find_all("select"):
    opts = sel.find_all("option")
    years = [o.get_text(strip=True) for o in opts if o.get_text(strip=True).isdigit()]
    if years:
        print(f"name={sel.get('name')!r}")
        print(f"id={sel.get('id')!r}")
        print(f"onchange={sel.get('onchange', '<none>')[:200]}")
        print(f"sample years: {years[:5]}...{years[-3:]}")
        print(f"first 3 option values: {[o.get('value') for o in opts[:3]]}")
        print()
