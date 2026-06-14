---
schema_version: agent-runtime-work-item/v1
work_id: TASKSET-RESEARCH-REPORTING
work_uid: 2032481f-6a74-4d14-bf47-c1f5d2bb5c92
kind: taskset
parent_id: INIT-RESEARCH-REPORTING
status: planned
owner: Lead Engineer
created_at: 2026-06-14T09:03:29+09:00
updated_at: 2026-06-14T09:03:29+09:00
origin_type: owner_request
origin_ref: AUDIT-2026-06-13-004
created_by: lead_engineer
title: 리서치·보고 태스크셋 (TASK-038~041)
summary: 워치리스트/백테스트/포트폴리오/브로커패리티 4건 — 독립적이며 병렬 실행 가능
tags: [research, reporting, watchlist, backtest, portfolio, broker-parity]
priority: P2
---

# TASKSET-RESEARCH-REPORTING — 리서치 및 보고 4건

## 부모 이니셔티브

`INIT-RESEARCH-REPORTING`

## 포함 태스크

tasks:
  - TASK-038
  - TASK-039
  - TASK-040
  - TASK-041

| work_id | 설명 | Owner |
|---------|------|-------|
| TASK-038 | Watchlist/screener/alert rule 확장 | UI/UX Designer |
| TASK-039 | Backtest 리서치 보고서 강화 | Quant Researcher |
| TASK-040 | Portfolio 성과 및 세금 구좌 방식 보고 | Performance Analyst |
| TASK-041 | 브로커 기능 패리티 매트릭스 | Lead Engineer |

## 의존 관계

4건은 서로 독립적이며 동시 실행 가능하다 (`depends_on: []`).

주문 경로·브로커 API·DB 마이그레이션을 건드리지 않는 read-only/report-only 범위.

## Wave 실행 계획

Wave 1: TASK-038, TASK-039, TASK-040, TASK-041 (병렬)
