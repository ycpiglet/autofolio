---
type: task
id: TASK-026
status: 완료
owner: UI/UX Designer
assignees: [UI/UX Designer]
priority: High
difficulty: 중
est_hours: 3
est_tokens: 35000
tags: [ui, components, safety, streamlit]
trigger_meeting: 자가발생
audit_log: AUDIT-2026-06-11-006
created: 2026-06-11
created_at: 2026-06-11T12:50:32+09:00
---

# TASK-026 UI Safety Rail Components

작업 ID: TASK-026
상태: 완료
Owner: UI/UX Designer
요청 시각: 2026-06-11T12:50:32+09:00
기록 시각: 2026-06-11T12:50:32+09:00

## 배경 및 목적

현재 상단바는 모드, auto, kill 상태를 보여주지만 환경/출처/서킷브레이커를 하나의
운영 안전 표면으로 구성하지 못한다. 공용 Safety Rail과 색상 의존 없는 badge helper를
만든다.

## 구현 범위

- `app/ui/components/ui.py`에 `status_tone`, `status_badge`, `build_safety_summary` 추가
- 기존 `badge()`를 새 helper로 연결
- `top_bar()`를 Safety Rail 성격으로 정리
- `tests/unit/test_ui_components_contract.py` 추가

## 완료 기준

- [x] status badge가 텍스트와 marker를 포함해 색상 의존만으로 동작하지 않음
- [x] Safety Rail이 환경, mode, auto, kill, circuit breaker 상태를 명시
- [x] `pytest tests/unit/test_ui_components_contract.py tests/unit/test_ui_theme_tokens.py -v` 통과

## 계획 링크

- `docs/superpowers/plans/2026-06-11-autofolio-ui-control-desk.md` Task 2

## 리스크 및 경계

- UI 표시 계약만 다룬다. system_state 저장 방식이나 trading guard 정책은 변경하지 않는다.

## 완료 기록

### 2026-06-11T14:39:46+09:00

- `app/ui/components/ui.py`에 `status_tone`, `status_badge`, `build_safety_summary`를 추가.
- `badge()`를 `status_badge()`로 연결해 색상과 함께 텍스트 마커를 항상 표시.
- `top_bar()`를 Safety Rail 형태로 정리하여 환경/모드/자동매매/킬스위치/서킷브레이커를 텍스트로 명시.
- `tests/unit/test_ui_components_contract.py`를 추가해 위 계약을 회귀 테스트로 고정.
- `pytest tests/unit/test_ui_components_contract.py tests/unit/test_ui_theme_tokens.py -v` 통과.
