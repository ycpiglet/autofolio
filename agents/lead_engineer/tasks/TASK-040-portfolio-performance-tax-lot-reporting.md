---
type: task
id: TASK-040
status: 완료
owner: Performance Analyst
assignees: [Performance Analyst, UI/UX Designer, QA]
priority: Medium
difficulty: 중
est_hours: 4
est_tokens: 45000
tags: [feature-landscape, portfolio, performance, reporting, read-only]
gate: read-only reporting only; no tax advice, order submission, broker order path, risk policy, schema migration, or prod mutation
trigger_meeting: Owner direct request
audit_log: AUDIT-2026-06-13-004
created: 2026-06-13
created_at: 2026-06-13T00:53:23+09:00
updated_at: 2026-06-14T19:07:22+09:00
---

# TASK-040 Portfolio Performance and Tax-Lot Style Reporting

작업 ID: TASK-040
상태: 완료
Owner: Performance Analyst
요청 시각: 2026-06-12
기록 시각: 2026-06-13T00:53:23+09:00

## 배경 및 목적

Autofolio는 paper holdings UI와 mock portfolio reality model을 갖췄지만, 실제 플랫폼처럼
기간별 성과, realized/unrealized P&L, fees/slippage, cashflow, attribution, tax-lot style
view를 읽기전용으로 제공하면 보유 상태와 성과 원인을 더 명확히 볼 수 있다.

## 범위

- 포함:
  - realized/unrealized P&L read-only summary.
  - cashflow, fee/slippage, turnover, sector/strategy/time attribution.
  - tax-lot style placeholder: 매수 lot 단위 표시와 면책 문구.
  - UI table/chart and export-friendly report.
  - mock/paper fixture tests.
- 제외:
  - 세무 조언 또는 실제 세금 계산 확정.
  - 주문/리밸런싱 실행.
  - KIS order endpoint, `OrderFlow`, `app/risk/**` 변경.
  - DB migration.

## Done When

1. 포트폴리오 화면 또는 보고서가 기간별 성과와 attribution을 읽기전용으로 보여준다.
2. realized/unrealized P&L과 fee/slippage/cashflow 가정이 명시된다.
3. tax-lot style 표시는 placeholder/면책으로 한정된다.
4. focused UI/backend tests가 통과한다.

## v1 이행

이 태스크는 agent_runtime v0.2.0 work-item 스키마(`agent-runtime-work-item/v1`) 계층에 포함된다.
유닛 스펙은 실행 시점에 생성된다 (현재 없음).

- Initiative: `agents/project/initiatives/INIT-RESEARCH-REPORTING.md`
- Taskset: `agents/project/initiatives/TASKSET-RESEARCH-REPORTING.md`

## 완료 기록

완료 시각: 2026-06-14T19:07:22+09:00
검토자: Performance Analyst / QA

## 증거

- `app/services/perf_report.py`: `PortfolioReport` dataclass + `build_portfolio_report()` 순수 함수 추가.
  - 실현/미실현 손익, 현금흐름·수수료·턴오버 면책, attribution by 자산군, tax-lot placeholder.
  - 면책 상수: `_CASHFLOW_NOTE`, `_FEE_SLIPPAGE_NOTE`, `_TURNOVER_NOTE`, `_TAX_LOT_DISCLAIMER`.
  - `__all__ = ["PortfolioReport", "build_portfolio_report"]`.
- `app/ui/views/portfolio.py`: `_render_perf_report()` + render() 하단 "📊 성과 리포트" expander 추가.
  - 라이브/mock 데이터 분기, 폴백 처리.
- `tests/unit/test_perf_report.py`: 17개 테스트 (TDD — 실패 선행 후 통과).
- 수정 전: 17개 FAILED (ModuleNotFoundError: app.services.perf_report)
- 수정 후: 17 passed (test_perf_report.py), 756 passed (전체)

## 리뷰

- 데이터 없는 항목(현금흐름·수수료·턴오버)은 '데이터 없음'/'not modeled' 명시 — 데이터 날조 없음.
- tax-lot은 execution_logs BUY 기록 기반 참고용 — 세무 조언 아님 (면책 표시).
- Attribution은 자산군별 미실현 평가손익 집계 — 시간/전략 축은 스냅샷 없어 불가 (명시).
- 주문 경로 (`order_flow.py`), risk policy, schema migration 변경 없음.
- TZ: report_date는 pnl_series 마지막 날짜 또는 고정 문자열 (datetime.now() 미사용).
- `__all__` 추가로 app/services/ 패키지 패턴 일관성 유지.

실측 비용 (시간): ~1h (subagent-driven-development)
실측 비용 (LLM 토큰): ~200k (estimated)
