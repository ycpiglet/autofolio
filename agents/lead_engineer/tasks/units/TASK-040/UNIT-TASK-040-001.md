---
unit_id: UNIT-TASK-040-001
task_id: TASK-040
task_set_id: TASKSET-RESEARCH-REPORTING
project_id: PROJECT-AUTOFOLIO
status: completed
horizon: unit
model_tier: worker_standard
escalation_triggers: [high_risk, repeated_failure]
context: "포트폴리오 성과/귀속/tax-lot 읽기전용 리포트. PortfolioReport dataclass + build_portfolio_report() pure function 추가 (app/services/perf_report.py). portfolio.py UI expander 연동. TDD: 실패 테스트 선행. 데이터 없는 항목은 '데이터 없음'/'not modeled' 명시. tax-lot은 참고용 placeholder + 면책 문구."
inputs:
  - agents/lead_engineer/tasks/TASK-040-portfolio-performance-tax-lot-reporting.md
  - app/ui/backend.py
  - app/ui/views/portfolio.py
  - app/ui/mock/data.py
  - tests/unit/test_backend_holdings.py
target_files:
  - app/services/perf_report.py
  - app/ui/views/portfolio.py
  - tests/unit/test_perf_report.py
scope: "app/services/perf_report.py 신규 생성 + app/ui/views/portfolio.py expander 추가 + tests/unit/test_perf_report.py. DB migration, broker order path (order_flow.py), app/risk/**, OrderFlow, KIS 주문 API 변경 없음. Read-only reporting only."
acceptance:
  - "PortfolioReport 필드: realized_pnl, unrealized_pnl, cashflow_note, fee_slippage_note, turnover_note, attribution_df, attribution_note, tax_lot_df, tax_lot_disclaimer, report_date"
  - "build_portfolio_report() 결정적 — 같은 입력 → 같은 출력"
  - "fee_slippage_note에 'not modeled' 또는 '미반영' 포함"
  - "tax_lot_disclaimer에 'illustrative' 또는 '참고용' 또는 '면책' 포함"
  - "attribution_df — '구분'/'기여(만원)' 컬럼, 자산군별 집계"
  - "tax_lot_df — 빈 holdings → empty DataFrame"
  - "python -m pytest tests/unit/test_perf_report.py -q: 17 passed"
  - "python -m pytest tests/ -q green"
  - "python scripts/check_agent_docs.py 0 error"
verification:
  - "python -m pytest tests/unit/test_perf_report.py -v"
  - "python -m pytest tests/unit -q"
  - "python -m pytest tests/ -q"
  - "python scripts/check_agent_docs.py"
  - "python scripts/generate_views.py --check"
  - "python scripts/build_task_index.py --check"
  - "python scripts/work_schema_gate.py --items --check"
handoff: "변경 파일 목록, pytest 결과(unit + full), gate 결과 보고. test_perf_report.py 실패→통과 증거 포함."
stop_condition: "app/services/perf_report.py + portfolio.py + test_perf_report.py 완료 후 중단. 주문 경로, risk policy, schema migration, KIS API endpoint 변경 금지."
depends_on: []
---

# UNIT-TASK-040-001 — 포트폴리오 성과·귀속·tax-lot 읽기전용 리포트

## Context

TASK-040: 읽기전용 성과 리포트 구현.
`app/services/perf_report.py`에 `PortfolioReport` dataclass + `build_portfolio_report()` 추가.
`app/ui/views/portfolio.py` "성과 리포트" expander 섹션 추가.
데이터 없는 항목(현금흐름·수수료·턴오버)은 '데이터 없음'/'not modeled' 명시.
tax-lot은 참고용 placeholder + 면책 문구 (세무 조언 아님).

## Target Files

- `app/services/perf_report.py` — 신규 (PortfolioReport + build_portfolio_report)
- `app/ui/views/portfolio.py` — expander 추가
- `tests/unit/test_perf_report.py` — 신규 (17 테스트)

## Scope

In scope: 위 3개 파일. 읽기전용.

Out of scope: DB migration, `app/engine/order_flow.py`, `app/risk/**`, KIS order API, `OrderFlow`,
실제 세금 계산, 주문·리밸런싱 실행.

## Steps

1. `tests/unit/test_perf_report.py` 작성 (17개 테스트, 모두 FAIL 확인).
2. `app/services/perf_report.py` 구현 → 테스트 GREEN.
3. `app/ui/views/portfolio.py` expander 추가.
4. 전체 pytest green + gate scripts OK.

## Acceptance Criteria

- `PortfolioReport` 10개 필드 존재
- `build_portfolio_report()` 결정적
- `fee_slippage_note` → 'not modeled'/'미반영' 포함
- `tax_lot_disclaimer` → 'illustrative'/'참고용'/'면책' 포함
- `attribution_df` → '구분'/'기여(만원)' 컬럼
- `pytest tests/unit/test_perf_report.py -q` 17 passed
- `pytest tests/ -q` green
- `check_agent_docs.py` 0 error

## Verification

```
python -m pytest tests/unit/test_perf_report.py -v
python -m pytest tests/unit -q
python -m pytest tests/ -q
python scripts/check_agent_docs.py
python scripts/generate_views.py --check
python scripts/build_task_index.py --check
python scripts/work_schema_gate.py --items --check
```

## Handoff

변경 파일 목록, pytest 결과(unit + full), gate 결과 보고.

## Stop Boundary

3개 파일 완료 후 즉시 중단. 주문 경로, risk policy, schema migration 변경 금지.

## 완료 기록

완료 시각: 2026-06-14T19:07:22+09:00
검토자: Performance Analyst / QA

**변경 내용:**
- `app/services/perf_report.py`: `PortfolioReport` dataclass, `__all__`, 면책 상수 4개, `build_portfolio_report()` 순수 함수.
- `app/ui/views/portfolio.py`: `_render_perf_report()` 헬퍼 + render() 하단 expander 추가.
- `tests/unit/test_perf_report.py`: 17개 테스트 (TDD — 실패 선행 후 통과).

**검증 결과:**
- 수정 전: 17개 FAILED (ModuleNotFoundError: app.services.perf_report)
- 수정 후: 17 passed (test_perf_report.py), 756 passed (전체)
- `check_agent_docs.py` → verified below
- `generate_views.py --check` → verified below
- `build_task_index.py --check` → verified below
