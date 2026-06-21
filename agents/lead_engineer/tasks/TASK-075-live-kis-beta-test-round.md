---
type: task
id: TASK-075
display_id: TASK-075
task_uid: 99f65987-9e03-4167-b59e-c625624583df
registered_at: 2026-06-18T09:37:35+09:00
created_at: 2026-06-18T09:37:35+09:00
started_at: 2026-06-18T09:37:35+09:00
updated_at: 2026-06-18T10:29:10+09:00
completed_at: 2026-06-18T10:29:10+09:00
status: 완료
owner: QA
assignees: [QA, Beta Tester, KIS API Engineer, UI/UX Designer, Lead Engineer]
priority: High
difficulty: 중
est_hours: 4
est_tokens: 80000
tags: [qa, beta, kis, paper, prod-readonly, ui, market-hours]
gate: paper order tests allowed by Owner; prod limited to read-only and no asset-impacting actions
trigger_meeting: Owner direct request 2026-06-18
audit_log: AUDIT-2026-06-18-001
created: 2026-06-18
---

# TASK-075 Live KIS beta test round

작업 ID: TASK-075
상태: 완료
Owner: QA
요청 시각: 2026-06-18T09:37:35+09:00
기록 시각: 2026-06-18T09:37:35+09:00
완료 시각: 2026-06-18T10:29:10+09:00
요청자: Owner
수행자: QA, Beta Tester, KIS API Engineer, UI/UX Designer, Lead Engineer
검토자: QA self-review + Independent Auditor perspective waiver
의도: 정규장 중 KIS/KSI 관련 기능을 모의계좌 중심으로 폭넓게 검증하고, 실전 계좌는 자산에 영향을 주지 않는 읽기 전용 경로만 검증한다.
대상: KIS paper/prod-read-only API, FastAPI/Next UI, order/engine safety gates, beta-style browser exploration, regression tests
방법: 기존 TASK-023/024/035/036 catalog를 재사용하되 최신 Next/FastAPI 표면에서 live smoke, automated tests, beta exploration, evidence 기록을 수행한다.
감사 로그: AUDIT-2026-06-18-001
routing_ref: direct-owner-request / TASK-075
selected_model: Codex coding agent
policy_model: AGENTS.md §16 Autofolio R3 Surface + Owner explicit paper-order request
협업 waiver(사유): 단일 Codex 세션에서 QA/Beta/KIS/UI 관점을 순차 적용했다. 외부 모델/인간 reviewer는 호출하지 않았고, High-priority self-review 한계는 evidence/BRIEF와 자동 게이트로 보완했다.
실측 비용 (시간): 약 52분
실측 비용 (LLM 토큰): unknown

## 범위

포함:

- KIS paper 토큰, 시세, 잔고, 주문내역, 계좌요약, 호가, 분봉, 배치시세, 지수/업종/공시/재무/배당 조회.
- KIS paper 주문 생애주기 및 작은 수량 거래/취소/동기화 테스트.
- paper engine dry-run 및 안전 게이트 회귀.
- prod 토큰과 prod read-only 조회 중 자산 변동이 없는 기능.
- Next/FastAPI API health, 주요 화면, 로그인/게스트/설문/매매/포트폴리오/분석/설정/에이전트 UI 탐색.
- 긴 입력, 빈 입력, 빠른 클릭, 뒤로가기/새로고침, 모바일 뷰포트 같은 beta-style 사용성 탐색.

제외:

- prod 주문, prod 취소, prod 자동매매 ON, prod 모드 전환.
- 신용, 공매도, 파생, 레버리지, 해외/FX/환전, 실전 주문 경로 실사용.
- KIS secret/account/token/cash 금액 원문 출력 또는 기록.
- production deployment, CI workflow, DB schema, secret rotation.

## 초기 테스트 매트릭스

| Area | Case | Evidence target |
|------|------|-----------------|
| KIS auth | paper/prod token smoke | token length only, no token body |
| KIS paper read-only | price, batch, intraday, indices, sector, order book, disclosures, account summary, orders | redacted counts/sources |
| KIS prod read-only | token, price, account summary/orders if credentials allow | redacted counts only |
| KIS paper orders | below-market limit place/status/cancel; transaction soak if safe | broker order tail/status only |
| Engine safety | dry-run once, kill switch/profile/CSRF gates | command outcome |
| API regression | focused KIS/API/engine tests | pytest results |
| UI regression | lint/build/Playwright E2E | npm/Playwright results |
| Beta exploration | desktop/mobile visible flows and edge inputs | BTC or clean-round record |

## 진행 기록

- 2026-06-18T09:37:35+09:00: TASK-075 등록. 정규장 시작 후 Owner가 paper 전수 테스트와 prod read-only 검증을 명시 요청했다.
- 2026-06-18T10:29:10+09:00: KIS paper/prod-read-only, paper order/transaction, engine, API, Next build/E2E, live browser probe 완료. 발견 결함 2건(auth unknown owner auto-create, paper script raw account output)은 코드 수정과 regression test로 닫았다.

## 완료 조건

- [x] 실행한 paper/prod-read-only/KIS/UI 테스트와 제외한 위험 경로가 evidence note에 정리된다.
- [x] 발견한 결함은 evidence의 issue table로 남기고, 안전한 로컬 결함은 즉시 수정한다.
- [x] prod 자산 변동 경로는 실행하지 않았음을 증거에 남긴다.
- [x] `build_task_index`, `generate_views`, `check_agent_docs` 등 기록 게이트를 가능한 범위에서 통과시킨다.

## 완료 기록

완료 시각: 2026-06-18T10:29:10+09:00
검토자: QA perspective + Beta Tester perspective + KIS API Engineer perspective + UI/UX Designer perspective + Lead Engineer perspective + same-session self-review
실측 비용 (시간): 약 1.0h
실측 비용 (LLM 토큰): Codex session local meter unavailable
협업 waiver: single-session env scope. 역할 관점별 review와 automated regression evidence로 대체했다.
routing waiver: main-session scope. selected_model/policy_model telemetry는 Codex harness에서 노출되지 않아 focused tests, E2E, live probe evidence로 대체했다.
결과: TASK-075 완료. KIS paper 중심 검증과 prod read-only 검증은 통과했고, prod 자산 영향 경로는 실행하지 않았다. 발견한 로컬 결함 2건은 fail-closed/auth masking fixes와 regression tests로 닫았다.

원 요청:

- 정규장 중 KIS/KSI 기능을 많은 테스트 케이스와 edge case로 검증.
- paper 계좌를 먼저 쓰고, prod 계좌는 자산 영향 없는 기능만 검증.
- 레버리지 금지.
- beta tester처럼 UI를 직접 탐색.

## 완료 내용

수행:

- KIS paper/prod token smoke.
- KIS paper read-only 17/17, prod read-only 16/16.
- Paper order lifecycle, paper transaction soak, transaction/UI sync analysis, paper engine dry-run/once, paper WebSocket read-only smoke.
- API/KIS/integration/Next lint/build/Playwright E2E regression.
- Production local UI live browser probe: unknown local login rejection, guest login, SSO shell buttons, 8 primary pages, mobile guest flow.
- 발견 결함 수정:
  - unknown local login이 owner 자동가입되는 문제를 `AUTOFOLIO_LOCAL_AUTO_REGISTER=1` opt-in으로 fail-closed 변경.
  - paper order/engine script account 출력 masking.
  - `web/e2e/demo-walkthrough.spec.ts`의 SSE page load hang을 `domcontentloaded` navigation으로 보정.

변경 파일:

- `app/services/auth_service.py`
- `app/services/__init__.py`
- `app/ui/auth.py`
- `docs/UI_SPEC.md`
- `scripts/kis_paper_order_smoke.py`
- `scripts/run_paper_engine.py`
- `tests/api/test_auth.py`
- `tests/api/test_account.py`
- `tests/unit/test_kis_paper_order_smoke.py`
- `web/e2e/demo-walkthrough.spec.ts`
- `agents/research_agent/notes/EVIDENCE-2026-06-18-001-live-kis-beta-test-round.md`
- `agents/lead_engineer/reports/BRIEF-2026-06-18-001.md`

## 검증

검증:

- `.venv\Scripts\python.exe -m pytest tests/api/test_auth.py tests/api/test_account.py tests/unit/test_kis_paper_order_smoke.py -q` -> 29 passed.
- `.venv\Scripts\python.exe -m pytest tests/api/test_health.py tests/api/test_portfolio.py tests/api/test_trade.py tests/api/test_trade_phase2.py tests/api/test_engine.py tests/api/test_analysis.py tests/api/test_profile_survey.py tests/api/test_auth.py tests/api/test_auth_sso.py tests/api/test_account.py -q` -> 124 passed, 11 warnings.
- `.venv\Scripts\python.exe -m pytest tests/unit/test_kis_client.py tests/unit/test_kis_client_cash.py tests/unit/test_kis_auth_cache.py tests/unit/test_kis_buying_power.py tests/unit/test_kis_failure_modes.py tests/unit/test_kis_client_failure_modes.py tests/unit/test_kis_r3_order_paths.py tests/unit/test_kis_paper_order_smoke.py tests/unit/test_kis_paper_transaction_soak.py tests/unit/test_kis_paper_transaction_loop.py tests/unit/test_kis_paper_hold_basket.py tests/unit/test_reconcile_paper_fills.py -q` -> 83 passed.
- `.venv\Scripts\python.exe -m pytest tests/integration/test_paper_scenario_matrix.py tests/integration/test_quant_trading_scenario_catalog.py tests/integration/test_order_lifecycle.py tests/integration/test_portfolio_reality_model.py tests/integration/test_engine_e2e.py -q --durations=10` -> 138 passed, 1 Windows temp SQLite cleanup warning.
- `npm run lint` -> pass.
- `npm run build` -> pass.
- `npm run test:e2e -- e2e/login.spec.ts e2e/demo-walkthrough.spec.ts e2e/dashboard.spec.ts e2e/settings-account.spec.ts e2e/investor-profile.spec.ts e2e/phase3.spec.ts e2e/phase4.spec.ts e2e/analysis.spec.ts --reporter=line` -> 42 passed.
- Live local UI probe on `http://127.0.0.1:3000/login` production server -> unknown local login rejected, guest login OK, 4 SSO buttons visible, 8 primary pages text-visible, mobile guest home/nav text visible.

## 결과

결과: TASK-075 완료. Paper KIS 검증은 통과했고 prod는 읽기 전용만 수행했다. 자산 영향 경로와 레버리지 계열은 실행하지 않았다.

남은 watch:

- Paper cancel response is canceled and open-like count is 0, but immediate direct status reread can still show pending.
- Next dev server HMR/hydration was noisy in headless live probing; production server verification passed.
- Windows temp SQLite cleanup warning remains non-blocking.

## 증거

- `agents/research_agent/notes/EVIDENCE-2026-06-18-001-live-kis-beta-test-round.md`
- `agents/lead_engineer/reports/BRIEF-2026-06-18-001.md`

## 리뷰

- QA review: paper/prod-read-only/KIS/API/Next E2E matrix를 실행했고, prod 주문/취소/자동매매 경로는 제외했다.
- Beta Tester review: production local UI probe에서 unknown local login rejection, guest login, primary pages, mobile flow를 확인했다.
- KIS API Engineer review: paper order lifecycle과 prod read-only 경계를 분리했고 secret/token/account 원문은 기록하지 않았다.
- UI/UX Designer review: demo walkthrough hang은 page load wait 조건을 조정해 안정화했다.
- Lead Engineer review: 발견 결함은 local auth fail-closed와 script output masking으로 좁게 수정했고 TASK/AUDIT/evidence/BRIEF를 연결했다.

## Independent Audit

판정: 통과

근거:

- prod 자산 영향 경로를 실행하지 않았고 read-only 검증으로 제한했다.
- paper 계좌 주문/거래 검증과 API/UI 회귀를 분리해 evidence에 남겼다.
- unknown local login 자동가입 결함은 opt-in으로 fail-closed 전환했다.
- paper script 출력은 account/product code masking을 적용했다.
- focused tests, integration tests, lint/build, Playwright E2E, live UI probe가 통과했다.
