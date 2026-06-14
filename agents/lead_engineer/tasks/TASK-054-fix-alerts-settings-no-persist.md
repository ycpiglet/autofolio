---
type: task
id: TASK-054
status: 완료
owner: UI/UX Designer
assignees: [UI/UX Designer, QA]
priority: High
difficulty: 중
est_hours: 4
est_tokens: 30000
tags: [bug, ui, alerts, persistence]
gate: -
trigger_meeting: 즉시 처리 권고
audit_log: AUDIT-2026-06-14-001
created: 2026-06-14
created_at: 2026-06-14T00:00:00+09:00
updated_at: 2026-06-14T13:09:51+09:00
---

# TASK-054 fix: 알림 채널 토글/규칙 설정 미저장 (alerts.py)

작업 ID: TASK-054
상태: 완료
Owner: UI/UX Designer
요청 시각: 2026-06-14
기록 시각: 2026-06-14T00:00:00+09:00
요청자: Owner
수행자: UI/UX Designer
의도: alerts.py 채널 토글과 알림 규칙 설정 변경 시 DB 저장 경로 구현
대상: app/ui/alerts.py, app/services/alerts.py (또는 store 레이어)
방법: on_change 핸들러 추가 + DB 저장/로드 경로 구현 + 재로딩 후 설정 유지 pytest 검증
감사 로그: AUDIT-2026-06-14-001

## 버그 내용

`app/ui/alerts.py`의 채널 토글(Telegram/Discord/Email/Notion/Sheets)과 알림 규칙 multiselect이 save 핸들러 없이 렌더만 됨.

**증상**: 사용자가 채널 토글을 변경하거나 알림 규칙을 선택해도 새로고침 시 원래 상태로 복귀.

**원인**: on_change 또는 on_click 저장 핸들러가 없어 변경 사항이 Streamlit session_state에만 머물고 DB/파일에 기록되지 않음.

## 수정 방향

1. 채널 토글 각각에 `on_change` 핸들러 추가 → `app/services/alerts.py` 또는 store 통해 DB 저장
2. 알림 규칙 multiselect에 `on_change` 핸들러 추가 → DB 저장
3. 페이지 진입 시 DB에서 저장된 설정 로드하여 초기값으로 사용

## 완료 기준

- 채널 토글 상태 DB 저장
- 규칙 multiselect 저장
- 새로고침 후 설정 유지
- `python -m pytest tests/ -q` green
- `python scripts/check_agent_docs.py` 0 error

## Done When

- 채널 토글 상태 DB 저장
- 규칙 multiselect 저장
- 새로고침 후 설정 유지

## v1 이행

이 태스크는 agent_runtime v0.2.0 work-item 스키마(`agent-runtime-work-item/v1`) 계층에 포함된다.
유닛 스펙: `agents/lead_engineer/tasks/units/TASK-054/UNIT-TASK-054-001.md`

- Initiative: `agents/project/initiatives/INIT-PRODUCT-MATURITY.md`
- Taskset: `agents/project/initiatives/TASKSET-PRODUCT-MATURITY.md`

## 완료 기록

완료 시각: 2026-06-14T13:09:51+09:00
검토자: UI/UX Designer / QA

## 증거

- `app/services/connections.py`: `get_alert_settings()`, `save_alert_settings()` 추가. vault `"alert_settings"` 키 사용 (connections 데이터와 독립). `if settings is None:` 가드. `__all__` 포함.
- `app/ui/views/alerts.py`: `render()` 재작성. 모듈 상단 임포트. 첫 렌더 시 vault 로드 → session_state 초기화. 각 토글/multiselect에 `on_change` 콜백 → `save_alert_settings()` 즉시 호출. 데모/라이브 공통.
- `tests/unit/test_alerts_persist.py`: 신규 7 테스트. TDD — 구현 전 7 FAILED (`AttributeError`) 확인.
  - Unit: defaults, round-trip, connections-isolation, `__all__`
  - AppTest: 저장값 초기화, 토글 on_change, multiselect on_change
- 수정 전: 7 FAILED. 수정 후: 7 PASSED.
- 전체 unit 테스트: 509 → 516 passed (0 regressions).

## 리뷰

- 영속 레이어: vault-backed (`app/ui/vault.py`) — 기존 settings.py와 동일한 패턴, 신규 스토어 없음.
- 패치 전략: `patch.object(alerts_mod, "get_alert_settings")` — 모듈 상단 바인딩 정확히 인터셉트.
- 위젯 키: `alert_rules_widget` (leading underscore 없음, 기존 `alert_ch_{name}` 패턴 일치).
- None 가드: `if settings is None:` — 빈 `rules=[]` 저장 허용.
- 임포트: 모듈 상단 (PEP8, linter 가시).

실측 비용 (시간): ~0.5h (subagent)
실측 비용 (LLM 토큰): ~152k (subagent)

## Independent Audit

판정: 통과 — vault round-trip 확인 (save→load 값 일치), AppTest 토글/규칙 on_change 실행 검증. 전체 516 passed, 0 doc error. TDD(실패 테스트 선행). 기존 connections 데이터 보존 검증. spec reviewer PASS + code quality reviewer APPROVED.
