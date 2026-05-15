"""1회 테스트: Playwright로 KBO 페이지 2 받기.

성공 기준: 페이지 2의 데이터 표가 있고, 31번 이후 순위 선수가 보임.
실패하면 메시지 출력하고 종료. 절대 retry 루프 안 만든다.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

from playwright.sync_api import sync_playwright


URL = "https://www.koreabaseball.com/Record/Player/HitterBasic/Basic1.aspx"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/126.0.0.0 Safari/537.36",
            locale="ko-KR",
        )
        page = ctx.new_page()

        print(f"[1] Loading: {URL}")
        page.goto(URL, wait_until="networkidle", timeout=30000)

        # Confirm page 1 loaded
        first_player = page.locator("table.tData01 tbody tr").first.locator("td").nth(1).text_content()
        print(f"[2] Page 1 first player: {first_player}")

        # Find the page 2 link — scope to .paging div so we don't grab "2" elsewhere
        print("[3] Looking for page 2 link inside .paging...")
        page_2_link = page.locator("div.paging a", has_text="2").first
        print(f"    target href: {page_2_link.get_attribute('href')}")
        page_2_link.click()
        page.wait_for_load_state("networkidle", timeout=15000)

        # Check page 2 first row
        first_player_p2 = page.locator("table.tData01 tbody tr").first.locator("td").nth(1).text_content()
        first_rank_p2 = page.locator("table.tData01 tbody tr").first.locator("td").nth(0).text_content()
        row_count = page.locator("table.tData01 tbody tr").count()

        print(f"[4] Page 2 first row: rank={first_rank_p2!r}, player={first_player_p2!r}")
        print(f"    Page 2 row count: {row_count}")

        if first_player_p2 and first_player_p2 != first_player:
            print("\n✅ SUCCESS — Playwright can navigate KBO pagination")
        else:
            print("\n❌ FAIL — Page 2 didn't actually load different data")

        browser.close()


if __name__ == "__main__":
    main()
