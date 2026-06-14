---
unit_id: UNIT-TASK-057-001
task_id: TASK-057
task_set_id: TASKSET-PRODUCT-MATURITY
project_id: PROJECT-AUTOFOLIO
status: completed
horizon: unit
model_tier: worker_standard
escalation_triggers: [high_risk, repeated_failure]
context: "backend.kpis()의 일손익률/누적손익률이 0.0 하드코딩 → 홈 KPI 카드 항상 0.00% 표시. repositories.py에 total_realized_pnl()/total_buy_cost_basis() 헬퍼 추가 후 kpis() 실계산."
inputs:
  - agents/lead_engineer/tasks/TASK-057-fix-kpi-returns-hardcoded-zero.md
  - app/ui/backend.py
  - app/database/repositories.py
  - tests/unit/test_backend_kpis.py
target_files:
  - app/database/repositories.py
  - app/ui/backend.py
  - tests/unit/test_backend_kpis.py
  - tests/unit/test_circuit_breaker.py
scope: "kpis() 함수 일손익률/누적손익률 실계산. 신규 repo 헬퍼 2개. 다른 화면/API 변경 금지."
acceptance:
  - "kpis() 일손익률 > 0 when today SELL realized profit exists"
  - "kpis() 누적손익률 > 0 when total realized + unrealized profit exists"
  - "empty holdings/fills → both return 0.0 (graceful)"
  - "python -m pytest tests/ -q green"
  - "python scripts/check_agent_docs.py 0 error"
verification:
  - "python -m pytest tests/unit/test_backend_kpis.py -v"
  - "python -m pytest tests/ -q"
  - "python scripts/check_agent_docs.py"
handoff: "변경 파일 목록, 계산 기준 요약, pytest 결과, check_agent_docs 결과 보고."
stop_condition: "kpis() 수정 완료 후 즉시 중단. 인접 뷰·다른 백엔드 함수 확장 금지."
depends_on: [TASK-063]
---

# UNIT-TASK-057-001 — KPI 일손익률/누적손익률 실계산

## Context

`backend.kpis()`의 `일손익률`/`누적손익률`이 `0.0` 하드코딩.
`execution_logs`·`order_logs` 기반 실계산 필요.

## Target Files

- `app/database/repositories.py` — `total_realized_pnl()`, `total_buy_cost_basis()` 추가
- `app/ui/backend.py` — `kpis()` 실계산 구현
- `tests/unit/test_backend_kpis.py` — 실패 테스트 선행, 통과 확인
- `tests/unit/test_circuit_breaker.py` — 신규 repo 헬퍼 단위테스트

## Calculation Basis

### daily_return
- 분자: `repo.today_realized_pnl()` (당일 SELL 실현 손익, TASK-063 수정 완료)
- 분모: `Σ(평단 × 수량)` of current holdings (보유 원가)
- 단순화: 전일 종가 평가액 없음 → 보유 원가를 분모로 대체. 코드 주석에 명시.

### total_return
- 분자: `repo.total_realized_pnl()` + `holdings_df 평가손익 합계`
- 분모: `repo.total_buy_cost_basis()` (전체 BUY 체결 원가 합계)
- 단순화: 매도 회수분 포함 분모 → TWR보다 보수적. 코드 주석에 명시.

## 완료 기록

완료 시각: 2026-06-14T11:13:13+09:00
검토자: Backend Engineer / QA
