---
schema_version: agent-runtime-work-item/v1
work_id: INIT-RESEARCH-REPORTING
work_uid: ea5e56a4-5f92-482b-b115-596524ae2fb5
kind: initiative
status: planned
owner: Lead Engineer
created_at: 2026-06-14T09:03:29+09:00
updated_at: 2026-06-14T09:03:29+09:00
origin_type: owner_request
origin_ref: AUDIT-2026-06-13-004
created_by: lead_engineer
title: Research and Reporting — Watchlist, Backtest, Portfolio, Broker Parity
summary: 투자 리서치·보고 기능 4건 — 워치리스트/스크리너/알림 확장, 백테스트 보고서 강화, 포트폴리오 성과·세금 보고, 브로커 기능 패리티 매트릭스.
tags: [research, reporting, watchlist, backtest, portfolio, broker-parity]
priority: P2
---

# INIT-RESEARCH-REPORTING — 리서치 및 보고 이니셔티브

## 목적

Autofolio의 투자 리서치·보고 기능을 강화한다. 워치리스트/스크리너/알림 확장,
백테스트 보고서 재현성 강화, 포트폴리오 성과·세금 보고, 브로커 기능 패리티 매트릭스
4건을 구현한다.

## 포함 작업

| ID | 설명 | 우선순위 |
|----|------|----------|
| TASK-038 | Watchlist/screener/alert rule 확장 | High |
| TASK-039 | Backtest 리서치 보고서 강화 | Medium |
| TASK-040 | Portfolio 성과 및 세금 구좌 방식 보고 | Medium |
| TASK-041 | 브로커 기능 패리티 매트릭스 | Medium |

## 실행 특성

4개 태스크는 서로 독립적이며 병렬 실행 가능하다. 주문 경로·브로커 API·DB 마이그레이션을
건드리지 않는 read-only/report-only 범위다.

## 완료 기준

- 워치리스트/스크리너 UI 생성/수정/삭제 가능
- 백테스트 보고서가 입력/가정/결과/한계를 포함한 재현 가능 형식으로 출력됨
- 포트폴리오 성과·세금 보고 UI 완성
- 브로커 기능 패리티 매트릭스 문서 완성
- `python scripts/check_agent_docs.py` 0 error
