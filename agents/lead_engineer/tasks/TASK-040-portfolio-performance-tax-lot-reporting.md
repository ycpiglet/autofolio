---
type: task
id: TASK-040
status: 대기
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
updated_at: 2026-06-13T00:53:23+09:00
---

# TASK-040 Portfolio Performance and Tax-Lot Style Reporting

작업 ID: TASK-040
상태: 대기
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
