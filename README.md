# ⚾ KBO Baseball Analysis

KBO(한국야구) 데이터를 활용한 **팀·선수 분석 대시보드**. 포트폴리오/학습용 MVP.

> 데이터 출처: Kaggle 팀 데이터셋 (1982~2021) + KBO 공식 기록실(현재 시즌). 실서비스 배포 계획 없음.

## ✨ 핵심 기능

### 🏆 팀 시즌 대시보드 (1982~2021, 323개 팀-시즌)
- OPS·ERA 백분위 기반 **종합 점수 + S/A/B/C/D 등급**
- 정렬·필터(연도/팀/등급) + 행 클릭 시 상세
- 시즌 캐릭터 자동 코멘트 ("타선의 힘으로 우승", "전 부문 압도" 등)
- 비슷한 시즌 TOP 5 자동 매칭

### 🏏 선수 대시보드 (현재 시즌, 30 타자 + 22 투수)
- 정렬 가능한 리더보드 + 행 클릭 상세
- **선수 비교 탭** — 두 선수 side-by-side, 지표별 🟢 우세 표시
- **팀 필터** — 사이드바에서 팀 선택 시 양 탭 동시 필터링
- 선수 캐릭터 자동 코멘트 ("거포형 슬러거", "에이스급 시즌" 등)

## 🚀 실행

```powershell
# 가상환경
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 의존성
pip install -r requirements.txt

# 통합 대시보드 (팀+선수, 사이드바 nav)
streamlit run app/streamlit_app.py

# EDA 노트북 (탐색용)
jupyter notebook notebooks/1_eda.ipynb
```

## 🛠 기술 스택

- **Python 3.11** · pandas · numpy · scikit-learn
- **데이터 수집**: requests + BeautifulSoup (KBO 공식 사이트, robots.txt 준수)
- **UI**: Streamlit (`st.navigation` 멀티 페이지)
- **시각화**: matplotlib · plotly
- **캐싱**: SQLite (HTTP 응답 캐시, 1.5초 요청 딜레이)
- **테스트**: pytest (12개 테스트, 전부 통과)

## 📁 구조

```
baseball_analysis/
├── app/
│   ├── streamlit_app.py        # st.navigation 진입점
│   └── views/
│       ├── team.py             # 팀 시즌 view
│       └── player.py           # 선수 view (3 tabs: 타자/투수/비교)
├── src/
│   ├── data/                   # 수집·캐시·HTTP 클라이언트·KBO 스크래퍼
│   ├── features/               # team_season·player·analysis
│   ├── models/                 # (예약)
│   └── viz/                    # (예약)
├── notebooks/
│   └── 1_eda.ipynb             # 40년 KBO 추세 EDA
├── data/raw/                   # Kaggle CSV (gitignored)
├── scripts/                    # 일회성 검증/디버그 스크립트
└── tests/                      # pytest
```

## 📊 데이터 출처

| 소스 | 범위 | 비고 |
|---|---|---|
| Kaggle KBO Team Data | 1982~2021 팀 단위 (타격+투수) | 정적 CSV |
| KBO 공식 기록실 (`koreabaseball.com/Record`) | 현재 시즌 선수 (페이지 1) | robots.txt 허용 경로 |

## ⚠️ 알려진 제한 (KBO 사이트 anti-bot)

KBO 사이트의 다음 동작은 ASP.NET WebForms POST(`__doPostBack`)로만 가능한데, 이 POST가 anti-bot으로 차단됨 (`requests` 및 Playwright 헤드리스 모두 시도):

- ❌ **페이지네이션** (페이지 2+ 접근, 31~55위 선수)
- ❌ **연도 변경** (1982~2025 과거 시즌 선수 데이터)
- ❌ **팀/포지션 필터** (서버 사이드)

다음 방법으로는 가능할 수 있음 (이번 프로젝트 범위 밖):
- Playwright **headful 모드** + 사용자 인터랙션
- `playwright-stealth` 플러그인 시도
- 헤드리스 핑거프린팅 우회

검증 시도 기록: `scripts/debug_pagination.py`, `scripts/test_playwright_pagination.py`.

## 🧪 테스트

```powershell
pytest tests/ -v
# 12 passed
```

- 캐시 round-trip / TTL 만료
- 로더 컬럼 alias (한·영, UTF-8/CP949 인코딩)
- 팀 시즌 merge·percentile·grade 로직
- KBO HTML 파서 (한국어 디코딩, 숫자 컬럼 타이핑)

## 🛣️ 가능한 확장 (향후)

흥미가 다시 생기면:
- Playwright headful + 수동 인터랙션으로 역사 데이터 확보
- 자체 사바메트릭스 metric 시도 (WAR 근사)
- 졸업작품용: 경기 단위 데이터 수집 → 실시간 승률 예측

## 라이선스

학습/포트폴리오 개인 프로젝트.
