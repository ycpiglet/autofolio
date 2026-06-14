---
type: task
id: TASK-054
status: 대기
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
updated_at: 2026-06-14T00:00:00+09:00
---

# TASK-054 fix: 알림 채널 토글/규칙 설정 미저장 (alerts.py)

작업 ID: TASK-054
상태: 대기
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
유닛 스펙은 실행 시점에 생성된다 (현재 없음).

- Initiative: `agents/project/initiatives/INIT-PRODUCT-MATURITY.md`
- Taskset: `agents/project/initiatives/TASKSET-PRODUCT-MATURITY.md`
