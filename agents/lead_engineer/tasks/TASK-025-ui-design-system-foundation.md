---
type: task
id: TASK-025
status: 완료
owner: Lead Engineer
assignees: [Lead Engineer, UI/UX Designer]
priority: High
difficulty: 중
est_hours: 3
est_tokens: 35000
tags: [ui, design-system, streamlit, safety]
trigger_meeting: 자가발생
audit_log: AUDIT-2026-06-11-006
created: 2026-06-11
created_at: 2026-06-11T12:50:32+09:00
---

# TASK-025 UI Design System Foundation

작업 ID: TASK-025
상태: 완료
Owner: Lead Engineer
요청 시각: 2026-06-11T12:50:32+09:00
기록 시각: 2026-06-11T12:50:32+09:00

## 배경 및 목적

`docs/design` 재첨부 자료와 외부 리서치를 바탕으로 Autofolio의 UI 방향을
`Autofolio Control Desk`로 고정한다. 구현 전 디자인 원칙, 토큰, 컴포넌트 매트릭스를
문서와 테스트 가능한 theme helper로 남긴다.

## 구현 범위

- `docs/design/autofolio/DESIGN.md` 작성
- `docs/design/autofolio/COMPONENT-MATRIX.md` 작성
- `app/ui/theme.py`에 semantic token과 `env_label()` 추가
- `tests/unit/test_ui_theme_tokens.py` 추가

## 완료 기준

- [x] 디자인 방향 문서가 `docs/design/autofolio/`에 존재
- [x] 환경 label이 mock/paper/prod/unknown을 명확히 구분
- [x] 한국식 손익 색상 규칙 유지
- [x] `pytest tests/unit/test_ui_theme_tokens.py -v` 통과

## 진행 기록

- 2026-06-11T14:28:33+09:00: Task 진행 중으로 전환
- 2026-06-11T14:29:00+09:00: `docs/design/autofolio/DESIGN.md`, `COMPONENT-MATRIX.md`, `app/ui/theme.py`, `tests/unit/test_ui_theme_tokens.py` 추가/수정
- 2026-06-11T14:30:55+09:00: `pytest tests/unit/test_ui_theme_tokens.py -v` 통과, `app/ui/views/trade.py`에서 `theme.env_label()` 연계

## 완료 기록

- 작업 산출물:
  - `docs/design/autofolio/DESIGN.md`
  - `docs/design/autofolio/COMPONENT-MATRIX.md`
  - `app/ui/theme.py`
  - `app/ui/views/trade.py`
  - `tests/unit/test_ui_theme_tokens.py`
- 검증: `pytest tests/unit/test_ui_theme_tokens.py -v`

## 계획 링크

- `docs/superpowers/plans/2026-06-11-autofolio-ui-control-desk.md` Task 1

## 리스크 및 경계

- 디자인 토큰만 추가한다. 주문/브로커/리스크 정책 코드는 변경하지 않는다.
