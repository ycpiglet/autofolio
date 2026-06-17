# Autofolio 할 일 목록 · 백로그

> 현황 스냅샷 + 우선순위 백로그. 로드맵 근거: [PRODUCT_BLUEPRINT.md](PRODUCT_BLUEPRINT.md) §8(P0–P4) · [ORG_PLAN.md](ORG_PLAN.md) §6–7 · [UI_SPEC.md](UI_SPEC.md) §7.
> 갱신: 2026-06-10T23:39 · main=54e9eef · pytest 131 passed · PR #1–#20 완료

---

## ✅ 완료 (2026-06-10 기준)

### 기반 · 프레임워크
- [x] **리브랜딩** — pamc/kis_autotrading_mvp → Autofolio.
- [x] **agent_runtime v0.1.8** — sync apply 27파일. AGENTS.md §6 Autonomous Delivery Lane(자율 PR+머지) 채택. orchestrator_safety_gate·pipeline·message_queue 이식.
- [x] **자율 머지 게이트** — `scripts/auto_merge.py` 운영 중. PR #2/#6/#7/#8/#9 AUTO-MERGE, #1/#3/#5/#10 Owner-merge. MERGE-POLICY.md → ADDENDUM 상태.
- [x] **GitHub Actions CI** — `.github/workflows/test.yml` (pytest + check_agent_docs, PR/main push 트리거).
- [x] **구조화 로깅** — `get_structured_logger/log_event`, `logs/events.jsonl` JSON Lines, `scripts/tail_events.py`.
- [x] **upstream 버그 보고 자동화** — `scripts/report_upstream_bug.py`, EVIDENCE-2026-06-09-001, agent_runtime Issue #5/#6/#7.

### KIS 연동 (P1.1b)
- [x] **자격증명** — paper·prod 키/계좌/엔드포인트 `.env` 입력, `resolve_settings()` 중앙화.
- [x] **KIS Open API 스펙 정본** — `docs/KIS_API_SPEC.md` (멀티에이전트 리서치, 공식 GitHub 교차검증).
- [x] **`KisClient` 5메서드** — get_current_price/get_positions/place_order/cancel_order/get_order_status. 현행 TR ID, rt_cd envelope, EGW00201 재시도. 단위테스트 17개. 라이브 paper 읽기 검증 완료.
- [x] **엔진 market-fallback PENDING 보정** — `_poll_fill()` 헬퍼. KIS 실브로커 PENDING 처리 일관화.
- [x] **paper 전용 주문 스모크** — `scripts/kis_paper_order_smoke.py` (prod 하드가드, 정규장에 사람 직접 실행).
- [x] **paper 자동 실행 스케줄러** — `scripts/run_paper_engine.py` (거래시간 가드, --dry-run, Notifier 연동).

### UI 라이브화 (전체 8화면)
- [x] **홈** — `backend.kpis()`/`recent_fills()` 라이브 KPI·최근 체결.
- [x] **포트폴리오** — `backend.holdings_df()` 실 KIS 잔고, 자산배분 차트·리밸런싱 갭 라이브.
- [x] **매매/주문** — 조건 등록·엔진 실행·주문로그 라이브 탭.
- [x] **내역·손익** — SQLite 주문로그 라이브 표시.
- [x] **분석** — attribution/retro_metrics/allocation_gap 라이브(보유 기반). 백테스트는 퀀트팀 이후 안내.
- [x] **알림** — 주문로그 기반 라이브 피드 (체결✅/취소🚫/오류❌ 아이콘).
- [x] **설정** — auto_enabled 토글 DB 즉시 동기화, 리스크 한도 DB 저장, 종목별 모드 라이브 분기.
- [x] **에이전트** — IC 결정문 파싱→매매 조건 자동 등록(사람 확인), `/retro` 워크플로 연동.

### 자동화 · 알림
- [x] **Notifier** — Telegram+로그 fallback 통합 발송. 체결/오류 자동 발송, run_summary.
- [x] **Telegram 명령봇** — `/status` `/pnl` `/positions` `/conditions` `/engine` `/propose`. allowlist 보안.
- [x] **IC 투자위원회** — 전문가→DA→리스크→PM→CIO→결정 로그(`.autofolio/decisions/`).
- [x] **`/retro` 워크플로** — `scripts/run_retro.py` (Performance Analyst→DA→Risk→Forward Actions, `.autofolio/retro/RETRO_*.md`).
- [x] **IC → 매매 조건 자동 연결** — 결정문 파싱→사람 확인 버튼→`backend.add_condition(created_by="IC")`.

---

## 🎯 다음 (우선순위)

### 1. 실주문 검증 (paper → prod) ★장 시간 중 사람 직접 실행
- [x] **paper 1주 수동 실주문** — 완료(2026-06-12, TASK-023): `kis_paper_order_smoke.py` 주문→조회→취소 성공, `run_paper_engine.py --once` 1주 체결(069500). HTS/앱 화면 대신 KIS API 잔고·체결로 broker-side 교차확인.
- [ ] **실전(prod) 1주 실주문** — paper 검증 후, Owner 명시 승인 후. `KIS_ENV=prod`로 전환.

### 2. 거버넌스 완성
- [ ] `execution-trader` 에이전트 + SKILL.md — 주문 실행 정책·슬리피지·분할매수.
- [ ] `compliance-officer` 에이전트 — 법·세금·공시 준수 게이트.
- [ ] `performance-analyst` 에이전트 SKILL.md + 분석 화면 전용 탭.

### 3. 퀀트 리서치팀
- [ ] `quant-researcher`·`backtest-engineer`·`data-engineer`·`optimization-quant` 에이전트 스캐폴딩.
- [ ] 백테스트 모듈 — point-in-time 데이터, look-ahead/생존편향 방어.
- [ ] 분석 화면 백테스트 탭을 실데이터로.

### 4. 자동 모드 강화
- [ ] **L3 감독형 자동** — 서킷브레이커·일일예산·주문한도 실집행 엔진 반영.
- [ ] 종목별 모드(L0–L4) 실제 엔진 분기 (현재 session_state만).
- [ ] 스케줄러를 백그라운드 데몬으로 — systemd/Windows 서비스 또는 `nohup`.

### 5. 알림 채널 확장
- [ ] Telegram `/approve` `/kill` 명령 (상태 변경 명령, 사람 승인 게이트 필요).
- [ ] Kakao "나에게 보내기", Notion 저널, 일일/주간 요약 리포트 자동화.
- [ ] SSO 실연결 — Google OIDC(`st.login`).

---

## 📋 백로그 (그룹별)

### Wave 1~6 완료 (2026-06-10 오전, PR #15~#20)
- [x] T-27/38/39/41: 서킷브레이커 UI, MVP_SPEC §5, README, Telegram 설정 스크립트
- [x] T-18/01/03/05/07/10: BaseNotifier/Bus, /quote, /ask, /mode, account_summary, watchlist
- [x] T-15/17/02/13/28: Discord, Email SMTP, /alert+price_alerts, /retro, L0-L4 게이트
- [x] T-12/35/29: 거래 저널 DB+UI, data_loader(PIT), backtest(SMA 크로스오버)
- [x] T-30/21/22: 백테스트 실행 UI, PnL 캘린더, 장전 체크리스트
- [x] T-43/45/42: pyproject.toml, CI 커버리지 게이트, review_pr.py


### Wave 7~9 완료 (2026-06-10 오후)
- [x] T-06 홈 자산곡선 라이브화 (backend.asset_curve())
- [x] T-19 IC /approve /ic Telegram 명령
- [x] T-31 시나리오 분석 라이브 (bull/base/bear, holdings 기반)
- [x] T-33 What-if 계산기 (종목 비중 변경 영향)
- [x] T-36 퀀트 시그널 (RSI/SMA/MACD/볼린저, look-ahead 방어)
- [x] T-37 포트폴리오 최적화 (균등비중/역변동성/모멘텀 + 리밸런싱 제안)
- [x] T-40 E2E 통합 테스트 6개 (엔진→DB 전 흐름, 킬스위치·L1 게이트)
- [x] T-44 Dockerfile + docker-compose.yml (app + scheduler 서비스)
- [x] T-16 Notion 어댑터 (IC 결정·회고 DB 기록)
- [x] T-34 Windows Task Scheduler 등록 스크립트
- [x] T-23 Google Sheets 어댑터 (포트폴리오 미러·알림)
- [x] T-20 Attribution Sankey 다이어그램 (plotly, bar chart 폴백)

### KIS API 확장 (P1.2)
- [x] **TASK-010** KIS WebSocket 실시간 (체결통보·현재가·호가) — `kis_ws_client.py` 신규, H0STCNT0/H0STASP0/H0STCNI0·paper H0STCNI9
- [x] **TASK-011** KIS 분봉 데이터 조회 — `inquire-time-itemchartprice`, TR `FHKST03010200`, `get_intraday_chart()`, data_loader, 분석 화면 분봉 차트
- [x] **TASK-012** KIS 장기 거래내역 조회 (3개월+) — TR `CTSC9215R`/`VTSC9215R`, 3개월 경계 분할, 내역 화면 날짜 조회 연결
- [x] **TASK-013** KIS 복수 종목 현재가 배치 조회 — 공식 batch 정본 `intstock-multprice`, 최대 30종목 청크, watchlist 연결
- [x] **TASK-014** KIS 시간외 주문 (장전·장후 단일가) — paper/mock 지원 + prod hardguard
- [x] **TASK-015** KIS 지수 조회 (KOSPI·KOSDAQ·KOSPI200) — `inquire-index-price`, `get_index_price()`, 홈 지수 위젯
- [x] **TASK-016** KIS 기업 재무정보 (PER·PBR·EPS·시가총액) — `inquire-price` valuation 필드 + `finance-ratio`, `get_fundamental()`, ResearchAgent/분석 탭 연결
- [x] **TASK-017** KIS 배당 정보 조회 — 공식 정본 `ksdinfo/dividend`, `get_dividend_info()`, 포트폴리오 예상연배당/배당수익률 표시
- [x] **TASK-018** KIS 호가창 10단계 조회 — `inquire-asking-price-exp-ccn`, `get_order_book()`, 매매 화면 호가/슬리피지 표시
- [x] **TASK-019** KIS 업종별 시세 조회 — 공식 `inquire-index-price` + 업종 master, `get_sector_price()`, 분석 탭 업종 퍼포먼스 표
- [x] **TASK-020** KIS 공시 정보 조회 — 공식 `news-title`, `get_disclosures()`, Compliance 공시 차단 플래그/알림 패널
- [x] **TASK-021** KIS 신용·공매도 주문 — SLL_TYPE paper/mock 지원 + L3/prod hardguard
- [x] **TASK-022** KIS 해외주식 주문 (미국·홍콩 등) — 해외 주문 payload + KRW valuation + prod hardguard
- [x] **TASK-023** UI 엔진 → KIS 실주문 E2E 검증 — 완료(2026-06-12, STATUS.md): paper 주문 smoke + `run_paper_engine.py --once` 1주 체결, SQLite 로그·UI 반영 확인. prod 실전 주문은 별도 R3 승인 필요

### 기술부채 · 정리 (잔여)
- [x] Streamlit runtime 은퇴 — Next.js/FastAPI 전환, legacy code archive.
- [ ] 테스트 커버리지 60%+ (현재 50% 게이트).
- [x] `agent_orchestrator` import 재확인 (v0.1.8 이식됨).
### 개발팀 활용
- [ ] PR/코드리뷰 워크플로 — independent-auditor·qa·lead-engineer 연결.
- [ ] 요구→스펙 흐름 — requirements-interviewer·research-agent 활용.

---

## 진행 표기
`[ ]` 대기 · `[~]` 진행중 · `[x]` 완료 — 사이클마다 갱신.
