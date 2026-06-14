---
type: task
id: TASK-059
status: 대기
owner: Backend Engineer
assignees: [Backend Engineer, QA]
priority: Medium
difficulty: 낮
est_hours: 2
est_tokens: 15000
tags: [bug, security, session, logout]
gate: -
trigger_meeting: 다음 사이클
audit_log: AUDIT-2026-06-14-001
created: 2026-06-14
created_at: 2026-06-14T00:00:00+09:00
updated_at: 2026-06-14T00:00:00+09:00
---

# TASK-059 fix: logout() 미완전 세션 상태 초기화 (state.py)

작업 ID: TASK-059
상태: 대기
Owner: Backend Engineer
요청 시각: 2026-06-14
기록 시각: 2026-06-14T00:00:00+09:00
요청자: Owner
수행자: Backend Engineer
의도: logout() 함수에서 모든 세션 상태를 DEFAULTS로 완전 초기화
대상: app/ui/state.py logout() 함수
방법: DEFAULTS 전체 키 순회 초기화 구현 + 안전 키 명시 검증 + 재로그인 미유지 테스트 추가
감사 로그: AUDIT-2026-06-14-001

## 버그 내용

`app/ui/state.py`의 `logout()` 함수가 `kill_switch`, `mode`, `symbol_modes`, `auto_enabled` 등의 핵심 거래 설정 키를 초기화하지 않음.

**증상**: 로그아웃 후 다른 사용자로 로그인하면 이전 세션의 kill_switch 상태, 자동매매 모드, 종목별 설정이 그대로 남아있어 보안 및 안전 위험.

**원인**: `logout()`이 일부 키만 초기화하고 DEFAULTS 딕셔너리의 전체 키를 순회하지 않음.

## 수정 방향

1. `logout()`에서 `DEFAULTS` 딕셔너리의 전체 키를 순회하며 `st.session_state`를 DEFAULTS 값으로 초기화
2. 특히 안전 관련 키(`kill_switch`, `auto_enabled`, `mode`, `symbol_modes`) 명시적 초기화 검증
3. 재로그인 시 이전 상태 미유지 확인 테스트 추가

## 완료 기준

- `logout()` 후 모든 세션 상태 DEFAULTS로 초기화
- 재로그인 시 이전 상태 미유지
- `python -m pytest tests/ -q` green

## Done When

- `logout()` 후 모든 세션 상태 DEFAULTS로 초기화
- 재로그인 시 이전 상태 미유지

## v1 이행

이 태스크는 agent_runtime v0.2.0 work-item 스키마(`agent-runtime-work-item/v1`) 계층에 포함된다.
유닛 스펙은 실행 시점에 생성된다 (현재 없음).

- Initiative: `agents/project/initiatives/INIT-PRODUCT-MATURITY.md`
- Taskset: `agents/project/initiatives/TASKSET-PRODUCT-MATURITY.md`
