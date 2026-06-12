---
type: task
id: TASK-039
status: 보류
owner: Backend Engineer
assignees: [Backend Engineer, Compliance Officer, QA]
priority: High
difficulty: 상
est_hours: 20
est_tokens: 150000
tags: [ui-overhaul, fastapi, trade, settings, safety-gates, phase3, r3-adjacent]
gate: Owner 명시 승인 필수 — state-changing 엔드포인트, R3 인접; blocked by TASK-038
trigger_meeting: Owner 명시 승인 후 개시
audit_log: AUDIT-2026-06-13-001
created: 2026-06-13
created_at: 2026-06-13T01:33:29+09:00
updated_at: 2026-06-13T01:33:29+09:00
---

# TASK-039 UI 대개편 Phase 3 — 매매 + 내역 + 설정 (state-changing + 안전 게이트) ⚠ 최고 리스크

작업 ID: TASK-039
상태: 보류
Owner: Backend Engineer
기록 시각: 2026-06-13T01:33:29+09:00

## ⚠ 보류 사유

이 태스크는 state-changing 엔드포인트와 안전 게이트를 포함해 **Autofolio R3 인접** 작업이다. Owner 명시 승인 없이 구현을 시작하지 않는다.

**시작 전 TASK-042, TASK-043 완료 필수** — 일일 한도 UTC 버그 및 fail-open 버그가 이 Phase 전에 수정되어야 한다.

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
- TASK-042, TASK-043 선행 완료

## 근거 경로

- 디자인 스펙(레포 내 권위 문서): `docs/superpowers/specs/2026-06-13-ui-overhaul-design.md` §Phase 3, §안전 불변식 (원 플랜은 세션 로컬)
- trade 게이트 구현: `app/services/trading.py` (Phase 0 완료)

## Done When

- Owner 명시 승인 수령
- 게이트 테스트 전수 통과
- paper 수동 검증 통과
