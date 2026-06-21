---
type: task
id: TASK-082
display_id: TASK-082
task_uid: 198470ca-4135-4b70-b3d1-087420ef2e92
registered_at: 2026-06-18T18:17:43+09:00
created_at: 2026-06-18T18:17:43+09:00
started_at: 2026-06-18T18:17:43+09:00
updated_at: 2026-06-18T18:17:43+09:00
completed_at: 2026-06-18T18:17:43+09:00
status: 완료
owner: Lead Engineer
assignees: [Lead Engineer, Backend Engineer, UI/UX Designer, QA, Doc Steward]
priority: High
difficulty: 상
est_hours: 3
est_tokens: 30000
tags: [manuals, safety, audit, ui, order-flow, r3]
gate: Owner direct implementation request; no live order, no secret, no external mutation
trigger_meeting: Owner direct request 2026-06-18
audit_log: AUDIT-2026-06-18-008
created: 2026-06-18
---

# TASK-082 In-app manual, risk acknowledgement, and order audit safety

작업 ID: TASK-082
상태: 완료
Owner: Lead Engineer
요청 시각: 2026-06-18T18:17:43+09:00
기록 시각: 2026-06-18T18:17:43+09:00
완료 시각: 2026-06-18T18:17:43+09:00
요청자: Owner
수행자: Lead Engineer, Backend Engineer, UI/UX Designer, QA, Doc Steward
검토자: Lead Engineer self-review + QA perspective
협업 waiver: 단일 세션 내 Owner direct R3 safety implementation. 실주문, secret, prod 실행은 하지 않았다.
의도: 문서 자체보다 앱 화면에서 사용자가 계정 연결, 위험 고지, 책임 동의, 주문 출처, 엔진 헬스를 직접 보고 체득하게 한다.
대상: `docs/manuals`, FastAPI manuals/acknowledgements/engine/trade API, 주문 intent/audit DB, Next manuals/trade/history/settings UI
방법: Markdown asset + API renderer + risk acknowledgement persistence + order intent idempotency + audit event timeline + engine health dashboard
감사 로그: AUDIT-2026-06-18-008
routing_ref: direct-owner-request / TASK-082
selected_model: Codex coding agent
policy_model: AGENTS.md §16 Autofolio R3 Surface; Owner direct approval; no live execution

## 범위

포함:

- 인앱 매뉴얼 asset과 `/manuals` 화면.
- 위험 고지/면책 동의 기록 API.
- 실전 환경에서 동의 없는 조건저장/엔진실행/자동매매 ON/킬스위치 해제 fail-closed.
- `order_intents`, `order_audit_events`, `engine_run_logs`, `user_acknowledgements` append-only 테이블.
- 주문 제출 전 idempotency key 기반 중복 intent 차단.
- 주문 출처 `USER`/`AGENT`/`SCHEDULER` 기록과 UI 표시.
- 엔진 헬스 조회와 history 감사 이벤트 표시.

제외:

- 실제 TOTP 검증 구현.
- 실주문, KIS secret 변경, KIS credential 조회/회전.
- 외부 배포 또는 production DB migration 실행.

## 완료 조건

- [x] 문서 asset이 앱 화면에서 조회된다.
- [x] Owner 전용 문서는 guest에게 노출되지 않는다.
- [x] 위험 고지 동의가 DB에 기록되고 상태 API로 조회된다.
- [x] prod mode critical action은 동의 없으면 428로 막힌다.
- [x] 주문 실행 전 intent/audit event가 남고 중복 intent는 broker 호출 전 차단된다.
- [x] UI가 매뉴얼, 엔진 헬스, 감사 이벤트를 표시한다.

## 완료 내용

수행:

- `docs/manuals/` 7개 문서 asset을 추가했다.
- `app/services/manuals.py`, `app/api/routers/manuals.py`를 추가했다.
- `app/services/acknowledgements.py`, `app/api/routers/acknowledgements.py`를 추가했다.
- DB 스키마에 `user_acknowledgements`, `order_intents`, `order_audit_events`, `engine_run_logs`를 추가했다.
- `OrderFlow`와 `LiveTradingEngine`에 intent/audit/run health 기록을 연결했다.
- `web/src/app/manuals/page.tsx`, trade safety panel, history audit table, settings safety summary를 추가했다.

결과:

- 사용자는 `/manuals`에서 제품/연동/매매/위험/운영 문서를 화면으로 읽고 위험 고지를 기록할 수 있다.
- 매매 화면은 엔진 헬스, stale processing, duplicate intent, 실전 고지 상태를 보여준다.
- 거래 내역 화면은 주문 로그와 별도로 주문 감사 이벤트를 보여준다.
- agent prefill에서 온 조건 저장은 `AGENT` 출처로 기록된다.

## 검증

- `.venv\Scripts\python.exe -m py_compile app\services\manuals.py app\services\acknowledgements.py app\api\routers\manuals.py app\api\routers\acknowledgements.py app\api\routers\engine.py app\api\routers\trade.py app\engine\order_flow.py app\engine\live_trading_engine.py app\database\repositories.py app\api\schemas\__init__.py` -> pass.
- `.venv\Scripts\python.exe -m pytest tests\api\test_manuals_acknowledgements.py tests\unit\test_order_intent_audit.py tests\unit\test_services_shim.py -q` -> 20 passed.
- `.venv\Scripts\python.exe -m pytest tests\api\test_phase3_state.py tests\api\test_trade.py tests\api\test_trade_phase2.py tests\api\test_engine.py tests\unit\test_condition_toctou_cas.py tests\unit\test_engine_market_fallback.py tests\unit\test_order_flow_and_notification_failures.py -q` -> 93 passed.
- `npm run lint` -> pass.
- `npm run build` -> pass, `/manuals` route generated.

## 증거

- `agents/research_agent/notes/EVIDENCE-2026-06-18-006-inapp-manual-risk-audit-safety.md`
- `agents/lead_engineer/reports/BRIEF-2026-06-18-006.md`

## 리뷰

- Lead Engineer: R3 표면 변경은 안전 게이트 강화 범위이며 실주문, secret 변경, 외부 배포는 수행하지 않았다.
- QA: 신규 API/서비스 테스트, 주문 intent/audit 회귀 테스트, 웹 lint/build가 통과했다.
- Doc Steward: `docs/manuals/` asset이 README/docs 색인과 `/manuals` 화면에 연결됐다.

## Independent Audit

판정: 통과

근거:

- 실주문과 secret mutation은 수행하지 않았다.
- R3 표면 변경은 Owner direct request 범위에서 안전 게이트를 강화하는 방향이다.
- prod mode critical action은 risk acknowledgement 없이는 fail-closed 된다.
- 주문 중복 방지는 broker 호출 전 idempotency 차단으로 검증됐다.
