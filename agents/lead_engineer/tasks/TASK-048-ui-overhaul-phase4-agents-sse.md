---
type: task
id: TASK-048
status: 완료
owner: Backend Engineer
assignees: [Backend Engineer, UI/UX Designer]
priority: Medium
difficulty: 중
est_hours: 12
est_tokens: 90000
tags: [ui-overhaul, sse, agents, ic, notifications, phase4]
gate: 선행 TASK-047 완료 전 착수 불가; 착수 전 선행 완료 확인 review 필요
trigger_meeting: TASK-047 완료 후 자동 개시
audit_log: AUDIT-2026-06-13-007
created: 2026-06-13
created_at: 2026-06-13T01:33:29+09:00
updated_at: 2026-06-13T01:33:29+09:00
---

# TASK-048 UI 대개편 Phase 4 — 에이전트/IC + 알림 + SSE

작업 ID: TASK-048
상태: 완료
Owner: Backend Engineer
요청 시각: 2026-06-13
기록 시각: 2026-06-13T01:33:29+09:00
요청자: Owner
수행자: Lead Engineer
의도: UI 대개편 Phase 4 — 에이전트·IC 실시간 통합과 SSE 스트리밍 구현 범위 정의
대상: app/brokers/kis/kis_ws_client.py, app/common/logger.py, FastAPI SSE 엔드포인트 신규 파일 (Phase 4 범위)
방법: 단일 SSE 허브(/api/stream/events) 구현, IC 백그라운드 잡 + SSE 진행 스트림, 에이전트 ask API 추가
감사 로그: AUDIT-2026-06-13-007

## 배경 및 목적

UI 대개편 Phase 4. 에이전트 실시간 통합과 SSE 스트리밍을 구현한다. Phase 3 이후 state-changing 게이트가 완전히 정착한 상태에서 진행.

## 작업 범위

### 백엔드 SSE

- `/api/stream/events` — 단일 SSE 허브
  - `logs/events.jsonl` tail 크로스 프로세스 브리지
  - KIS WS opt-in (price/orderbook)
  - 데모 ticker (목 데이터 스트림)
  - 이벤트 타입: `price`, `orderbook`, `fill`, `engine`
- `GET /api/agents/list` — 에이전트 목록
- `POST /api/agents/ask` — 에이전트 질의
- `POST /api/agents/ic/run` — IC 백그라운드 잡 + SSE 진행 스트림 (`ic.py run_ic` progress 콜백 대체)

### 프론트

- `AgentMessage` 컴포넌트
- IC 트랜스크립트 뷰어
- 알림 피드 (`/notifications`)
- `/agents` 화면 — 에이전트 팀 상태 + IC 실행

### 사전 스파이크 (구현 전 검증)

- IC 장기실행 SSE 재접속 복원 가능성 확인
- KIS WS single-owner 아키텍처 유지 검증

## 완료 기준

- `GET /api/stream/events` SSE 연결 + 이벤트 수신 테스트 green
- 에이전트 ask Playwright 통과
- IC run SSE 진행 Playwright 통과
- 알림 피드 렌더 확인
- `npm run build` 오류 없음

## 근거 경로

- 디자인 스펙(레포 내 권위 문서): `docs/superpowers/specs/2026-06-13-ui-overhaul-design.md` §Phase 4 (원 플랜은 세션 로컬)
- KIS WS: `app/brokers/kis/kis_ws_client.py`
- 이벤트 로그: `app/common/logger.py` (events.jsonl)

## Done When

- SSE 이벤트 스트림 e2e 테스트 통과
- 에이전트/IC 화면 Playwright green

## v1 이행

이 태스크는 agent_runtime v0.2.0 work-item 스키마(`agent-runtime-work-item/v1`) 계층에 포함된다.
유닛 스펙은 실행 시점에 생성된다 (현재 없음).

- Initiative: `agents/project/initiatives/INIT-UI-OVERHAUL.md`
- Taskset: `agents/project/initiatives/TASKSET-UI-OVERHAUL.md`
- Unit spec: `agents/lead_engineer/tasks/units/TASK-048/UNIT-TASK-048-001.md`

## 완료 기록

완료 시각: 2026-06-15T17:09:35+09:00
검토자: Backend Engineer + UI/UX Designer

## 증거

- **백엔드** (PR #80, merged): `agents.py`(GET list[session], POST ask·ic/run[require_owner+CSRF], GET ic/stream/{id}[SSE replay+라이브], GET ic/decisions), `stream.py`(GET /stream/events[SSE: events.jsonl tail + demo ticker]). 테스트 22건. pytest 1037 passed.
- **프론트** (`web/`): AgentMessage·IcTranscript(EventSource ic/stream)·EventFeed(EventSource /stream/events) — 전부 unmount 시 close. /agents(team+ask+IC live progress+past decisions), /alerts(라이브 피드). 폴백 없는 가시 에러 상태.
- 검증: pytest 1037/coverage 78.4%, npm lint·build 그린, `CI=1 npx playwright test` 전체 21 passed ×2, check_agent_docs 0 error.

## 리뷰

- **데몬 보류 정책 준수**(Owner): 모든 SSE는 요청당 `StreamingResponse` — 연결 수명 동안만, `request.is_disconnected()`로 끊김 시 종료. 항시가동 백그라운드/데몬 **없음**. IC 잡=asyncio task+executor(데몬 스레드 아님). **KIS WS opt-in OFF 기본**(자동기동 안 함).
- **비용/권한**: ask·ic-run은 require_owner+CSRF로 guest/demo의 LLM 호출 차단. read/stream은 session(guest 데모 가능).
- **안전**: 주문경로 무관(에이전트/IC는 리서치/심의, 매매상태 미변경). EventSource 누수 없음(useRef+cleanup).
- **한계(정직)**: Playwright SSE는 streamed-body route-mock(실 백엔드 미기동); 실 LLM 키 없으면 ask/IC는 stub. 실 SSE 장기실행 재접속은 백엔드 replay 로직+수동 검증 영역.

