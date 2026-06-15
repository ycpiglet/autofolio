---
unit_id: UNIT-TASK-048-001
task_id: TASK-048
task_set_id: TASKSET-UI-OVERHAUL
project_id: PROJECT-AUTOFOLIO
status: completed
horizon: unit
model_tier: worker_standard
escalation_triggers: [high_risk, repeated_failure]
context: "UI 대개편 Phase 4 — 에이전트/IC API + SSE 이벤트 허브 + 에이전트 화면/알림 피드. 데몬 보류 정책 준수: SSE는 요청당(StreamingResponse, 클라이언트 끊김 시 종료), 항시가동 백그라운드 없음, KIS WS opt-in OFF 기본."
inputs:
  - agents/lead_engineer/tasks/TASK-048-ui-overhaul-phase4-agents-sse.md
  - docs/superpowers/specs/2026-06-13-ui-overhaul-design.md
  - app/services/agents.py
  - app/common/logger.py
target_files:
  - app/api/routers/agents.py
  - app/api/routers/stream.py
  - tests/api/test_agents_stream.py
  - web/src/components/domain/AgentMessage.tsx
  - web/src/components/domain/IcTranscript.tsx
  - web/src/components/domain/EventFeed.tsx
  - web/src/app/agents/page.tsx
  - web/src/app/alerts/page.tsx
  - web/e2e/phase4.spec.ts
scope: "에이전트/IC API(list·ask·ic/run·ic/stream·decisions) + SSE 허브(/stream/events) + 프론트 에이전트 화면·IC 트랜스크립트·알림 피드. SSE 요청당, 데몬 미기동, KIS WS opt-in OFF. 주문경로 무관."
acceptance:
  - "GET /agents/list(session), POST /agents/ask·ic/run(require_owner+CSRF)"
  - "GET /agents/ic/stream/{job_id} SSE 재접속 replay+라이브"
  - "GET /stream/events SSE(events.jsonl tail + demo ticker), 클라이언트 끊김 시 종료"
  - "데몬 미기동(per-request StreamingResponse), KIS WS opt-in OFF 기본"
  - "ask/ic-run guest 403 + CSRF"
  - "프론트: 에이전트 화면(ask+IC live), IcTranscript/EventFeed EventSource cleanup on unmount, 알림 피드"
  - "Playwright 프로덕션 모드 전체 통과 + 기존 pytest green"
verification:
  - "python -m pytest tests/ -q --cov=app --cov-fail-under=50"
  - "cd web && npm run lint && npm run build && CI=1 npx playwright test"
  - "python scripts/check_agent_docs.py"
handoff: "백엔드 PR(#80) 머지 후 프론트 화면+SSE 소비. 데몬 보류 준수·SSE cleanup·전체 스위트 통과 보고."
stop_condition: "Phase 4 에이전트/IC/SSE/알림 완료 후 중단. 항시가동 데몬·KIS WS 자동기동 금지. Phase 5는 별도."
depends_on: [UNIT-TASK-045-001, UNIT-TASK-047-001]
---

# UNIT-TASK-048-001 — UI 대개편 Phase 4 (에이전트/IC + 알림 + SSE)

## Context

에이전트·IC 실시간 통합과 SSE 스트리밍. Owner가 항시가동 데몬을 보류했으므로
SSE는 요청당(연결 수명 동안만)으로 구현하고, KIS WS는 opt-in OFF 기본으로 둔다.

## Scope

In scope: 에이전트/IC API + SSE 허브 + 프론트 에이전트 화면/IC 트랜스크립트/알림 피드.

Out of scope: 항시가동 데몬, KIS WS 자동기동, 주문경로 변경, Phase 5(분석/은퇴).

## 실행 단위 (2 서브유닛)

1. **백엔드** (PR #80, merged): `agents.py`(list/ask/ic-run/ic-stream/decisions) + `stream.py`(/stream/events).
   ask·ic-run=require_owner+CSRF(guest LLM 비용 차단). 모든 SSE=StreamingResponse 비동기 제너레이터,
   `request.is_disconnected()` 폴링으로 끊김 시 종료, 항시가동 데몬 없음. IC 잡=asyncio task+executor,
   재접속 시 step replay. KIS WS opt-in OFF 기본. 테스트 22건(행잉 없음).
2. **프론트**: AgentMessage·IcTranscript(EventSource ic/stream)·EventFeed(EventSource /stream/events) — 모두 unmount 시 close.
   /agents(team+ask+IC live+decisions), /alerts(라이브 피드). 폴백 없는 에러 상태. phase4.spec.ts.

## 안전

- SSE per-request, 데몬 미기동, KIS WS opt-in OFF. 주문경로 무관. EventSource 누수 없음(cleanup).

## Verification

```powershell
python -m pytest tests/ -q --cov=app --cov-fail-under=50
cd web; npm run lint; npm run build; $env:CI=1; npx playwright test
python scripts/check_agent_docs.py
```

## Stop Boundary

Phase 4 완료 후 중단. 데몬/WS 자동기동 금지. Phase 5는 별도.

## 완료 기록

완료 시각: 2026-06-15T17:09:35+09:00
검토자: Backend Engineer + UI/UX Designer

**변경 내용:**
- **백엔드** (PR #80): `app/api/routers/agents.py`(GET list, POST ask[owner+CSRF], POST ic/run[owner+CSRF]→job_id, GET ic/stream/{id}[SSE replay+라이브], GET ic/decisions), `app/api/routers/stream.py`(GET /stream/events[SSE: events.jsonl tail + demo ticker]). 모든 SSE=요청당 StreamingResponse, 끊김 시 종료, 데몬 미기동. KIS WS opt-in OFF 기본. 테스트 22건.
- **프론트** (`web/`): AgentMessage, IcTranscript(EventSource ic/stream, unmount close), EventFeed(EventSource /stream/events, unmount close, 연결끊김 상태). /agents(team+ask+IC live progress+past decisions), /alerts(라이브 피드). 폴백 없는 가시 에러 상태.

**검증 결과:**
- `python -m pytest tests/ -q` → 1037 passed, coverage 78.4%
- `npm run lint` clean / `npm run build` 그린 / `CI=1 npx playwright test` 전체 21 passed ×2(login/dashboard/phase3/phase4)
- `python scripts/check_agent_docs.py` → 0 error
- 데몬 미기동·SSE per-request·KIS WS opt-in OFF·EventSource cleanup 확인

## Independent Audit

판정: 통과 — 에이전트/IC/SSE 실시간 통합, 데몬 보류 정책 준수(per-request SSE, WS 자동기동 없음), 전체 프로덕션 E2E 그린.
