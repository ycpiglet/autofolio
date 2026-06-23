---
type: task
id: TASK-106
display_id: TASK-106
task_uid: 6b820f0b-f62b-493a-b63b-6d4b70a01c00
registered_at: 2026-06-19T15:09:12+09:00
created_at: 2026-06-19T15:09:12+09:00
started_at: 2026-06-19T15:09:12+09:00
updated_at: 2026-06-19T15:09:12+09:00
completed_at: 2026-06-19T15:09:12+09:00
status: 완료
owner: Backend Engineer
assignees: [Backend Engineer, QA, Lead Engineer]
priority: High
difficulty: 중
est_hours: 1
est_tokens: 16000
tags: [auth, membership, read-scope, app-user, local-prototype]
initiative_id: INIT-MEMBERSHIP-ACCESS
task_set_id: TASKSET-MEMBERSHIP-ACCESS
gate: local API authorization boundary only; no production DB, deploy, bank/payment API, real account number, KIS/order/risk/prod/secret change
trigger_meeting: Owner direct request 2026-06-19
audit_log: AUDIT-2026-06-19-016
created: 2026-06-19
---

# TASK-106 Membership app-user read boundary

작업 ID: TASK-106
상태: 완료
Owner: Backend Engineer
요청 시각: 2026-06-19T15:09:12+09:00
기록 시각: 2026-06-19T15:09:12+09:00
완료 시각: 2026-06-19T15:09:12+09:00
요청자: Owner
수행자: Backend Engineer + QA + Lead Engineer perspective (Codex)
검토자: Backend Engineer self-review + QA perspective + Lead Engineer perspective
협업 waiver: 단일 세션 범위 작업. 제품 read API의 local authorization dependency만 승인 사용자 전용으로 올렸으며 production DB/payment/deploy/secret 없음.
routing_ref: TASKSET-MEMBERSHIP-ACCESS / TASK-106
selected_model: Codex coding agent
policy_model: AGENTS.md §6 R1/R2 local reversible implementation; AGENTS.md §16 R3 surfaces avoided
실측 비용 (시간): 약 0.5h
실측 비용 (LLM 토큰): unknown
의도: 게스트 세션이 남아 있어도 포트폴리오/마켓/분석/매매/엔진/에이전트/매뉴얼 같은 제품 read surface를 사용할 수 없게 한다.
대상: `app/api/routers/*` read dependencies, API contract tests
방법: 제품 read endpoints의 dependency를 `require_session`에서 `require_app_user`로 올렸다. Owner/member는 200, guest는 403, anonymous는 401이라는 계약으로 테스트를 갱신했다.
감사 로그: AUDIT-2026-06-19-016

## 범위

포함:

- portfolio read: holdings, kpis, asset-curve, allocation-gap, overview.
- market read: indices, watchlist, price, fundamental, order-book, intraday, sectors, disclosures, symbols.
- analysis read: attribution, retro, daily-pnl, backtest, VaR, scenario, what-if.
- trade read: recent fills, conditions, orders.
- engine status read.
- agents read/SSE: list, research, premarket summary, IC stream, decisions.
- stream/events SSE.
- account/profile/manuals/acknowledgement status read.
- tests now use `member_client` for approved-user read coverage and assert representative guest 403 cases.

제외:

- production DB/Supabase schema or migration.
- external deploy.
- real payment/bank API/open-banking/PG.
- 실제 계좌번호, 고객 입금기록, 고객 PII repo 저장.
- user_id 단위 포트폴리오/엔진/주문 데이터 격리 완성.
- KIS/order/risk/prod/secret 변경.

## 완료 조건

- [x] product read endpoints require owner/member roles.
- [x] guest sessions receive 403 on representative product read endpoints.
- [x] anonymous callers still receive 401.
- [x] members can read product data without Owner/admin role.
- [x] owner-only mutations remain owner-only.
- [x] API, lint, build, and focused E2E checks pass.

## 완료 기록

완료일: 2026-06-19
결과: Local prototype now matches the membership premise more closely: having a signed session is not enough to use the product; the caller must be an approved app user (`owner` or `member`).
변경 파일: `app/api/routers/account.py`, `app/api/routers/acknowledgements.py`, `app/api/routers/agents.py`, `app/api/routers/analysis.py`, `app/api/routers/engine.py`, `app/api/routers/manuals.py`, `app/api/routers/market.py`, `app/api/routers/portfolio.py`, `app/api/routers/profile.py`, `app/api/routers/stream.py`, `app/api/routers/trade.py`, `tests/api/*` focused contract tests.
이슈: This does not create per-user data isolation. Members can authenticate to the product surface, but the underlying portfolio/engine data model is still single-owner/local until TASK-087 production schema/RLS work.
다음 담당자 인수 사항: TASK-087에서 Supabase/RLS schema, user_id ownership columns, per-user broker/token storage, and per-user engine/safety isolation을 설계한다.

## 완료 내용

- Product read dependencies were moved from session-only to approved app-user.
- Tests distinguish three states: anonymous 401, guest 403, member/owner 200.
- Internal guest fixtures remain usable only for auth/gate regression, not product access success.

## 결과

TASK-106 완료. 전체 membership product goal은 아직 production schema, deployment, payment provider, and user_id isolation이 남아 있어 active 상태로 유지한다.

## 증거

- `app/api/deps.py`
- `app/api/routers/portfolio.py`
- `app/api/routers/market.py`
- `app/api/routers/analysis.py`
- `app/api/routers/agents.py`
- `tests/api/conftest.py`
- `tests/api/test_portfolio.py`
- `tests/api/test_agents_stream.py`

## 리뷰

- Backend Engineer self-review: read surface는 owner/member만 허용하고, Owner/admin mutation은 기존 `require_owner_csrf`로 유지했다.
- QA perspective: full API suite and focused E2E confirm anonymous/guest/member boundaries.
- Lead Engineer perspective: production DB, deploy, real payment/bank API, KIS/order/risk/secret 경계는 건드리지 않았다.

## Independent Audit

판정: 통과

Same-session audit note: local authorization boundary hardening only. This prevents guest sessions from reading product surfaces, but does not prove production multi-tenant isolation.

## 검증

- `.venv\Scripts\python.exe -m pytest tests/api/test_account.py tests/api/test_portfolio.py tests/api/test_market.py tests/api/test_market_phase2.py tests/api/test_engine.py tests/api/test_trade.py tests/api/test_trade_phase2.py -q` -> 94 passed, 2 warnings
- `.venv\Scripts\python.exe -m pytest tests/api/test_analysis.py tests/api/test_agents_research.py tests/api/test_agents_stream.py tests/api/test_premarket_summary.py tests/api/test_manuals_acknowledgements.py tests/api/test_profile_survey.py -q` -> 105 passed, 14 warnings
- `.venv\Scripts\python.exe -m pytest tests/api -q` -> 325 passed, 19 warnings
- `npm run lint` in `web/` -> pass
- `npm run build` in `web/` -> pass
- `npm run test:e2e -- e2e/login.spec.ts --reporter=line` -> 5 passed
- `npm run test:e2e -- e2e/dashboard.spec.ts --reporter=line` -> 6 passed
