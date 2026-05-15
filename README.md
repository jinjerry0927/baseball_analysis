# Baseball Analysis (KBO)

KBO 팀 데이터를 활용한 팀 평가, 팀 분석, 승패 예측 프로젝트.

> 포트폴리오/학습용 MVP. 흥미가 유지되면 졸업작품으로 확장. **실서비스 배포 계획 없음.**

## 🎯 Phase 1 목표 — 팀 단위 분석 (1982~2021)

Kaggle KBO 팀 단위 데이터셋 (타격·투수, 40년치)을 활용.

| 기능 | 설명 |
|---|---|
| 팀 시즌 카드 | 한 팀-시즌 선택 → OPS/ERA/승률 등 핵심 지표가 **KBO 역사 40년 내 백분위** 어디인지 표시 |
| 팀 비교 | 두 팀-시즌의 타격+투수 핵심 지표 레이더 차트 |
| 승패 예측 | 두 팀-시즌 선택 → 승률 예측 (로지스틱 회귀 베이스라인) |

## 📅 Phase 1 마일스톤 (4~5주)

- [x] 1주차 — 환경 세팅, 범용 CSV 로더, Kaggle 팀 데이터 2종(타격/투수) 통합
- [ ] 2주차 — EDA, 40년 추이 시각화, 피처 엔지니어링
- [ ] 3주차 — 팀 시즌 카드 (Streamlit) + 백분위 계산
- [ ] 4주차 — 팀 비교 화면 + 승패 예측 모델
- [ ] 5주차 — UI 통합, Streamlit Cloud 배포, 회고

## 📌 Phase 2 — 선수 단위 분석 (STATIZ 스크래퍼)

Phase 1 마무리 후 진입.

- [ ] STATIZ 스크래퍼 구현 (쿠키 주입 방식, `PoliteClient` 위에)
- [ ] 선수 단위 데이터 수집 (최근 시즌 우선)
- [ ] 선수 카드 (포지션별 백분위, WAR 등 사바메트릭스 포함)
- [ ] 다년치 선수 성장 곡선
- [ ] 모델 고도화 — 선발 투수/라인업까지 입력받는 예측

## 🛠 기술 스택

- **Python 3.11**
- **데이터 처리**: pandas, numpy
- **모델링**: scikit-learn (→ Phase 2에서 xgboost)
- **시각화**: plotly, matplotlib
- **UI**: Streamlit
- **캐싱** (Phase 2 스크래퍼용): SQLite

## 📁 프로젝트 구조

```
baseball_analysis/
├── data/
│   ├── raw/          # Kaggle CSV (gitignore, .gitkeep만 추적)
│   └── cache/        # SQLite 캐시 (Phase 2용, gitignore)
├── notebooks/        # EDA, 모델 실험
├── src/
│   ├── data/         # 로더·캐시·HTTP 클라이언트
│   ├── features/     # 피처 엔지니어링
│   ├── models/       # 학습·예측
│   └── viz/          # 차트 함수
├── app/              # Streamlit 앱
└── tests/
```

## 🚀 시작하기

```powershell
# 가상환경 생성 및 활성화
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 의존성 설치
pip install -r requirements.txt

# EDA 노트북
jupyter notebook notebooks/1_eda.ipynb

# (이후) Streamlit 앱 실행
streamlit run app/streamlit_app.py
```

## 📊 데이터 소스

### Phase 1 — Kaggle (사용 중)
Kaggle에서 받은 팀 단위 CSV 2개를 `data/raw/`에 둠:
- `kbo_team_batting.csv` — 1982~2021 팀 시즌 타격 (323행)
- `kbo_team_pitching.csv` — 1982~2021 팀 시즌 투수 (323행)

### Phase 2 — STATIZ (예정)
- **STATIZ** — KBO 사바메트릭스 (WAR, wRC+, FIP 등). 로그인 필요 → 쿠키 주입으로 인증.
- 로컬 SQLite 캐시 + 1.5초 요청 딜레이 (`PoliteClient`).
- 학습 목적 개인 사용에 한정, 수집 데이터 재배포 금지.

## 라이선스

학습용 개인 프로젝트.
