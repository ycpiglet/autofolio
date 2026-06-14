---
type: task
id: TASK-047
status: 보류
owner: Backend Engineer
assignees: [Backend Engineer, Compliance Officer, QA]
priority: High
difficulty: 상
est_hours: 20
est_tokens: 150000
tags: [ui-overhaul, fastapi, trade, settings, safety-gates, phase3, r3-adjacent]
gate: Owner 명시 승인 필수 — state-changing 엔드포인트, R3 인접; blocked by TASK-046
trigger_meeting: Owner 명시 승인 후 개시
audit_log: AUDIT-2026-06-13-007
created: 2026-06-13
created_at: 2026-06-13T01:33:29+09:00
updated_at: 2026-06-13T01:33:29+09:00
---

# TASK-047 UI 대개편 Phase 3 — 매매 + 내역 + 설정 (state-changing + 안전 게이트) ⚠ 최고 리스크

작업 ID: TASK-047
상태: 보류
Owner: Backend Engineer
요청 시각: 2026-06-13
기록 시각: 2026-06-13T01:33:29+09:00
요청자: Owner
수행자: Lead Engineer
의도: UI 대개편 Phase 3 — state-changing 엔드포인트와 안전 게이트 구현 범위를 사전 정의
대상: app/services/trading.py, app/ui/views/trade.py, app/ui/views/history.py, app/ui/views/settings.py (Phase 3 범위)
방법: require_owner 데코레이터·CSRF 미들웨어 추가, DB-backed kill-switch/auto-trading, OrderForm 2단계 ack 구현
감사 로그: AUDIT-2026-06-13-007

## ⚠ 보류 사유

이 태스크는 state-changing 엔드포인트와 안전 게이트를 포함해 **Autofolio R3 인접** 작업이다. Owner 명시 승인 없이 구현을 시작하지 않는다.

**시작 전 TASK-050, TASK-051 완료 필수** — 일일 한도 UTC 버그 및 fail-open 버그가 이 Phase 전에 수정되어야 한다.

## 배경 및 목적

UI 대개편 Phase 3. 가장 리스크가 높은 state-changing 엔드포인트와 안전 게이트를 구현한다. 모든 엔드포인트에 `require_owner`(guest 403) + CSRF 헤더 필수.

## 작업 범위

### state-changing 엔드포인트

- `POST /api/engine/kill-switch` — DB-backed (세션 전용 갭 수정)
- `POST /api/engine/auto-trading` — DB-backed, `require_owner`
- `POST /api/engine/run-once` — single-flight 락 + 409 conflict
- `POST /api/trade/conditions` — 공시 422 / 컴플라이언스 CAUTION 409+ack_token 2단계
- `PUT /api/settings/*`

### 안전 게이트

- 킬스위치/심볼모드 DB-backed 통일: Streamlit에도 동일 PR 적용
- `require_owner` 데코레이터 — guest 403 전수
- CSRF 헤더 검증 미들웨어

### 프론트

- `OrderForm` — 조건 저장 2단계(공시 차단→ack 팝업→재제출)
- `OrderBookLadder`
- `SecretField`
- 설정 5탭
- `/trade`, `/history`, `/settings` 화면

## 완료 기준

- 게이트 테스트: guest 403 전수, kill-switch 200/409, 공시 422, 컴플라이언스 409+ack_token
- paper 환경 수동 검증 (Owner 실행)
- `python -m pytest tests/ -q` green
- `npm run build` 오류 없음
- TASK-050, TASK-051 선행 완료

## 근거 경로

- 디자인 스펙(레포 내 권위 문서): `docs/superpowers/specs/2026-06-13-ui-overhaul-design.md` §Phase 3, §안전 불변식 (원 플랜은 세션 로컬)
- trade 게이트 구현: `app/services/trading.py` (Phase 0 완료)

## Done When

- Owner 명시 승인 수령
- 게이트 테스트 전수 통과
- paper 수동 검증 통과

## v1 이행

이 태스크는 agent_runtime v0.2.0 work-item 스키마(`agent-runtime-work-item/v1`) 계층에 포함된다.
유닛 스펙은 실행 시점에 생성된다 (현재 없음).

- Initiative: `agents/project/initiatives/INIT-UI-OVERHAUL.md`
- Taskset: `agents/project/initiatives/TASKSET-UI-OVERHAUL.md`
