---
type: task
id: TASK-048
status: 대기
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
상태: 대기
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
