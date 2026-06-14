---
type: task
id: TASK-039
status: 완료
owner: Quant Researcher
assignees: [Quant Researcher, QA, UI/UX Designer]
priority: Medium
difficulty: 중
est_hours: 4
est_tokens: 45000
tags: [feature-landscape, backtest, research, reports, qa]
gate: backtest/report/mock-only; no live scheduler, broker order path, risk policy, schema migration, or prod mutation
trigger_meeting: Owner direct request
audit_log: AUDIT-2026-06-13-004
created: 2026-06-13
created_at: 2026-06-13T00:53:23+09:00
updated_at: 2026-06-14T18:23:09+09:00
---

# TASK-039 Backtest Research Report Hardening

작업 ID: TASK-039
상태: 완료
Owner: Quant Researcher
요청 시각: 2026-06-12
기록 시각: 2026-06-13T00:53:23+09:00

## 배경 및 목적

퀀트 플랫폼은 backtest 결과를 단순 수익률이 아니라 benchmark, drawdown, trades,
parameters, fills/fees/slippage assumptions, scheduled-event caveat, paper/live parity note로
기록한다. Autofolio의 분석/백테스트 화면도 실전 전환 전에 재현 가능한 연구 기록이 필요하다.

## 범위

- 포함:
  - backtest run summary schema 또는 markdown/JSON output.
  - parameter table, benchmark comparison, drawdown, trade list, turnover, fee/slippage assumptions.
  - scheduled-event timing caveat와 paper/live parity note.
  - UI 표시 또는 downloadable report.
  - deterministic fixture tests.
- 제외:
  - live scheduler 실행.
  - 실제 주문 실행.
  - KIS broker/order path 변경.
  - DB migration.

## Done When

1. backtest report가 입력/가정/결과/한계/재현 정보를 한 파일 또는 UI section으로 보여준다.
2. benchmark, drawdown, trades, fees/slippage assumptions가 빠지면 테스트가 실패한다.
3. scheduled-event와 paper/live 차이를 명시한다.
4. focused regression과 docs record가 통과한다.

## v1 이행

이 태스크는 agent_runtime v0.2.0 work-item 스키마(`agent-runtime-work-item/v1`) 계층에 포함된다.
유닛 스펙은 실행 시점에 생성된다 (현재 없음).

- Initiative: `agents/project/initiatives/INIT-RESEARCH-REPORTING.md`
- Taskset: `agents/project/initiatives/TASKSET-RESEARCH-REPORTING.md`

## 완료 기록

완료 시각: 2026-06-14T18:23:09+09:00
검토자: Lead Engineer

## 증거

- `app/quant/backtest.py` — `BacktestReport` + `build_report()` 추가 (BacktestResult 변경 없음)
- `app/ui/views/analysis.py` — `_backtest_section` expander 확장 (파라미터 테이블·벤치마크·거래내역·가정)
- `tests/unit/test_backtest.py` — 5개 신규 테스트 추가 (8 passed)
- `agents/lead_engineer/tasks/units/TASK-039/UNIT-TASK-039-001.md` — 완료 기록
- `python -m pytest tests/ -q` → 739 passed, 0 failed
- `python -m pytest tests/unit -q` → 560 passed, 0 failed
- `python scripts/check_agent_docs.py` → 0 error
- `python scripts/generate_views.py --check` → OK
- `python scripts/build_task_index.py --check` → OK

## 리뷰

- 기존 `BacktestResult` 변경 없음 — 하위 호환
- `build_report()` 결정적 (고정 캐시 데이터 → 고정 출력, 랜덤 없음)
- 수수료/슬리피지 정직하게 "미반영" 명시 (fabrication 없음)
- 정기 이벤트 주의 및 페이퍼/실거래 차이 안내 포함
- UI는 read-only 분석 전용 — live 주문 경로 미변경
