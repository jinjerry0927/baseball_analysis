# Baseball Analysis (KBO)

KBO 야구 데이터를 활용한 선수 평가, 팀 분석, 승패 예측 프로젝트.

> 포트폴리오/학습용 MVP. 흥미가 유지되면 졸업작품으로 확장. **실서비스 배포 계획 없음.**

## 🎯 목표

| 기능 | 설명 |
|---|---|
| 선수 평가 | 타자/투수 핵심 스탯 + 동일 포지션 백분위 표시 |
| 팀 분석 | 두 팀의 핵심 지표 레이더 차트 비교 |
| 승패 예측 | 두 팀 선택 → 승률 예측 (로지스틱 회귀 베이스라인) |

## 📅 Phase 1 마일스톤 (5~7주)

- [x] 1주 — 환경 세팅 + STATIZ 스크래퍼 + SQLite 캐시 + 2024시즌 데이터 수집
- [ ] 2주 — EDA 노트북, 데이터 검증
- [ ] 3주 — 선수 평가 화면 + 백분위 (Streamlit)
- [ ] 4주 — 팀 분석 화면 + 레이더 차트
- [ ] 5주 — 승패 예측 모델 (로지스틱) + 시간 분할 검증
- [ ] 6주 — UI 통합 + 다듬기
- [ ] 7주 — README + Streamlit Cloud 배포 + 회고

## 🛠 기술 스택

- **Python 3.11**
- **데이터 수집**: `requests` + `BeautifulSoup` (STATIZ 스크래핑)
- **데이터 처리**: pandas, numpy
- **모델링**: scikit-learn (→ Phase 2에서 xgboost)
- **시각화**: plotly, matplotlib
- **UI**: Streamlit
- **캐싱**: SQLite

## 📁 프로젝트 구조

```
baseball_analysis/
├── data/
│   ├── raw/          # 원본 스냅샷 (gitignore)
│   └── cache/        # SQLite 캐시 (gitignore)
├── notebooks/        # EDA, 모델 실험
├── src/
│   ├── data/         # 수집·캐싱
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

# (이후) Streamlit 앱 실행
streamlit run app/streamlit_app.py
```

## 📊 데이터 소스

- **STATIZ** (https://statiz.sports-conference.com) — 주 데이터 소스, WAR 등 사바메트릭스 포함
- **KBO 공식 기록실** (https://www.koreabaseball.com) — 검증용

### ⚠️ 스크래핑 시 유의

- **robots.txt 확인 필수**: 첫 실행 전 STATIZ의 robots.txt를 확인해 허용된 경로만 접근.
- **요청 간 딜레이 1~2초** + 로컬 SQLite 캐싱으로 같은 페이지 재요청 금지.
- 학습 목적의 개인 사용에 한정. 수집한 데이터 재배포 금지.

## 📌 Phase 2 (조건부 확장)

흥미가 유지되면 진행:

- 다년치 시계열 분석 (선수 성장 곡선)
- XGBoost로 예측 모델 고도화 (선발 투수, 라인업 포함)
- 모델 비교 실험 + 특성 중요도 시각화
- 자체 평가 metric 제안

## 라이선스

학습용 개인 프로젝트.
