---
type: task
id: TASK-027
status: 완료
owner: UI/UX Designer
assignees: [UI/UX Designer, QA]
priority: Medium
difficulty: 중
est_hours: 3
est_tokens: 35000
tags: [ui, dashboard, portfolio, streamlit]
trigger_meeting: 자가발생
audit_log: AUDIT-2026-06-11-006
created: 2026-06-11
created_at: 2026-06-11T12:50:32+09:00
---

# TASK-027 UI Dashboard and Portfolio Refresh

작업 ID: TASK-027
상태: 완료
Owner: UI/UX Designer
요청 시각: 2026-06-11T12:50:32+09:00
기록 시각: 2026-06-11T12:50:32+09:00

## 배경 및 목적

Home과 Portfolio를 marketing형 화면이 아니라 운영자가 장중에 스캔하는 control desk로
재배치한다. Home은 action보다 상태와 리스크 요약을 먼저 보여주고, Portfolio는 보유/비중/
손익 표를 중심에 둔다.

## 구현 범위

- `app/ui/views/home.py` layout refresh
- `app/ui/views/portfolio.py` holdings-first refresh
- 필요 시 pure display helper만 `app/ui/backend.py`에 추가
- 기존 KPI/holdings 테스트 유지

## 완료 기준

- [x] Home이 safety/market state → KPI → chart/table → alerts 순서로 표시
- [x] Portfolio가 holdings table과 allocation/risk summary를 우선 표시
- [x] 빈 상태와 demo mode가 정상 동작
- [x] `pytest tests/unit/test_backend_kpis.py tests/unit/test_backend_holdings.py -v` 통과

## 계획 링크

- `docs/superpowers/plans/2026-06-11-autofolio-ui-control-desk.md` Task 3

## 리스크 및 경계

- 백엔드 데이터 계산을 바꾸지 않는다. 화면 배치와 표시 계약 중심으로 제한한다.

## 완료 기록

### 2026-06-11T18:23:32+09:00

- Home을 운영 상태 → 시장 상태 → 계좌 KPI → 자산 곡선/보유 요약 → 검토 대기 제안/최근 체결 → 알림 순서로 재배치.
- Home의 승인/거부 버튼을 제거해 주문 관련 action은 Trade 화면으로 한정.
- Portfolio를 holdings-first 구조로 재배치하고 평가금액/손익/보유수/현금비중, 자산배분, 목표 대비, 리스크 메모를 뒤따르게 구성.
- `ACTIVE`/`CLEAR`/`TRIGGERED` guard 상태가 색상만이 아니라 marker text와 함께 올바른 tone으로 표시되도록 component contract 테스트를 추가.
- 검증:
  - `pytest tests/unit/test_backend_kpis.py tests/unit/test_backend_holdings.py -v` → 17 passed
  - `pytest tests/unit/test_backend_kpis.py tests/unit/test_backend_holdings.py tests/unit/test_ui_components_contract.py tests/unit/test_ui_theme_tokens.py -v` → 29 passed
  - `python -m py_compile app\ui\views\home.py app\ui\views\portfolio.py app\ui\components\ui.py` → 통과
