# Autofolio 할 일 목록 · 백로그

> 현황 스냅샷 + 우선순위 백로그. 로드맵 근거: [PRODUCT_BLUEPRINT.md](PRODUCT_BLUEPRINT.md) §8(P0–P4) · [ORG_PLAN.md](ORG_PLAN.md) §6–7 · [UI_SPEC.md](UI_SPEC.md) §7.
> 갱신: 2026-06-10T07:52 · main=23218a1 · pytest 87 passed · PR #1–#10 완료

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
- [ ] **paper 1주 수동 실주문** — `! python scripts/kis_paper_order_smoke.py` (정규장 09:00~15:30). 체결조회·취소 생애주기 확인 후 기록.
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

### 기술부채 · 정리
- [ ] MVP_SPEC §5 구조도 업데이트 (신규 셸·agents_runtime·IC 반영).
- [ ] `streamlit_app.py`(구 MVP) vs `autofolio_app.py`(신 셸) 역할 정리 또는 통합.
- [ ] 테스트 커버리지 확대 — 리스크·backend 어댑터 AppTest, 엔진 E2E.
- [ ] `agent_orchestrator` import 오류 해소 — orchestrator_safety_gate v0.1.8에 이식됨, 재확인 필요.

### 개발팀 활용
- [ ] PR/코드리뷰 워크플로 — independent-auditor·qa·lead-engineer 연결.
- [ ] 요구→스펙 흐름 — requirements-interviewer·research-agent 활용.

---

## 진행 표기
`[ ]` 대기 · `[~]` 진행중 · `[x]` 완료 — 사이클마다 갱신.
