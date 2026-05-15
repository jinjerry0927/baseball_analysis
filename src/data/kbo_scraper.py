"""KBO 공식 사이트(koreabaseball.com) 스크래퍼.

robots.txt가 `/Record/...` 경로를 허용하므로 합법적으로 접근 가능하다.

페이지는 ASP.NET 정적 HTML로 렌더링되어 `requests` + BeautifulSoup으로 충분.
모든 fetch는 `PoliteClient`를 거쳐 1.5초 딜레이 + SQLite 캐시 적용된다.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlencode

import pandas as pd
from bs4 import BeautifulSoup

from .http_client import FetchResult, PoliteClient

BASE_URL = "https://www.koreabaseball.com"

# 기록실 엔드포인트 (브라우저로 확인된 경로)
HITTER_BASIC_PATH = "/Record/Player/HitterBasic/Basic1.aspx"
HITTER_DETAIL_PATH = "/Record/Player/HitterBasic/Basic2.aspx"
PITCHER_BASIC_PATH = "/Record/Player/PitcherBasic/Basic1.aspx"
PITCHER_DETAIL_PATH = "/Record/Player/PitcherBasic/Basic2.aspx"


@dataclass
class RecordQuery:
    """기록실 쿼리 파라미터.

    필드 이름은 KBO 사이트의 form 필드와 일치시켜야 한다.
    빈 문자열은 "전체" 의미. 발견되는 대로 채워나간다.
    """
    sort: str = "HRA_RT"          # 기본: 타율 기준
    season: str = ""              # ""=현재시즌, "2024" 등
    series: str = ""              # 정규시즌/포스트시즌 ("0"=정규?)
    team: str = ""                # 팀 필터 (코드값)
    position: str = ""            # 포지션 필터

    def to_params(self) -> dict[str, str]:
        d = {"sort": self.sort}
        if self.season:
            d["season"] = self.season
        if self.series:
            d["series"] = self.series
        if self.team:
            d["team"] = self.team
        if self.position:
            d["position"] = self.position
        return d


def _build_url(path: str, query: RecordQuery) -> str:
    return f"{BASE_URL}{path}?{urlencode(query.to_params())}"


def fetch_hitter_basic(query: RecordQuery | None = None,
                       client: PoliteClient | None = None) -> FetchResult:
    """타자 기본기록 한 페이지 받기."""
    q = query or RecordQuery()
    c = client or PoliteClient()
    return c.get(_build_url(HITTER_BASIC_PATH, q))


def fetch_pitcher_basic(query: RecordQuery | None = None,
                        client: PoliteClient | None = None) -> FetchResult:
    """투수 기본기록 한 페이지 받기."""
    q = query or RecordQuery()
    c = client or PoliteClient()
    return c.get(_build_url(PITCHER_BASIC_PATH, q))


# ─────────────────────── Parsing ───────────────────────

# 한글/영문 → 캐노니컬 컬럼명 (loader.py와 일관성 유지)
HEADER_CANONICAL: dict[str, str] = {
    "순위": "rank",
    "선수명": "player",
    "팀명": "team",
    "AVG": "avg",
    "G": "g",
    "PA": "pa",
    "AB": "ab",
    "R": "r",
    "H": "h",
    "2B": "2b",
    "3B": "3b",
    "HR": "hr",
    "TB": "tb",
    "RBI": "rbi",
    "SAC": "sac",
    "SF": "sf",
    "BB": "bb",
    "IBB": "ibb",
    "HBP": "hbp",
    "SO": "so",
    "GDP": "gdp",
    "OBP": "obp",
    "SLG": "slg",
    "OPS": "ops",
    "SB": "sb",
    "CS": "cs",
    "MH": "mh",
    "RISP": "risp",
    "PH-BA": "ph_ba",
}


def parse_record_table(html: bytes | str) -> pd.DataFrame:
    """KBO 기록실 페이지의 데이터 테이블을 DataFrame으로 변환.

    표는 class="tData01"로 식별. 헤더는 첫 행, 나머지는 데이터.
    숫자 컬럼은 자동으로 numeric 변환 시도.
    """
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table", class_="tData01")
    if table is None:
        raise ValueError("Data table (class=tData01) not found in HTML")

    rows = table.find_all("tr")
    if len(rows) < 2:
        raise ValueError(f"Expected header + data rows, got {len(rows)}")

    headers_raw = [c.get_text(strip=True) for c in rows[0].find_all(["th", "td"])]
    headers = [HEADER_CANONICAL.get(h, h.lower()) for h in headers_raw]

    data = []
    for r in rows[1:]:
        cells = [c.get_text(strip=True) for c in r.find_all(["th", "td"])]
        if len(cells) != len(headers):
            continue  # skip malformed rows
        data.append(cells)

    df = pd.DataFrame(data, columns=headers)
    # Convert numeric-looking columns, leave text alone
    for col in df.columns:
        if col in ("player", "team"):
            continue
        converted = pd.to_numeric(df[col], errors="coerce")
        # Only adopt the conversion if it didn't lose information
        if converted.notna().sum() >= df[col].astype(bool).sum():
            df[col] = converted
    return df


# ─────────────────────── Pagination (TODO) ───────────────────────
# 페이지네이션은 ASP.NET __doPostBack 기반이라 단순 GET으로는 안 된다.
# 시도한 것 (scripts/debug_pagination.py 참고):
#   1. hfPage=2 + EVENTTARGET=btnNo2  → KBO 에러 페이지 반환
#   2. hfPage=2만 (EVENTTARGET 비움)   → 200 OK지만 페이지 1 데이터
#   3. EVENTTARGET=btnNo2만 (hfPage=1) → 에러 페이지
#   4. 브라우저 User-Agent 추가         → 변화 없음
# KBO가 POST를 검증하는 메커니즘이 더 있어 보임 (XSRF 토큰? Origin 검증?).
# 다음 세션 첫 작업: Playwright(헤드리스 브라우저)로 전환하거나, DevTools에서
# 실제 브라우저 POST 요청을 캡쳐해서 비교 분석.

_PAGE_BUTTON_RE = re.compile(r"__doPostBack\('([^']+\$btnNo(\d+))'")


def extract_page_count(html: bytes | str) -> int:
    """페이지 1 HTML에서 총 페이지 수를 읽는다 (페이지네이션 구현 전 정찰용)."""
    soup = BeautifulSoup(html, "lxml")
    nums = []
    for a in soup.find_all("a", href=True):
        m = _PAGE_BUTTON_RE.search(a["href"])
        if m:
            nums.append(int(m.group(2)))
    return max(nums) if nums else 1
