---
unit_id: UNIT-TASK-039-001
task_id: TASK-039
task_set_id: TASKSET-RESEARCH-REPORTING
project_id: PROJECT-AUTOFOLIO
status: completed
horizon: unit
model_tier: worker_standard
escalation_triggers: [high_risk, repeated_failure]
context: "백테스트 결과를 재현 가능한 연구 리포트로 강화. BacktestReport dataclass + build_report() 추가. 파라미터 테이블·벤치마크 비교·최대낙폭·거래내역·턴오버·수수료/슬리피지 가정·정기이벤트 주의·페이퍼/실거래 차이 명시. UI(analysis.py) expander에 표시."
inputs:
  - agents/lead_engineer/tasks/TASK-039-backtest-research-report-hardening.md
  - app/quant/backtest.py
  - app/ui/views/analysis.py
  - tests/unit/test_backtest.py
target_files:
  - app/quant/backtest.py
  - app/ui/views/analysis.py
  - tests/unit/test_backtest.py
scope: "app/quant/backtest.py에 BacktestReport + build_report() 추가. analysis.py _backtest_section 표시 확장. DB migration, live scheduler, broker order path, risk policy 변경 없음."
acceptance:
  - "BacktestReport 필드: parameters, benchmark_return_pct, max_drawdown_pct, trades, turnover_pct, fee_slippage_assumption, scheduled_event_caveat, paper_live_parity_note"
  - "build_report() 결정적 — 같은 입력 → 같은 출력"
  - "fee_slippage_assumption에 'not modeled' 또는 '미반영' 포함"
  - "turnover_pct == 0.0 when no trades"
  - "python -m pytest tests/unit/test_backtest.py -q 8 passed"
  - "python -m pytest tests/ -q green"
  - "python scripts/check_agent_docs.py 0 error"
verification:
  - "python -m pytest tests/unit/test_backtest.py -q"
  - "python -m pytest tests/ -q"
  - "python -m pytest tests/unit -q"
  - "python scripts/check_agent_docs.py"
  - "python scripts/generate_views.py --check"
  - "python scripts/build_task_index.py --check"
handoff: "변경 파일 목록, pytest 결과(unit + full), gate 결과 보고."
stop_condition: "app/quant/backtest.py + analysis.py + tests/unit/test_backtest.py 수정 후 즉시 중단. broker, scheduler, risk 경로 변경 금지."
depends_on: []
---

# UNIT-TASK-039-001 — Backtest Research Report Hardening

## Context

TASK-039: `BacktestResult`(기존)를 확장하는 `BacktestReport` dataclass + `build_report()`
함수를 `app/quant/backtest.py`에 추가. 파라미터 테이블, 벤치마크 비교, 턴오버,
수수료/슬리피지 가정(미반영 명시), 정기 이벤트 주의, 페이퍼/실거래 차이 안내를 포함.
UI(`app/ui/views/analysis.py` `_backtest_section`)에 expander로 표시.

## Target Files

- `app/quant/backtest.py` — `BacktestReport` dataclass + `build_report()` 추가
- `app/ui/views/analysis.py` — `_backtest_section` 확장
- `tests/unit/test_backtest.py` — 5개 신규 테스트 추가

## Scope

In scope: `app/quant/backtest.py` 확장, `analysis.py` 표시 확장, 테스트.

Out of scope: DB migration, live scheduler, broker order path (`order_flow.py`), risk policy,
`BacktestResult` 기존 필드 변경 금지.

## Acceptance Criteria

- `BacktestReport` 8개 필수 필드 (parameters, benchmark_return_pct, max_drawdown_pct, trades, turnover_pct, fee_slippage_assumption, scheduled_event_caveat, paper_live_parity_note) 모두 존재
- `build_report()` 결정적 (같은 입력 → 동일 출력)
- `fee_slippage_assumption` "not modeled" / "미반영" 포함
- turnover 0-trade → 0.0
- `pytest tests/unit/test_backtest.py -q` 8 passed
- `pytest tests/ -q` green
- `check_agent_docs.py` 0 error

## 완료 기록

완료 시각: 2026-06-14T18:17:18+09:00
검토자: Lead Engineer

**변경 내용:**
- `app/quant/backtest.py`: `BacktestReport` dataclass, `_FEE_SLIPPAGE_TEXT`, `_SCHEDULED_EVENT_CAVEAT`, `_PAPER_LIVE_PARITY_NOTE` 상수, `build_report()` 함수 추가.
- `app/ui/views/analysis.py`: `_backtest_section` — `build_report()` 호출 후 session state에 `BacktestReport` 저장. expander로 파라미터 테이블·벤치마크·에쿼티 커브·거래내역·가정 표시.
- `tests/unit/test_backtest.py`: `test_build_report_has_required_fields`, `test_build_report_is_deterministic`, `test_benchmark_return_is_buy_and_hold`, `test_fee_slippage_assumption_says_not_modeled`, `test_turnover_zero_when_no_trades` 추가.

**검증 결과:**
- 수정 전: 5개 신규 테스트 FAILED (ImportError: build_report)
- 수정 후: 8 passed (test_backtest.py), 739 passed (전체), 560 passed (unit)
- `check_agent_docs.py` → 0 error
- `generate_views.py --check` → OK
- `build_task_index.py --check` → OK
