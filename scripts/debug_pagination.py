"""임시 디버그: KBO 페이지네이션 POST 변형을 시도."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bs4 import BeautifulSoup

from src.data.http_client import PoliteClient
from src.data.kbo_scraper import (
    HITTER_BASIC_PATH,
    RecordQuery,
    _build_url,
    _extract_page_targets,
)


def main():
    c = PoliteClient()
    url = _build_url(HITTER_BASIC_PATH, RecordQuery(sort="HRA_RT"))
    r1 = c.get(url)
    soup1 = BeautifulSoup(r1.content, "lxml")

    targets = _extract_page_targets(soup1)
    print(f"targets: {targets}")

    # Build base form from hidden fields
    base_form: dict[str, str] = {}
    for inp in soup1.find_all("input", type="hidden"):
        n = inp.get("name")
        if n:
            base_form[n] = inp.get("value") or ""
    hf_page_key = [k for k in base_form if k.endswith("hfPage")][0]
    print(f"hfPage key: {hf_page_key}, current value: {base_form[hf_page_key]!r}")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/126.0.0.0 Safari/537.36"
        ),
        "Referer": url,
        "Origin": "https://www.koreabaseball.com",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
        "Cache-Control": "max-age=0",
        "Upgrade-Insecure-Requests": "1",
    }

    # Variations
    variants = []

    # V1: hfPage=2, EVENTTARGET=btnNo2
    v1 = dict(base_form)
    v1[hf_page_key] = "2"
    v1["__EVENTTARGET"] = targets[2]
    v1["__EVENTARGUMENT"] = ""
    variants.append(("hfPage=2 + EVENTTARGET=btnNo2", v1))

    # V2: hfPage=2 only, blank EVENTTARGET
    v2 = dict(base_form)
    v2[hf_page_key] = "2"
    v2["__EVENTTARGET"] = ""
    v2["__EVENTARGUMENT"] = ""
    variants.append(("hfPage=2 only, blank EVENTTARGET", v2))

    # V3: original (EVENTTARGET only, hfPage stays at 1) - the one we tried first
    v3 = dict(base_form)
    v3["__EVENTTARGET"] = targets[2]
    v3["__EVENTARGUMENT"] = ""
    variants.append(("EVENTTARGET=btnNo2, hfPage stays 1", v3))

    # V4: V1 without scriptmanager-like prefix
    v4 = dict(v1)
    # Remove the EVENTVALIDATION to see if it's the issue (it shouldn't be, but for science)
    # v4.pop("__EVENTVALIDATION", None)
    variants.append(("Same as V1 (sanity repeat)", v4))

    for label, form in variants:
        resp = c.session.post(url, data=form, headers=headers, timeout=30)
        soup = BeautifulSoup(resp.content, "lxml")
        table = soup.find("table", class_="tData01")
        print(f"\n[{label}]")
        print(f"  status={resp.status_code}, bytes={len(resp.content)}, has_data_table={table is not None}")
        if table:
            rows = table.find_all("tr")
            first = [td.get_text(strip=True) for td in rows[1].find_all(["th", "td"])]
            print(f"  first row: rank={first[0]} player={first[1]} team={first[2]} AVG={first[3]}")


if __name__ == "__main__":
    main()
