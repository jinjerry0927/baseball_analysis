"""Find all sort keys available on the KBO hitter basic page."""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bs4 import BeautifulSoup

html = (Path(__file__).resolve().parents[1] / "data" / "raw" /
        "kbo_hitter_basic_default.html").read_text(encoding="utf-8")
soup = BeautifulSoup(html, "lxml")

print("== Sort links (?sort=KEY in href) ==")
sort_keys = []
for a in soup.find_all("a", href=True):
    href = a["href"]
    if "?sort=" in href:
        txt = a.get_text(strip=True)
        key = href.split("sort=")[1].split("&")[0]
        sort_keys.append((txt, key, href))
        print(f"  {txt!r:8} key={key:12}  href={href}")

print(f"\nTotal unique sort keys: {len(set(k for _, k, _ in sort_keys))}")
